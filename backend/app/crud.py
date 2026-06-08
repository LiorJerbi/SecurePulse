from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models import LogEntry
from app.parser import parse_log_file


def store_log_entries(db: Session, entries: list[dict]) -> int:
    db_entries = [LogEntry(**entry) for entry in entries]
    db.add_all(db_entries)
    db.commit()
    return len(db_entries)


def get_log_entries(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    source_ip: str = None,
    log_type: str = None,
    status_code: int = None,
) -> tuple[int, list[LogEntry]]:
    query = select(LogEntry)

    if source_ip:
        query = query.where(LogEntry.source_ip == source_ip)
    if log_type:
        query = query.where(LogEntry.log_type == log_type)
    if status_code:
        query = query.where(LogEntry.status_code == status_code)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()

    offset = (page - 1) * page_size
    query = query.order_by(LogEntry.timestamp.desc()).offset(offset).limit(page_size)
    results = db.execute(query).scalars().all()

    return total, results