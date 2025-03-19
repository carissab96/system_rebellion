from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=12)
    
    @validator('password')
    def validate_password(cls, password):
        # Sir Hawkington's Distinguished Password Validation
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r'\d', password):
            raise ValueError("Password must contain a number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain a special character")
        return password

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

class UserProfileCreate(BaseModel):
    location: Optional[str] = None
    website: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_profile: Optional[str] = None
    theme_preference: str = 'system'
    notification_settings: str = 'all'
    optimization_level: str = 'balanced'

class UserProfileResponse(UserProfileCreate):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime    