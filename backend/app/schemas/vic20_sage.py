from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SageWisdomType(str, Enum):
    """Types of wisdom VIC-20 Sage maintains"""
    ANCIENT_WISDOM = "ancient_wisdom"
    COORDINATION_PATTERN = "coordination_pattern"
    CONFLICT_RESOLUTION = "conflict_resolution"
    SYSTEM_HARMONY = "system_harmony"
    AGENT_MEDIATION = "agent_mediation"

class SageWisdomBase(BaseModel):
    """Base wisdom schema for VIC-20 Sage's ancient knowledge system"""
    wisdom_type: SageWisdomType
    title: str
    content: str
    context: Dict[str, Any] = Field(default_factory=dict)
    relevance: int = Field(ge=1, le=10, default=5)
    tags: List[str] = Field(default_factory=list)
    related_agents: List[str] = Field(default_factory=list)

class SageWisdomCreate(SageWisdomBase):
    """Schema for creating new wisdom entries"""
    pass

class SageWisdomRead(SageWisdomBase):
    """Schema for reading wisdom entries with system fields"""
    id: str
    created_at: datetime
    updated_at: datetime
    applied_count: int = 0
    last_applied: Optional[datetime] = None
    effectiveness: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class SageWisdomUpdate(BaseModel):
    """Schema for updating wisdom entries"""
    title: Optional[str] = None
    content: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    relevance: Optional[int] = None
    tags: Optional[List[str]] = None
    related_agents: Optional[List[str]] = None
    effectiveness: Optional[float] = None

class SageWisdomQuery(BaseModel):
    """Schema for querying wisdom entries"""
    wisdom_types: Optional[List[SageWisdomType]] = None
    min_relevance: Optional[int] = None
    tags: Optional[List[str]] = None
    related_agents: Optional[List[str]] = None
    time_range: Optional[tuple[datetime, datetime]] = None
    limit: int = 100
    offset: int = 0
