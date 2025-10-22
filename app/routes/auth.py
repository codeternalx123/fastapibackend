from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.schemas import UserIn, UserCreate, UserOut, UserUpdate, Token, PasswordReset
from app.models.database import User
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from app.core.config import settings
from app.deps import get_db, get_current_user, rate_limit
from app.utils.email import send_reset_password_email
import secrets

router = APIRouter()

@router.post('/register', response_model=UserOut)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        is_active=True
    )
    user.set_password(user_in.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post('/login', response_model=Token, dependencies=[Depends(rate_limit)])
async def login(
    user_in: UserIn,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_in.username).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    if not user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        {'sub': user.email, 'is_superuser': user.is_superuser},
        expires_delta=access_token_expires
    )
    return {'access_token': token, 'token_type': 'bearer'}

@router.post("/password-reset/request")
async def request_password_reset(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if user:
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        db.commit()
        
        background_tasks.add_task(
            send_reset_password_email,
            email_to=user.email,
            token=reset_token
        )
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/password-reset/verify")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.reset_token == reset_data.token,
        User.reset_token_expires > func.now()
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user.set_password(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password successfully reset"}

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_in.password:
        current_user.set_password(user_in.password)
    if user_in.full_name:
        current_user.full_name = user_in.full_name
        
    db.commit()
    db.refresh(current_user)
    return current_user
