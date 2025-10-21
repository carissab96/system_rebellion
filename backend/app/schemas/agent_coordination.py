"""
Pydantic models for agent coordination data validation.
"""
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class CrossAgentCoordinationBase(BaseModel):
    """Base schema for cross-agent coordination events."""
    user_id: str
    primary_agent: str
    supporting_agents: Optional[Any] = None
    coordination_type: str
    coordination_success: bool = False
    coordination_details: Optional[Any] = None


class CrossAgentCoordinationCreate(CrossAgentCoordinationBase):
    """Schema for creating a new coordination event."""
    pass


class CrossAgentCoordinationRead(CrossAgentCoordinationBase):
    """Schema for reading coordination event data."""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
