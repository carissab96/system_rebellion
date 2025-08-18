from pydantic import BaseModel
from typing import Any
from datetime import datetime

class AgentDecisionBase(BaseModel):
    user_id: str
    agent_name: str
    decision: str
    context: Any  # could be dict/JSON depending on model

class AgentDecisionCreate(AgentDecisionBase):
    pass

class AgentDecisionRead(AgentDecisionBase):
    id: str
    timestamp: datetime

    class Config:
        orm_mode = True
