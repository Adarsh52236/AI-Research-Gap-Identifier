from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    tags: List[str] = Field(default_factory=list)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    tags: Optional[List[str]] = None

class ProjectResponse(ProjectBase):
    id: UUID
    favorite: bool
    owner_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
