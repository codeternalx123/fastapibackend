from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============ REQUEST MODELS ============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=1, description="User's full name")
    metadata: Optional[Dict[str, Any]] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class OTPRequest(BaseModel):
    email: EmailStr
    action: str = Field(..., description="Action type: 'login', 'verify_email', 'transaction'")


class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    action: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UpdateSettingsRequest(BaseModel):
    language: Optional[str] = None
    timezone: Optional[str] = None
    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    notification_sms: Optional[bool] = None
    privacy_profile_public: Optional[bool] = None
    privacy_show_activity: Optional[bool] = None
    privacy_show_location: Optional[bool] = None
    privacy_show_email: Optional[bool] = None
    privacy_show_phone: Optional[bool] = None
    two_factor_enabled: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None


# ============ RESPONSE MODELS ============

class UserSettings(BaseModel):
    language: str = "en"
    timezone: str = "UTC"
    notifications: Dict[str, bool]
    privacy: Dict[str, bool]
    twoFactorEnabled: bool = False
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_email_verified: bool
    roles: List[str]
    created_at: datetime
    last_login_at: Optional[datetime] = None
    settings: UserSettings
    subscription: Optional[Dict[str, Any]] = None
    profile_picture: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    user: UserResponse


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class OTPResponse(BaseModel):
    message: str
    verified: bool = False
