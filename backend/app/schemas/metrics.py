from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

class MetricBase(BaseModel):
    user_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    disk_usage: float = Field(ge=0, le=100)
    network_usage: Optional[float] = None
    process_count: Optional[int] = None
    additional_metrics: Optional[Dict] = None

class MetricCreate(MetricBase):
    pass

class MetricResponse(MetricBase):
    id: UUID

class MetricUpdate(BaseModel):
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    network_usage: Optional[float] = None
    process_count: Optional[int] = None
    additional_metrics: Optional[Dict] = None