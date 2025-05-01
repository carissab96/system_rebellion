from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class ConfigType(str, Enum):
    NETWORK = 'NETWORK'
    SYSTEM = 'SYSTEM'
    SECURITY = 'SECURITY'
    PERFORMANCE = 'PERFORMANCE'


class SystemConfigurationBase(BaseModel):
    name: str
    description: Optional[str] = None
    config_type: ConfigType
    settings: Dict[str, Any]
    is_active: bool = False


class SystemConfigurationCreate(SystemConfigurationBase):
    pass


class SystemConfigurationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config_type: Optional[ConfigType] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SystemConfigurationInDB(SystemConfigurationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemConfiguration(SystemConfigurationInDB):
    pass


class SystemConfigurationList(BaseModel):
    configurations: List[SystemConfiguration]
    total: int
