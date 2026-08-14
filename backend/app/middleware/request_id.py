import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        request.state.request_id = req_id
        
        # Inject request_id into standard logging module via context or filter
        # Because we use a filter, we just rely on the logging framework checking the context.
        # Python's contextvars can do this globally, but for simplicity we just store it in request.state
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response
