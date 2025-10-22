from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import jwt
from datetime import datetime, timedelta
import os

from app.models.auth_schemas import (
    RegisterRequest,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    OTPRequest,
    OTPVerify,
    AuthResponse,
    UserResponse,
    MessageResponse,
    OTPResponse,
    TokenResponse,
    UpdateProfileRequest,
    UpdateSettingsRequest
)
from app.services.supabase_auth import SupabaseAuthService

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

auth_service = SupabaseAuthService()


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user"""
    user = await auth_service.register_user(request)
    
    # Create JWT token
    access_token = create_access_token(
        data={"user_id": user['id'], "email": user['email']}
    )
    
    # Convert to response
    user_response = await auth_service.user_to_response(user)
    
    return AuthResponse(
        access_token=access_token,
        user=user_response
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user"""
    user = await auth_service.login_user(request)
    
    # Create JWT token
    access_token = create_access_token(
        data={"user_id": user['id'], "email": user['email']}
    )
    
    # Convert to response
    user_response = await auth_service.user_to_response(user)
    
    return AuthResponse(
        access_token=access_token,
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return await auth_service.user_to_response(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile"""
    updated_user = await auth_service.update_user_profile(current_user['id'], request)
    return await auth_service.user_to_response(updated_user)


@router.put("/settings", response_model=Dict[str, Any])
async def update_settings(
    request: UpdateSettingsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user settings"""
    return await auth_service.update_user_settings(current_user['id'], request)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: PasswordResetRequest):
    """Request password reset"""
    reset_token = await auth_service.create_password_reset_token(request.email)
    
    # TODO: Send email with reset link
    # send_password_reset_email(request.email, reset_token)
    
    if reset_token:
        print(f"Password reset token for {request.email}: {reset_token}")
    
    return MessageResponse(
        message="If your email is registered, you will receive a password reset link"
    )


@router.post("/reset-password/confirm", response_model=MessageResponse)
async def confirm_reset_password(request: PasswordResetConfirm):
    """Confirm password reset with token"""
    await auth_service.reset_password(request.token, request.new_password)
    return MessageResponse(message="Password reset successful")


@router.post("/otp/request", response_model=MessageResponse)
async def request_otp(request: OTPRequest):
    """Request OTP code"""
    otp_code = await auth_service.create_otp(request.email, request.action)
    
    # TODO: Send OTP via email/SMS
    # send_otp_email(request.email, otp_code)
    
    print(f"OTP for {request.email}: {otp_code}")
    
    return MessageResponse(message="OTP sent successfully")


@router.post("/otp/verify", response_model=OTPResponse)
async def verify_otp(request: OTPVerify):
    """Verify OTP code"""
    verified = await auth_service.verify_otp(request.email, request.otp_code, request.action)
    return OTPResponse(message="OTP verified successfully", verified=verified)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Refresh access token"""
    access_token = create_access_token(
        data={"user_id": current_user['id'], "email": current_user['email']}
    )
    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout user (client should delete token)"""
    return MessageResponse(message="Logged out successfully")
