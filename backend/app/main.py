import os
import tempfile
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models
from app.parser import parse_log_file
from app import crud
from app.detector import run_all_detectors
from app.schemas import IngestResponse, PaginatedLogs, AlertResponse, AnalysisResult
from app.models import LogEntry, Alert
from sqlalchemy import select
from datetime import datetime
from app.gemini_service import explain_alert
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SecurePulse",
    description="AI-Powered Log Analysis & Threat Detection",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "SecurePulse API",
        "version": "0.2.0"
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_log_file(
    log_type: str = Query(..., enum=["apache", "auth"]),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".log"):
        raise HTTPException(status_code=400, detail="Only .log files are accepted")

    contents = await file.read()

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".log", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        parsed_entries = parse_log_file(tmp_path, log_type)
        if not parsed_entries:
            raise HTTPException(status_code=422, detail="No valid log lines could be parsed")
        stored = crud.store_log_entries(db, parsed_entries)
    finally:
        os.unlink(tmp_path)

    return IngestResponse(
        message="Log file ingested successfully",
        log_type=log_type,
        lines_parsed=len(parsed_entries),
        lines_stored=stored
    )


@app.get("/logs", response_model=PaginatedLogs)
def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    source_ip: str = Query(None),
    log_type: str = Query(None, enum=["apache", "auth"]),
    status_code: int = Query(None),
    db: Session = Depends(get_db)
):
    total, results = crud.get_log_entries(
        db, page, page_size, source_ip, log_type, status_code
    )
    return PaginatedLogs(
        total=total,
        page=page,
        page_size=page_size,
        results=results
    )

@app.post("/analyze", response_model=AnalysisResult)
def analyze_logs(db: Session = Depends(get_db)):
    results = run_all_detectors(db)
    return results


@app.get("/alerts", response_model=list[AlertResponse])
def get_alerts(
    severity: str = Query(None, enum=["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
    alert_type: str = Query(None),
    from_date: datetime = Query(None),
    to_date: datetime = Query(None),
    db: Session = Depends(get_db)
):
    query = select(Alert).order_by(Alert.created_at.desc())

    if severity:
        query = query.where(Alert.severity == severity)
    if alert_type:
        query = query.where(Alert.alert_type == alert_type)
    if from_date:
        query = query.where(Alert.created_at >= from_date)
    if to_date:
        query = query.where(Alert.created_at <= to_date)

    results = db.execute(query).scalars().all()
    return results


@app.post("/alerts/{alert_id}/explain", response_model=AlertResponse)
def explain_alert_endpoint(
    alert_id: int,
    db: Session = Depends(get_db)
):
    alert = db.execute(
        select(Alert).where(Alert.id == alert_id)
    ).scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    if alert.ai_explanation:
        return alert

    alert.ai_explanation = explain_alert(alert)
    db.commit()
    db.refresh(alert)
    return alert


@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    from sqlalchemy import func

    total_logs = db.execute(select(func.count()).select_from(LogEntry)).scalar()
    total_alerts = db.execute(select(func.count()).select_from(Alert)).scalar()

    alerts_by_type = db.execute(
        select(Alert.alert_type, func.count(Alert.id))
        .group_by(Alert.alert_type)
    ).all()

    alerts_by_severity = db.execute(
        select(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity)
    ).all()

    detection_rate = round(total_alerts / total_logs * 100, 2) if total_logs > 0 else 0

    return {
        "total_logs": total_logs,
        "total_alerts": total_alerts,
        "detection_rate_percent": detection_rate,
        "alerts_by_type": {row[0]: row[1] for row in alerts_by_type},
        "alerts_by_severity": {row[0]: row[1] for row in alerts_by_severity},
    }