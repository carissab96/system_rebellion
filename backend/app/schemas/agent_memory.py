from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class AgentMemoryBase(BaseModel):
    user_id: str
    agent_name: str
    memory_type: str   # 'incident', 'pattern', 'preference', etc.
    content: Any
    importance: int

class AgentMemoryCreate(AgentMemoryBase):
    """Used when inserting new memory rows"""
    pass

class AgentMemoryRead(AgentMemoryBase):
    id: str
    timestamp: datetime
    last_accessed: Optional[datetime] = None
    access_count: int

    class Config:
        orm_mode = True  # allows SQLAlchemy → Pydantic conversion
