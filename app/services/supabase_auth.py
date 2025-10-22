from supabase import Client
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import secrets
import bcrypt
from fastapi import HTTPException, status

from app.core.supabase_config import get_supabase_client, get_supabase_admin_client
from app.models.auth_schemas import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    UserSettings,
    UpdateProfileRequest,
    UpdateSettingsRequest
)


class SupabaseAuthService:
    """Service for authentication operations using Supabase"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.admin_client = get_supabase_admin_client()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    async def register_user(self, request: RegisterRequest) -> Dict[str, Any]:
        """Register a new user"""
        
        # Check if user exists
        existing = self.client.table('users').select('id').eq('email', request.email).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user_id = f"user_{secrets.token_urlsafe(16)}"
        password_hash = self.hash_password(request.password)
        
        user_data = {
            "id": user_id,
            "email": request.email,
            "password_hash": password_hash,
            "name": request.name,
            "is_email_verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": request.metadata or {}
        }
        
        # Insert user
        result = self.client.table('users').insert(user_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Assign default role
        self.client.table('user_roles').insert({
            "user_id": user_id,
            "role": "user"
        }).execute()
        
        # Create default settings
        await self._create_default_settings(user_id)
        
        return result.data[0]
    
    async def login_user(self, request: LoginRequest) -> Dict[str, Any]:
        """Login user and return user data"""
        
        # Find user
        result = self.client.table('users').select('*').eq('email', request.email).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = result.data[0]
        
        # Verify password
        if not self.verify_password(request.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        self.client.table('users').update({
            "last_login_at": datetime.utcnow().isoformat()
        }).eq('id', user['id']).execute()
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        result = self.client.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        result = self.client.table('users').select('*').eq('email', email).execute()
        return result.data[0] if result.data else None
    
    async def get_user_roles(self, user_id: str) -> List[str]:
        """Get user roles"""
        result = self.client.table('user_roles').select('role').eq('user_id', user_id).execute()
        return [r['role'] for r in result.data] if result.data else []
    
    async def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user settings"""
        result = self.client.table('user_settings').select('*').eq('user_id', user_id).execute()
        
        if not result.data:
            # Create default settings if not exist
            await self._create_default_settings(user_id)
            result = self.client.table('user_settings').select('*').eq('user_id', user_id).execute()
        
        settings = result.data[0] if result.data else {}
        
        return {
            "language": settings.get("language", "en"),
            "timezone": settings.get("timezone", "UTC"),
            "notifications": {
                "email": settings.get("notification_email", True),
                "push": settings.get("notification_push", True),
                "sms": settings.get("notification_sms", False),
            },
            "privacy": {
                "isProfilePublic": settings.get("privacy_profile_public", False),
                "showActivity": settings.get("privacy_show_activity", True),
                "showLocation": settings.get("privacy_show_location", True),
                "showEmail": settings.get("privacy_show_email", False),
                "showPhone": settings.get("privacy_show_phone", False),
            },
            "twoFactorEnabled": settings.get("two_factor_enabled", False),
            "preferences": settings.get("preferences", {}),
        }
    
    async def _create_default_settings(self, user_id: str):
        """Create default settings for a user"""
        settings_data = {
            "user_id": user_id,
            "language": "en",
            "timezone": "UTC",
            "notification_email": True,
            "notification_push": True,
            "notification_sms": False,
            "privacy_profile_public": False,
            "privacy_show_activity": True,
            "privacy_show_location": True,
            "privacy_show_email": False,
            "privacy_show_phone": False,
            "two_factor_enabled": False,
            "preferences": {}
        }
        self.client.table('user_settings').insert(settings_data).execute()
    
    async def update_user_profile(self, user_id: str, request: UpdateProfileRequest) -> Dict[str, Any]:
        """Update user profile"""
        update_data = {}
        
        if request.name is not None:
            update_data["name"] = request.name
        if request.profile_picture is not None:
            update_data["profile_picture"] = request.profile_picture
        if request.metadata is not None:
            update_data["metadata"] = request.metadata
        
        if update_data:
            result = self.client.table('users').update(update_data).eq('id', user_id).execute()
            return result.data[0] if result.data else {}
        
        return await self.get_user_by_id(user_id)
    
    async def update_user_settings(self, user_id: str, request: UpdateSettingsRequest) -> Dict[str, Any]:
        """Update user settings"""
        update_data = {}
        
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        if update_data:
            result = self.client.table('user_settings').update(update_data).eq('user_id', user_id).execute()
        
        return await self.get_user_settings(user_id)
    
    async def create_password_reset_token(self, email: str) -> str:
        """Create password reset token"""
        user = await self.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists
            return ""
        
        reset_token = secrets.token_urlsafe(32)
        expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        
        self.client.table('password_reset_tokens').insert({
            "user_id": user['id'],
            "token": reset_token,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return reset_token
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        # Find token
        result = self.client.table('password_reset_tokens').select('*').eq('token', token).eq('used', False).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        token_data = result.data[0]
        
        # Check expiry
        if datetime.fromisoformat(token_data['expires_at']) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Update password
        password_hash = self.hash_password(new_password)
        self.client.table('users').update({
            "password_hash": password_hash
        }).eq('id', token_data['user_id']).execute()
        
        # Mark token as used
        self.client.table('password_reset_tokens').update({
            "used": True
        }).eq('id', token_data['id']).execute()
        
        return True
    
    async def create_otp(self, email: str, action: str) -> str:
        """Create OTP code"""
        otp_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        expires_at = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        
        self.client.table('otp_tokens').insert({
            "email": email,
            "otp_code": otp_code,
            "action": action,
            "expires_at": expires_at,
            "verified": False,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return otp_code
    
    async def verify_otp(self, email: str, otp_code: str, action: str) -> bool:
        """Verify OTP code"""
        result = self.client.table('otp_tokens').select('*').eq('email', email).eq('otp_code', otp_code).eq('action', action).eq('verified', False).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code"
            )
        
        otp_data = result.data[0]
        
        # Check expiry
        if datetime.fromisoformat(otp_data['expires_at']) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired"
            )
        
        # Mark as verified
        self.client.table('otp_tokens').update({
            "verified": True
        }).eq('id', otp_data['id']).execute()
        
        return True
    
    async def user_to_response(self, user: Dict[str, Any]) -> UserResponse:
        """Convert user dict to UserResponse"""
        roles = await self.get_user_roles(user['id'])
        settings_dict = await self.get_user_settings(user['id'])
        
        settings = UserSettings(
            language=settings_dict.get("language", "en"),
            timezone=settings_dict.get("timezone", "UTC"),
            notifications=settings_dict.get("notifications", {}),
            privacy=settings_dict.get("privacy", {}),
            twoFactorEnabled=settings_dict.get("twoFactorEnabled", False),
            preferences=settings_dict.get("preferences")
        )
        
        return UserResponse(
            id=user['id'],
            email=user['email'],
            name=user['name'],
            is_email_verified=user.get('is_email_verified', False),
            roles=roles,
            created_at=datetime.fromisoformat(user['created_at']) if isinstance(user['created_at'], str) else user['created_at'],
            last_login_at=datetime.fromisoformat(user['last_login_at']) if user.get('last_login_at') and isinstance(user['last_login_at'], str) else user.get('last_login_at'),
            settings=settings,
            profile_picture=user.get('profile_picture'),
            metadata=user.get('metadata')
        )
