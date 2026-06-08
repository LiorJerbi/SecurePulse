import os
import tempfile
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models
from app.parser import parse_log_file
from app import crud
from app.schemas import IngestResponse, PaginatedLogs

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SecurePulse",
    description="AI-Powered Log Analysis & Threat Detection",
    version="0.2.0"
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