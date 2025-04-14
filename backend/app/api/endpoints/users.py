from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.api.deps import get_current_user, get_db
from app.models.user import User

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

class UserUpdateSchema(BaseModel):
    """
    Schema for updating user information
    """
    operating_system: str = None
    os_version: str = None
    cpu_cores: int = None
    total_memory: int = None
    first_name: str = None
    last_name: str = None
    bio: str = None
    
    class Config:
        orm_mode = True

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user)
):
    # Log request headers for debugging
    logger.info(f"Request headers: {request.headers}")
    
    # Check if user is authenticated
    if not current_user:
        logger.error("User not authenticated")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    """
    Sir Hawkington's User Profile Protocol
    
    Get current user information
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "bio": current_user.bio,
        "operating_system": current_user.operating_system,
        "os_version": current_user.os_version,
        "cpu_cores": current_user.cpu_cores,
        "total_memory": current_user.total_memory,
        "needs_onboarding": current_user.needs_onboarding,
        "avatar": current_user.avatar
    }

@router.patch("/me", response_model=Dict[str, Any])
async def update_current_user(
    request: Request,
    user_data: UserUpdateSchema,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Log request headers for debugging
    logger.info(f"PATCH /me request headers: {request.headers}")
    logger.info(f"PATCH /me request data: {user_data}")
    
    # Check if user is authenticated
    if not current_user:
        logger.error("User not authenticated for profile update")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"}
        )
    """
    The Meth Snail's User Update Protocol
    
    Update current user information
    """
    # Update user fields if provided in the request
    if user_data.operating_system is not None:
        current_user.operating_system = user_data.operating_system
    if user_data.os_version is not None:
        current_user.os_version = user_data.os_version
    if user_data.cpu_cores is not None:
        current_user.cpu_cores = user_data.cpu_cores
    if user_data.total_memory is not None:
        current_user.total_memory = user_data.total_memory
    if user_data.first_name is not None:
        current_user.first_name = user_data.first_name
    if user_data.last_name is not None:
        current_user.last_name = user_data.last_name
    if user_data.bio is not None:
        current_user.bio = user_data.bio
    
    # Save changes to database
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    # Return updated user information
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "bio": current_user.bio,
        "operating_system": current_user.operating_system,
        "os_version": current_user.os_version,
        "cpu_cores": current_user.cpu_cores,
        "total_memory": current_user.total_memory,
        "needs_onboarding": current_user.needs_onboarding,
        "avatar": current_user.avatar
    }
