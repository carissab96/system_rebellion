from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class StickMemoryType(str, Enum):
    """Types of memories The Stick maintains"""
    ANXIETY_PATTERN = "anxiety_pattern"
    HYPERVIGILANCE_LOG = "hypervigilance_log"
    SYSTEM_STATE = "system_state"
    AGENT_INTERACTION = "agent_interaction"
    LEARNING_PATTERN = "learning_pattern"

class StickMemoryBase(BaseModel):
    """Base memory schema for The Stick's eidetic memory system"""
    memory_type: StickMemoryType
    content: Dict[str, Any]
    context: Dict[str, Any] = Field(default_factory=dict)
    importance: int = Field(ge=1, le=10, default=5)
    tags: List[str] = Field(default_factory=list)

class StickMemoryCreate(StickMemoryBase):
    """Schema for creating new memories"""
    pass

class StickMemoryRead(StickMemoryBase):
    """Schema for reading memories with system fields"""
    id: str
    created_at: datetime
    updated_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class StickMemoryUpdate(BaseModel):
    """Schema for updating existing memories"""
    content: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    importance: Optional[int] = None
    tags: Optional[List[str]] = None

class StickMemoryQuery(BaseModel):
    """Schema for querying memories"""
    memory_types: Optional[List[StickMemoryType]] = None
    min_importance: Optional[int] = None
    tags: Optional[List[str]] = None
    time_range: Optional[tuple[datetime, datetime]] = None
    limit: int = 100
    offset: int = 0
