from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger('app')

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        return response

class SQLInjectionMiddleware(BaseHTTPMiddleware):
    SUSPICIOUS_SQL_PATTERNS = [
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP",
        "UNION", "OR '1'='1", "OR 1=1",
        "--", ";", "/*", "*/"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Check query parameters
        query_params = request.query_params
        for param in query_params.values():
            if self._contains_sql_injection(param):
                logger.warning(f"Potential SQL injection detected in query params: {param}")
                return Response(
                    content="Invalid request",
                    status_code=400
                )
        
        # Check path parameters
        path_params = request.path_params
        for param in path_params.values():
            if self._contains_sql_injection(str(param)):
                logger.warning(f"Potential SQL injection detected in path params: {param}")
                return Response(
                    content="Invalid request",
                    status_code=400
                )
        
        return await call_next(request)
    
    def _contains_sql_injection(self, value: str) -> bool:
        value = value.upper()
        return any(pattern.upper() in value for pattern in self.SUSPICIOUS_SQL_PATTERNS)