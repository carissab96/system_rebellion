from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional, Dict, Any
from datetime import datetime


# Basic user profile data
class UserProfileData(BaseModel):
    operating_system: Optional[str] = None
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    total_memory: Optional[int] = None
    linux_distro: Optional[str] = None
    linux_distro_version: Optional[str] = None
    avatar: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_profile: Optional[str] = None

# User preferences data
class UserPreferencesData(BaseModel):
    optimization_level: Optional[str] = "balanced"
    theme_preferences: Optional[Dict[str, Any]] = None
    notification_settings: Optional[str] = "all"
    theme_preference: Optional[str] = "system"

# Base user model with common fields
class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr

# Model for creating a new user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    profile: Optional[UserProfileData] = None
    preferences: Optional[UserPreferencesData] = None

# Model for updating user profile
class UserProfileUpdate(BaseModel):
    profile: Optional[UserProfileData] = None
    preferences: Optional[UserPreferencesData] = None

# Complete user response model
class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    needs_onboarding: bool = True
    
    # System information
    operating_system: Optional[str] = None
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    total_memory: Optional[int] = None
    avatar: Optional[str] = None
    
    # Extended profile and preferences
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True