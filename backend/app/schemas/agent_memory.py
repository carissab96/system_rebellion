from pydantic import BaseModel, Field, validator
from typing import Any, Optional, List, Dict, Union
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

# ============================================================================
# Base Memory Models
# ============================================================================

class MemoryCategory(str, Enum):
    """Categories for organizing different types of memories"""
    OBSERVATION = "observation"
    DECISION = "decision"
    PATTERN = "pattern"
    PREFERENCE = "preference"
    INCIDENT = "incident"
    LEARNING = "learning"
    COORDINATION = "coordination"
    PERFORMANCE = "performance"

class MemoryPriority(int, Enum):
    """Priority levels for memories"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class AgentMemoryBase(BaseModel):
    """Base model for all agent memories"""
    user_id: str = Field(..., description="ID of the user this memory belongs to")
    agent_name: str = Field(..., description="Name of the agent this memory is associated with")
    memory_type: str = Field(..., description="Type/category of the memory")
    content: Dict[str, Any] = Field(..., description="The actual memory content as a dictionary")
    importance: MemoryPriority = Field(default=MemoryPriority.MEDIUM, description="Importance level of this memory")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Additional context about when/where this memory was formed"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorizing and searching memories"
    )
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# ============================================================================
# Memory CRUD Schemas
# ============================================================================

class AgentMemoryCreate(AgentMemoryBase):
    """Schema for creating a new memory"""
    memory_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentMemoryUpdate(BaseModel):
    """Schema for updating an existing memory"""
    content: Optional[Dict[str, Any]] = None
    importance: Optional[MemoryPriority] = None
    context: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class AgentMemoryInDB(AgentMemoryBase):
    """Schema for memory as stored in the database"""
    id: int = Field(..., description="Database primary key")
    memory_id: str = Field(..., description="Public UUID for the memory")
    timestamp: datetime = Field(..., description="When the memory was created")
    last_accessed: Optional[datetime] = Field(
        None, 
        description="When the memory was last accessed"
    )
    access_count: int = Field(
        default=0,
        description="Number of times this memory has been accessed"
    )
    version: int = Field(
        default=1,
        description="Version number for optimistic concurrency control"
    )
    
    class Config:
        orm_mode = True

class AgentMemoryResponse(AgentMemoryInDB):
    """Schema for memory as returned in API responses"""
    pass

# ============================================================================
# Memory Bank Schemas
# ============================================================================

class MemoryBankBase(BaseModel):
    """Base model for memory banks"""
    name: str = Field(..., description="Name of the memory bank")
    description: Optional[str] = Field(
        None,
        description="Description of what this memory bank is used for"
    )
    agent_name: str = Field(
        ...,
        description="Name of the agent this memory bank belongs to"
    )
    is_shared: bool = Field(
        default=False,
        description="Whether this memory bank is shared across agents"
    )
    capacity: Optional[int] = Field(
        None,
        description="Maximum number of memories this bank can hold (None for unlimited)"
    )
    
    class Config:
        use_enum_values = True

class MemoryBankCreate(MemoryBankBase):
    """Schema for creating a new memory bank"""
    pass

class MemoryBankUpdate(BaseModel):
    """Schema for updating a memory bank"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_shared: Optional[bool] = None
    capacity: Optional[int] = None

class MemoryBankInDB(MemoryBankBase):
    """Schema for memory bank as stored in the database"""
    id: int = Field(..., description="Database primary key")
    user_id: str = Field(..., description="ID of the user who owns this memory bank")
    created_at: datetime = Field(..., description="When the memory bank was created")
    updated_at: datetime = Field(..., description="When the memory bank was last updated")
    memory_count: int = Field(
        default=0,
        description="Current number of memories in this bank"
    )
    
    class Config:
        orm_mode = True

class MemoryBankResponse(MemoryBankInDB):
    """Schema for memory bank as returned in API responses"""
    pass

# ============================================================================
# Central Memory Schemas
# ============================================================================

class CentralMemoryCreate(AgentMemoryCreate):
    """Schema for creating a memory in the central memory bank"""
    source_agent: str = Field(
        ...,
        description="Name of the agent that created this memory"
    )
    source_memory_id: Optional[str] = Field(
        None,
        description="ID of the original memory in the agent's memory bank"
    )
    relevance_score: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Relevance score for cross-agent sharing"
    )

class CentralMemoryUpdate(AgentMemoryUpdate):
    """Schema for updating a memory in the central memory bank"""
    relevance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Updated relevance score for cross-agent sharing"
    )

class CentralMemoryResponse(AgentMemoryResponse):
    """Schema for central memory as returned in API responses"""
    source_agent: str
    source_memory_id: Optional[str]
    relevance_score: float
    
    class Config:
        orm_mode = True
