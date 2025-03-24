from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.system import SystemConfiguration, ConfigType
from app.schemas.configuration import (
    SystemConfiguration as SystemConfigurationSchema,
    SystemConfigurationCreate,
    SystemConfigurationUpdate,
    SystemConfigurationList
)

router = APIRouter()


@router.get("/", response_model=SystemConfigurationList)
async def get_system_configurations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    config_type: Optional[ConfigType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all system configurations for the current user.
    """
    query = select(SystemConfiguration).where(
        SystemConfiguration.user_id == current_user.id
    )
    
    if config_type:
        query = query.where(SystemConfiguration.config_type == config_type)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    configurations = result.scalars().all()
    
    # Count total configurations
    count_query = select(SystemConfiguration).where(
        SystemConfiguration.user_id == current_user.id
    )
    
    if config_type:
        count_query = count_query.where(SystemConfiguration.config_type == config_type)
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    return {"configurations": configurations, "total": total}


@router.post("/", response_model=SystemConfigurationSchema, status_code=status.HTTP_201_CREATED)
async def create_system_configuration(
    config_data: SystemConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new system configuration.
    """
    configuration = SystemConfiguration(
        user_id=current_user.id,
        user=current_user,
        name=config_data.name,
        description=config_data.description,
        config_type=config_data.config_type,
        settings=config_data.settings,
        is_active=config_data.is_active
    )
    
    db.add(configuration)
    await db.commit()
    await db.refresh(configuration)
    
    return configuration


@router.get("/{config_id}", response_model=SystemConfigurationSchema)
async def get_system_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific system configuration by ID.
    """
    query = select(SystemConfiguration).where(
        SystemConfiguration.id == str(config_id),
        SystemConfiguration.user_id == current_user.id
    )
    
    result = await db.execute(query)
    configuration = result.scalars().first()
    
    if not configuration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System configuration not found"
        )
    
    return configuration


@router.put("/{config_id}", response_model=SystemConfigurationSchema)
async def update_system_configuration(
    config_id: UUID,
    config_data: SystemConfigurationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing system configuration.
    """
    query = select(SystemConfiguration).where(
        SystemConfiguration.id == str(config_id),
        SystemConfiguration.user_id == current_user.id
    )
    
    result = await db.execute(query)
    configuration = result.scalars().first()
    
    if not configuration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System configuration not found"
        )
    
    # Update configuration fields
    if config_data.name is not None:
        configuration.name = config_data.name
    if config_data.description is not None:
        configuration.description = config_data.description
    if config_data.config_type is not None:
        configuration.config_type = config_data.config_type
    if config_data.settings is not None:
        configuration.settings = config_data.settings
    if config_data.is_active is not None:
        configuration.is_active = config_data.is_active
    
    await db.commit()
    await db.refresh(configuration)
    
    return configuration


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a system configuration.
    """
    query = select(SystemConfiguration).where(
        SystemConfiguration.id == str(config_id),
        SystemConfiguration.user_id == current_user.id
    )
    
    result = await db.execute(query)
    configuration = result.scalars().first()
    
    if not configuration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System configuration not found"
        )
    
    await db.delete(configuration)
    await db.commit()
    
    return None


@router.post("/{config_id}/activate", response_model=SystemConfigurationSchema)
async def activate_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Activate a specific system configuration and deactivate all others of the same type.
    """
    # First, get the configuration to activate
    query = select(SystemConfiguration).where(
        SystemConfiguration.id == str(config_id),
        SystemConfiguration.user_id == current_user.id
    )
    
    result = await db.execute(query)
    configuration = result.scalars().first()
    
    if not configuration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System configuration not found"
        )
    
    # Deactivate all configurations of the same type
    query = select(SystemConfiguration).where(
        SystemConfiguration.user_id == current_user.id,
        SystemConfiguration.config_type == configuration.config_type,
        SystemConfiguration.is_active == True
    )
    
    result = await db.execute(query)
    active_configs = result.scalars().all()
    
    for config in active_configs:
        config.is_active = False
    
    # Activate the requested configuration
    configuration.is_active = True
    
    await db.commit()
    await db.refresh(configuration)
    
    return configuration
