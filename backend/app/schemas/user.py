from typing import Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    full_name: str = Field(..., max_length=150)
    email: EmailStr = Field(...)
    username: str = Field(..., min_length=3, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    email_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class InternalUser(UserResponse):
    password_hash: str
    deleted_at: Optional[datetime] = None
