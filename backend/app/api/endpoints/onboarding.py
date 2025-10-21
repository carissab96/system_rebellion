# backend/app/routers/onboarding.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json
import logging

from app.core.auth import get_current_user
from app.core.database import get_async_db
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response models
from pydantic import BaseModel

class OnboardingProgressRequest(BaseModel):
    current_step: int
    completed_steps: list[int]
    form_data: Dict[str, Any]

class OnboardingProgressResponse(BaseModel):
    current_step: int
    completed_steps: list[int]
    form_data: Dict[str, Any]
    started_at: str
    last_updated_at: str
    completion_percentage: float

@router.post("/onboarding-progress", response_model=Dict[str, Any])
async def save_onboarding_progress(
    progress_data: OnboardingProgressRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    print("🔥 ONBOARDING SAVE ENDPOINT HIT!")
    print(f"🔥 User: {current_user.email}")
    print(f"🔥 Data received: {progress_data}")
    """Save user's onboarding progress"""
    try:
        # Get fresh user object
        print("🔥 Getting user from database...")
        result = await db.execute(select(User).where(User.id == current_user.id))
        user = result.scalars().first()
        
        if not user:
            print("🔥 ERROR: User not found!")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update progress tracking
        now = datetime.now(timezone.utc)
        
        # Set started_at if this is the first save
        if not user.onboarding_started_at:
            print("🔥 Setting started_at (first save)")
            user.onboarding_started_at = now
            user.onboarding_abandoned_count = 0  # Reset counter on first save
        
        # Update step tracking
        print("🔥 Setting onboarding_progress...")
        user.onboarding_progress = progress_data.current_step  # INTEGER step
        user.onboarding_data = json.dumps({  # JSON data as TEXT
            "current_step": progress_data.current_step,
            "completed_steps": progress_data.completed_steps,
            "form_data": progress_data.form_data
        })
        user.onboarding_last_step_at = now
        
        await db.commit()
        await db.refresh(user)
        
        # Calculate completion percentage (assuming 5 total steps)
        completion_percentage = (progress_data.current_step / 5) * 100
        
        response_data = {
            "current_step": progress_data.current_step,
            "completed_steps": progress_data.completed_steps,
            "form_data": progress_data.form_data,
            "started_at": user.onboarding_started_at.isoformat(),
            "last_updated_at": user.onboarding_last_step_at.isoformat(),
            "completion_percentage": completion_percentage,
            "success": True
        }
        
        logger.info(f"Saved onboarding progress for user {user.email}: step {progress_data.current_step}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error saving onboarding progress: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save onboarding progress"
        )

@router.get("/onboarding-progress", response_model=Optional[OnboardingProgressResponse])
async def get_onboarding_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user's saved onboarding progress"""
    try:
        result = await db.execute(select(User).where(User.id == current_user.id))
        user = result.scalars().first()
        
        if not user or not user.onboarding_data:
            return None
        
        # Parse the JSON data
        progress_data = json.loads(user.onboarding_data)
        completion_percentage = (progress_data["current_step"] / 5) * 100
        
        return {
            "current_step": progress_data["current_step"],
            "completed_steps": progress_data["completed_steps"],
            "form_data": progress_data["form_data"],
            "started_at": user.onboarding_started_at.isoformat(),
            "last_updated_at": user.onboarding_last_step_at.isoformat(),
            "completion_percentage": completion_percentage
        }
        
    except Exception as e:
        logger.error(f"Error loading onboarding progress: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load onboarding progress"
        )

@router.delete("/onboarding-progress")
async def clear_onboarding_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Clear user's onboarding progress"""
    try:
        result = await db.execute(select(User).where(User.id == current_user.id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Clear progress data but increment abandonment counter
        user.onboarding_data = None
        user.onboarding_progress = None
        user.onboarding_abandoned_count += 1
        # Keep started_at and last_step_at for analytics
        
        await db.commit()
        
        logger.info(f"Cleared onboarding progress for user {user.email} (abandonment #{user.onboarding_abandoned_count})")
        return {"success": True, "message": "Onboarding progress cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing onboarding progress: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear onboarding progress"
        )