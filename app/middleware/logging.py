from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import time
import logging
from app.core.logging import RequestIdFilter

logger = logging.getLogger('app')

class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to logger
        request_filter = RequestIdFilter(request_id)
        logger.addFilter(request_filter)
        
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else None
            }
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = (time.time() - start_time) * 1000
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time, 2)
                }
            )
            
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            logger.exception(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "error": str(e)
                }
            )
            raise
        finally:
            # Remove request filter
            logger.removeFilter(request_filter)