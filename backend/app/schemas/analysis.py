from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel

from app.core.enums import AnalysisStatus

class AnalysisCreate(BaseModel):
    project_id: UUID
    query: str

class AnalysisUpdate(BaseModel):
    status: Optional[AnalysisStatus] = None
    paper_count: Optional[int] = None
    topic_count: Optional[int] = None
    gap_count: Optional[int] = None
    summary: Optional[str] = None
    raw_response: Optional[dict] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class AnalysisBase(BaseModel):
    id: UUID
    project_id: UUID
    query: str
    status: AnalysisStatus
    paper_count: int
    topic_count: int
    gap_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class AnalysisListItem(AnalysisBase):
    pass

class AnalysisResponse(AnalysisBase):
    summary: Optional[str]
    raw_response: Optional[dict]
    error_message: Optional[str]

    class Config:
        from_attributes = True
