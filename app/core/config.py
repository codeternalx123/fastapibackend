from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "TumorHeal API"
    SECRET_KEY: str = "CHANGE_ME_TO_A_STRONG_SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24
    DEBUG: bool = True
    CORS_ORIGINS: list = ["*"]  # change in production
    
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost/tumorheal"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Supabase settings
    SUPABASE_URL: str = "your-supabase-project-url"
    SUPABASE_KEY: str = "your-supabase-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # JWT settings
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # M-Pesa settings
    MPESA_ENVIRONMENT: str = "sandbox"
    MPESA_CONSUMER_KEY: Optional[str] = None
    MPESA_CONSUMER_SECRET: Optional[str] = None
    MPESA_SHORTCODE: Optional[str] = None
    MPESA_PASSKEY: Optional[str] = None
    MPESA_CALLBACK_URL: Optional[str] = None
    
    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Security settings
    ALLOWED_HOSTS: list = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 60
    JWT_SECRET_KEY: str = "CHANGE_ME_JWT_SECRET"
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True
    class Config:
        env_file = ".env"

settings = Settings()
