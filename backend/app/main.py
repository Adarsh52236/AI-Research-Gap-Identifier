"""FastAPI app entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.api.v1 import search, upload, analysis, report, health, papers


def _parse_origins(origins: str) -> list[str]:
    # Accept comma-separated origins in env
    return [o.strip() for o in origins.split(",") if o.strip()]


app = FastAPI(
    title="AI Research Gap Identifier API",
    version="0.1.0",
)

# TODO: Restrict origins later for production
allowed_origins = ["*"] # _parse_origins(settings.ALLOWED_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(report.router, prefix="/api/v1/report", tags=["report"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(papers.router, prefix="/api/v1/papers", tags=["papers"])
