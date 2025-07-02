from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

class MetricBase(BaseModel):
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    disk_usage: float = Field(ge=0, le=100)
    network: Optional[Dict] = None  # Change network_usage to network with Dict type
    process_count: Optional[int] = None
    additional_metrics: Optional[Dict] = None

class MetricCreate(MetricBase):
    pass

class MetricResponse(MetricBase):
    id: int

class MetricUpdate(BaseModel):
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    network: Optional[float] = None
    process_count: Optional[int] = None
    additional_metrics: Optional[Dict] = None