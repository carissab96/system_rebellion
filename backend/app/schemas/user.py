# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime


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


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    operating_system: Optional[str] = None
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    total_memory: Optional[int] = None
    avatar: Optional[str] = None
    is_onboarded: Optional[bool] = False,
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    is_active: bool


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse