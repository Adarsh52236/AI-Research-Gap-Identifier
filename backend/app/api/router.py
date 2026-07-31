from fastapi import APIRouter
from app.api.endpoints import health
from app.api.endpoints import diagnostics
from app.api.endpoints import auth
from app.api.endpoints import chat

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
api_router.include_router(diagnostics.router, prefix="/diagnostics", tags=["diagnostics"])
api_router.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
