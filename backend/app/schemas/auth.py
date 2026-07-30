from pydantic import BaseModel, EmailStr, Field
import uuid

class RegisterRequest(BaseModel):
    full_name: str = Field(..., max_length=150)
    email: EmailStr = Field(...)
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CurrentUser(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    
    model_config = {"from_attributes": True}
