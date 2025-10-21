# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
from enum import Enum

class UserRole(str, Enum):
    """User roles for access control"""
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"
    SERVICE_ACCOUNT = "service_account"

class User(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    role: UserRole = UserRole.USER

class UserProfileData(BaseModel):
    operating_system: Optional[str] = None
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    total_memory: Optional[int] = None
    linux_distro: Optional[str] = None
    linux_distro_version: Optional[str] = None
    avatar: Optional[str] = None

class UserPreferencesData(BaseModel):
    optimization_level: Optional[str] = None
    theme_preferences: Optional[Dict[str, Any]] = None

class UserProfileUpdate(BaseModel):
    profile: Optional[UserProfileData] = None
    preferences: Optional[UserPreferencesData] = None

class UserCreate(User):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class UserInDB(User):
    """User model as stored in the database"""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    
    class Config:
        from_attributes = True

class UserResponse(User):
    """User model for API responses"""
    id: str
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    operating_system: Optional[str] = None
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    total_memory: Optional[int] = None
    avatar: Optional[str] = None
    is_onboarded: bool = False
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenPayload(BaseModel):
    """Payload included in JWT tokens"""
    sub: str  # Subject (user ID)
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    type: str  # Token type (access, refresh, etc.)
    scopes: List[str] = []  # List of permissions/roles
    
    @validator('exp', 'iat', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v

class Token(BaseModel):
    """Authentication token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(
        7200,
        description="Number of seconds until the access token expires"
    )
    user: UserResponse = Field(..., description="Authenticated user information")

class TokenData(BaseModel):
    """Data extracted from a token"""
    user_id: str
    scopes: List[str] = []
    expires: Optional[datetime] = None

class PasswordResetRequest(BaseModel):
    """Request to reset a password"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token and new password"""
    token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(..., min_length=8, description="New password")

class ChangePassword(BaseModel):
    """Change password while authenticated"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")