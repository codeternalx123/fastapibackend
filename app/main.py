from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.routes import (
    auth, plan, reports, health, analytics, 
    food_scanning, quantum_payments, mpesa_payments, supabase_auth
)
from app.deps import rate_limit
from app.middleware.logging import RequestMiddleware
from app.middleware.security import SecurityHeadersMiddleware, SQLInjectionMiddleware

logger = setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="TumorHeal API - Health Optimization Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    dependencies=[Depends(rate_limit)]
)

# Security middlewares
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SQLInjectionMiddleware)
app.add_middleware(RequestMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# API Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(supabase_auth.router, tags=["supabase-auth"])
app.include_router(plan.router, prefix="/api/v1/plan", tags=["plan"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(food_scanning.router, prefix="/api/v1/food", tags=["food-scanning"])
app.include_router(quantum_payments.router, prefix="/api/v1/payments", tags=["quantum-secure-payments"])
app.include_router(mpesa_payments.router, tags=["mpesa-payments"])

@app.get('/health')
def health():
    return {'status': 'ok'}
