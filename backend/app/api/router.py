from fastapi import APIRouter
from app.api.endpoints import health, papers
from app.api.endpoints import analysis
from app.api.endpoints import diagnostics
from app.api.endpoints import projects
from app.api.endpoints import analyses
from app.api.endpoints import auth

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(analysis.router, prefix="/api/v1", tags=["analysis_old"])
api_router.include_router(diagnostics.router, prefix="/diagnostics", tags=["diagnostics"])
api_router.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
api_router.include_router(analyses.router, prefix="/api/v1", tags=["analyses"])
