"""Health check endpoint."""
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AI Research Gap Identifier API",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

from backend.app.db.session import SessionLocal
from backend.app.config import settings
from backend.app.core.storage.artifact_store import get_artifact_store
import time
from sqlalchemy import text

@router.get("/deep")
async def deep_health_check():
    """Deep health check endpoint for cloud diagnosis."""
    response = {
        "status": "ok",
        "db_ok": False,
        "supabase_storage_ok": False,
        "vector_backend": settings.VECTOR_BACKEND,
        "artifact_backend": settings.ARTIFACT_BACKEND,
    }
    
    # Check DB
    if settings.DB_ENABLED:
        try:
            start_time = time.time()
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            if (time.time() - start_time) < 2.0:
                response["db_ok"] = True
        except Exception:
            pass

    # Check Supabase Storage
    if settings.ARTIFACT_BACKEND.lower() == "supabase":
        try:
            store = get_artifact_store()
            # Lightweight check: list buckets
            store.client.storage.list_buckets()
            response["supabase_storage_ok"] = True
        except Exception:
            pass

    if not response["db_ok"] and settings.DB_ENABLED:
        response["status"] = "degraded"
        
    return response

@router.get("/debug/db")
async def debug_db():
    from backend.app.db.session import SessionLocal
    from backend.app.db.models import PipelineRunRow
    from sqlalchemy import select
    
    db = SessionLocal()
    try:
        # Try to query the session_id column to see if it exists
        row = db.execute(select(PipelineRunRow).limit(1)).scalar_one_or_none()
        return {"status": "ok", "message": "Database query succeeded", "row_found": row is not None}
    except Exception as e:
        return {"status": "error", "error": str(e), "type": type(e).__name__}
    finally:
        db.close()
