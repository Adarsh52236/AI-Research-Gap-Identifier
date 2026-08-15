"""FastAPI app entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.db.session import engine
from backend.app.db.models import Base
from backend.app.api.v1 import search, upload, analysis, report, health, papers, auth, review

from backend.app.utils.logger import get_logger
logger = get_logger(__name__)

# Initialize DB tables if DB is enabled
if settings.DB_ENABLED and engine:
    dialect = engine.dialect.name
    logger.info(f"Database is ENABLED. Dialect in use: {dialect}")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
else:
    logger.info("Database is DISABLED or engine is not configured.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def _parse_origins(origins: str) -> list[str]:
    # Accept comma-separated origins in env
    return [o.strip() for o in origins.split(",") if o.strip()]


from backend.app.middleware.error_handler import global_exception_handler
from backend.app.middleware.request_id import RequestIdMiddleware
from backend.app.middleware.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI(
    title="AI Research Gap Identifier API",
    version="0.1.0",
)

# Exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Rate Limiter
app.state.limiter = limiter

# Middlewares (Order matters: outermost first)
app.add_middleware(RequestIdMiddleware)

allowed_origins = _parse_origins(settings.ALLOWED_ORIGINS)

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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(review.router, prefix="/api/v1/review", tags=["review"])
