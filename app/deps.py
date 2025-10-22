from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import decode_access_token as decode_token
from app.core.database import get_db
from app.models.database import User
from app.core.config import settings
import time
from redis import Redis
from typing import Generator

security = HTTPBearer()
redis = Redis.from_url(settings.REDIS_URL)

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
