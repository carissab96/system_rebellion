from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
