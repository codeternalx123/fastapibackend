from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import decode_access_token as decode_token
from app.core.database import get_db
from app.models.database import User
from app.core.config import settings
import time
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from typing import Generator
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

# Try to connect to Redis, but don't fail if it's not available
try:
    redis = Redis.from_url(settings.REDIS_URL)
    redis.ping()  # Test connection
    REDIS_AVAILABLE = True
    logger.info("Redis connected successfully")
except (RedisConnectionError, Exception) as e:
    redis = None
    REDIS_AVAILABLE = False
    logger.warning(f"Redis not available: {e}. Rate limiting disabled.")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user = db.query(User).filter(User.email == payload['sub']).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not enough privileges"
        )
    return current_user

def rate_limit(request: Request):
    """Rate limiting function - skips if Redis is not available"""
    if not REDIS_AVAILABLE or redis is None:
        # Skip rate limiting if Redis is not available
        return
    
    try:
        client = request.client.host
        key = f"rate_limit:{client}"
        current = redis.get(key)
        
        if current is not None and int(current) > settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        pipe.execute()
    except RedisConnectionError as e:
        # Log the error but don't block the request
        logger.warning(f"Redis connection error during rate limiting: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error in rate_limit: {e}")
        return
