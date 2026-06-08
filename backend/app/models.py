from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class LogEntry(Base):
    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    log_type: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_line: Mapped[str] = mapped_column(Text, nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=True)
    path: Mapped[str] = mapped_column(String(500), nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=True)
    user: Mapped[str] = mapped_column(String(100), nullable=True)
    event: Mapped[str] = mapped_column(String(100), nullable=True)

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    ai_explanation: Mapped[str] = mapped_column(Text, nullable=True)