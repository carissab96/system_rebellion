from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class AlertSeverity(str, Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'


class SystemAlertBase(BaseModel):
    title: str
    message: str
    severity: AlertSeverity = AlertSeverity.MEDIUM
    additional_data: Optional[Dict[str, Any]] = None
    is_read: bool = False


class SystemAlertCreate(SystemAlertBase):
    pass


class SystemAlertUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    additional_data: Optional[Dict[str, Any]] = None
    is_read: Optional[bool] = None


class SystemAlertInDB(SystemAlertBase):
    id: UUID
    user_id: UUID
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SystemAlert(SystemAlertInDB):
    pass


class SystemAlertList(BaseModel):
    alerts: List[SystemAlert]
    total: int
