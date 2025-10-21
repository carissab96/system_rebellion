from pydantic import BaseModel
from typing import Any
from datetime import datetime

class AgentGlobalPatternBase(BaseModel):
    agent_name: str
    pattern_key: str
    value: Any

class AgentGlobalPatternCreate(AgentGlobalPatternBase):
    pass

class AgentGlobalPatternRead(AgentGlobalPatternBase):
    updated_at: datetime

    class Config:
        from_attributes = True
