from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models import LogEntry, Alert
import os


WHITELISTED_SUDO_USERS = set(os.getenv("WHITELISTED_SUDO_USERS", "").split(","))

def _create_alert(
    db: Session,
    alert_type: str,
    severity: str,
    source_ip: str,
    description: str
) -> Alert:
    alert = Alert(
        created_at=datetime.now(timezone.utc),
        alert_type=alert_type,
        severity=severity,
        source_ip=source_ip,
        description=description,
        ai_explanation=None
    )
    db.add(alert)
    return alert


def detect_brute_force_ssh(db: Session) -> list[Alert]:
    alerts = []
    window = timedelta(seconds=60)

    failed_entries = db.execute(
        select(LogEntry)
        .where(LogEntry.log_type == "auth")
        .where(LogEntry.event.like("%Failed password%"))
        .order_by(LogEntry.source_ip, LogEntry.timestamp)
    ).scalars().all()

    by_ip: dict[str, list[datetime]] = {}
    for entry in failed_entries:
        by_ip.setdefault(entry.source_ip, []).append(entry.timestamp)

    for ip, timestamps in by_ip.items():
        for i, ts in enumerate(timestamps):
            window_hits = [t for t in timestamps[i:] if t - ts <= window]
            if len(window_hits) >= 5:
                alerts.append(_create_alert(
                    db=db,
                    alert_type="BRUTE_FORCE_SSH",
                    severity="HIGH",
                    source_ip=ip,
                    description=f"{len(window_hits)} failed SSH attempts from {ip} within 60 seconds"
                ))
                break

    return alerts


def detect_http_scanner(db: Session) -> list[Alert]:
    alerts = []
    window = timedelta(seconds=30)

    not_found_entries = db.execute(
        select(LogEntry)
        .where(LogEntry.log_type == "apache")
        .where(LogEntry.status_code == 404)
        .order_by(LogEntry.source_ip, LogEntry.timestamp)
    ).scalars().all()

    by_ip: dict[str, list[datetime]] = {}
    for entry in not_found_entries:
        by_ip.setdefault(entry.source_ip, []).append(entry.timestamp)

    for ip, timestamps in by_ip.items():
        for i, ts in enumerate(timestamps):
            window_hits = [t for t in timestamps[i:] if t - ts <= window]
            if len(window_hits) >= 10:
                alerts.append(_create_alert(
                    db=db,
                    alert_type="HTTP_SCANNER",
                    severity="MEDIUM",
                    source_ip=ip,
                    description=f"{len(window_hits)} HTTP 404 responses to {ip} within 30 seconds"
                ))
                break

    return alerts


def detect_privilege_escalation(db: Session) -> list[Alert]:
    alerts = []

    sudo_entries = db.execute(
        select(LogEntry)
        .where(LogEntry.log_type == "auth")
        .where(LogEntry.event.like("%sudo%"))
    ).scalars().all()

    for entry in sudo_entries:
        event_lower = entry.event.lower()
        user = None
        if ":" in entry.event:
            user = entry.event.split(":")[0].strip()

        if user and user not in WHITELISTED_SUDO_USERS:
            alerts.append(_create_alert(
                db=db,
                alert_type="PRIVILEGE_ESCALATION",
                severity="CRITICAL",
                source_ip=entry.source_ip,
                description=f"Non-whitelisted user '{user}' executed sudo command: {entry.event[:100]}"
            ))

    return alerts


def detect_off_hours_access(db: Session) -> list[Alert]:
    alerts = []

    successful_logins = db.execute(
        select(LogEntry)
        .where(LogEntry.log_type == "auth")
        .where(LogEntry.event.like("%Accepted password%"))
    ).scalars().all()

    for entry in successful_logins:
        hour = entry.timestamp.hour
        if 0 <= hour < 5:
            alerts.append(_create_alert(
                db=db,
                alert_type="OFF_HOURS_ACCESS",
                severity="MEDIUM",
                source_ip=entry.source_ip,
                description=f"Successful login from {entry.source_ip} at {entry.timestamp.strftime('%H:%M:%S')} (off-hours window: 00:00-05:00)"
            ))

    return alerts


def run_all_detectors(db: Session) -> dict:
    existing = db.execute(select(func.count()).select_from(Alert)).scalar()
    if existing > 0:
        db.execute(Alert.__table__.delete())
        db.commit()

    all_alerts = []
    all_alerts.extend(detect_brute_force_ssh(db))
    all_alerts.extend(detect_http_scanner(db))
    all_alerts.extend(detect_privilege_escalation(db))
    all_alerts.extend(detect_off_hours_access(db))

    db.commit()

    return {
        "total_alerts": len(all_alerts),
        "by_severity": {
            "CRITICAL": len([a for a in all_alerts if a.severity == "CRITICAL"]),
            "HIGH": len([a for a in all_alerts if a.severity == "HIGH"]),
            "MEDIUM": len([a for a in all_alerts if a.severity == "MEDIUM"]),
            "LOW": len([a for a in all_alerts if a.severity == "LOW"]),
        },
        "by_type": {
            alert_type: len([a for a in all_alerts if a.alert_type == alert_type])
            for alert_type in set(a.alert_type for a in all_alerts)
        }
    }