from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.system import OptimizationProfile
from app.schemas.optimization import (
    OptimizationProfile as OptimizationProfileSchema,
    OptimizationProfileCreate,
    OptimizationProfileUpdate,
    OptimizationProfileList
)

router = APIRouter()


@router.get("/", response_model=OptimizationProfileList)
async def get_optimization_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all optimization profiles for the current user.
    """
    import logging
    import uuid
    from datetime import datetime
    
    logger = logging.getLogger("optimization_api")
    logger.info(f"Fetching optimization profiles for user {current_user.id}")
    
    query = select(OptimizationProfile).where(
        OptimizationProfile.user_id == current_user.id
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    profiles = result.scalars().all()
    
    # Count total profiles
    count_query = select(OptimizationProfile).where(
        OptimizationProfile.user_id == current_user.id
    )
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # If no profiles exist, create some test ones
    if not profiles:
        logger.warning(f"No profiles found for user {current_user.id}, creating test profiles")
        
        # Create test profiles
        test_profiles = [
            OptimizationProfile(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                name="Balanced Performance",
                description="Default profile with balanced settings for performance and power usage",
                settings={
                    "cpu_governor": "ondemand",
                    "swapiness": 60,
                    "vm_dirty_ratio": 20,
                    "vm_dirty_background_ratio": 10,
                    "cpuThreshold": 80,
                    "memoryThreshold": 80,
                    "diskThreshold": 90,
                    "networkThreshold": 70,
                    "enableAutoTuning": True,
                    "cpuPriority": "medium",
                    "backgroundProcessLimit": 25,
                    "memoryAllocation": {
                        "applications": 70,
                        "systemCache": 30
                    },
                    "diskPerformance": "balance",
                    "networkOptimization": {
                        "prioritizeStreaming": False,
                        "prioritizeDownloads": False,
                        "lowLatencyMode": False
                    },
                    "powerProfile": "balanced"
                },
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            OptimizationProfile(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                name="High Performance",
                description="Optimized for maximum performance at the cost of power efficiency",
                settings={
                    "cpu_governor": "performance",
                    "swapiness": 10,
                    "vm_dirty_ratio": 10,
                    "vm_dirty_background_ratio": 5,
                    "cpuThreshold": 90,
                    "memoryThreshold": 85,
                    "diskThreshold": 95,
                    "networkThreshold": 60,
                    "enableAutoTuning": True,
                    "cpuPriority": "high",
                    "backgroundProcessLimit": 10,
                    "memoryAllocation": {
                        "applications": 85,
                        "systemCache": 15
                    },
                    "diskPerformance": "speed",
                    "networkOptimization": {
                        "prioritizeStreaming": True,
                        "prioritizeDownloads": True,
                        "lowLatencyMode": True
                    },
                    "powerProfile": "performance"
                },
                is_active=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            OptimizationProfile(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                name="Power Saving",
                description="Optimized for maximum battery life and power efficiency",
                settings={
                    "cpu_governor": "powersave",
                    "swapiness": 80,
                    "vm_dirty_ratio": 30,
                    "vm_dirty_background_ratio": 20,
                    "cpuThreshold": 60,
                    "memoryThreshold": 70,
                    "diskThreshold": 80,
                    "networkThreshold": 50,
                    "enableAutoTuning": True,
                    "cpuPriority": "low",
                    "backgroundProcessLimit": 50,
                    "memoryAllocation": {
                        "applications": 60,
                        "systemCache": 40
                    },
                    "diskPerformance": "powersave",
                    "networkOptimization": {
                        "prioritizeStreaming": False,
                        "prioritizeDownloads": False,
                        "lowLatencyMode": False
                    },
                    "powerProfile": "powersave"
                },
                is_active=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        # Add test profiles to the database
        for profile in test_profiles:
            db.add(profile)
        
        try:
            await db.commit()
            logger.info(f"Created {len(test_profiles)} test profiles for user {current_user.id}")
            
            # Refresh the profiles list with the newly created ones
            query = select(OptimizationProfile).where(
                OptimizationProfile.user_id == current_user.id
            ).offset(skip).limit(limit)
            
            result = await db.execute(query)
            profiles = result.scalars().all()
            
            # Update the total count
            count_query = select(OptimizationProfile).where(
                OptimizationProfile.user_id == current_user.id
            )
            count_result = await db.execute(count_query)
            total = len(count_result.scalars().all())
        except Exception as e:
            logger.error(f"Error creating test profiles: {str(e)}")
            await db.rollback()
            # Return the test profiles anyway, but they won't be persisted
            profiles = test_profiles
            total = len(test_profiles)
    
    return {"profiles": profiles, "total": total}


@router.post("/", response_model=OptimizationProfileSchema, status_code=status.HTTP_201_CREATED)
async def create_optimization_profile(
    profile_data: OptimizationProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new optimization profile.
    """
    profile = OptimizationProfile(
        user_id=current_user.id,
        name=profile_data.name,
        description=profile_data.description,
        settings=profile_data.settings,
        is_active=profile_data.is_active
    )
    
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.get("/{profile_id}", response_model=OptimizationProfileSchema)
async def get_optimization_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific optimization profile by ID.
    """
    query = select(OptimizationProfile).where(
        OptimizationProfile.id == str(profile_id),
        OptimizationProfile.user_id == current_user.id
    )
    
    result = await db.execute(query)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization profile not found"
        )
    
    return profile


@router.put("/{profile_id}", response_model=OptimizationProfileSchema)
async def update_optimization_profile(
    profile_id: UUID,
    profile_data: OptimizationProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing optimization profile.
    """
    query = select(OptimizationProfile).where(
        OptimizationProfile.id == str(profile_id),
        OptimizationProfile.user_id == current_user.id
    )
    
    result = await db.execute(query)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization profile not found"
        )
    
    # Update profile fields
    if profile_data.name is not None:
        profile.name = profile_data.name
    if profile_data.description is not None:
        profile.description = profile_data.description
    if profile_data.settings is not None:
        profile.settings = profile_data.settings
    if profile_data.is_active is not None:
        profile.is_active = profile_data.is_active
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_optimization_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an optimization profile.
    """
    query = select(OptimizationProfile).where(
        OptimizationProfile.id == str(profile_id),
        OptimizationProfile.user_id == current_user.id
    )
    
    result = await db.execute(query)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization profile not found"
        )
    
    await db.delete(profile)
    await db.commit()
    
    return None


@router.post("/{profile_id}/activate", response_model=OptimizationProfileSchema)
async def activate_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Activate a specific optimization profile and deactivate all others.
    """
    # First, deactivate all profiles
    query = select(OptimizationProfile).where(
        OptimizationProfile.user_id == current_user.id,
        OptimizationProfile.is_active == True
    )
    
    result = await db.execute(query)
    active_profiles = result.scalars().all()
    
    for profile in active_profiles:
        profile.is_active = False
    
    # Then, activate the requested profile
    query = select(OptimizationProfile).where(
        OptimizationProfile.id == str(profile_id),
        OptimizationProfile.user_id == current_user.id
    )
    
    result = await db.execute(query)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization profile not found"
        )
    
    profile.is_active = True
    
    await db.commit()
    await db.refresh(profile)
    
    return profile
