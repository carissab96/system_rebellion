from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID


class OptimizationProfileBase(BaseModel):
    name: str
    description: Optional[str] = None
    settings: Dict[str, Any]
    is_active: bool = False


class OptimizationProfileCreate(OptimizationProfileBase):
    pass


class OptimizationProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class OptimizationProfileInDB(OptimizationProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class OptimizationProfile(OptimizationProfileInDB):
    pass


class OptimizationProfileList(BaseModel):
    profiles: List[OptimizationProfile]
    total: int
