from fastapi import Request
from fastapi.responses import JSONResponse
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(f"[{req_id}] Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": req_id
            }
        }
    )
