from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LogEntryResponse(BaseModel):
    id: int
    timestamp: datetime
    source_ip: str
    log_type: str
    method: Optional[str]
    path: Optional[str]
    status_code: Optional[int]
    user: Optional[str]
    event: Optional[str]
    raw_line: str

    model_config = {"from_attributes": True}


class IngestResponse(BaseModel):
    message: str
    log_type: str
    lines_parsed: int
    lines_stored: int


class PaginatedLogs(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[LogEntryResponse]