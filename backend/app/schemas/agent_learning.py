#!/usr/bin/env python3
"""
Agent Learning Records Schemas

Pydantic schemas for agent learning records API validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AgentLearningRecordBase(BaseModel):
    """Base schema for agent learning records"""
    agent_name: str = Field(..., max_length=50, description="Name of the agent")
    
    # Hierarchical fingerprints
    fingerprint_l1: str = Field(..., max_length=50, description="Level 1 fingerprint (broad)")
    fingerprint_l2: str = Field(..., max_length=100, description="Level 2 fingerprint (medium)")
    fingerprint_l3: str = Field(..., max_length=150, description="Level 3 fingerprint (specific)")
    
    # Situation context
    resource_type: str = Field(..., max_length=20, description="Resource type: cpu, memory, disk, network")
    severity: str = Field(..., max_length=20, description="Severity: low, medium, high, critical")
    root_cause: Optional[str] = Field(None, max_length=50, description="Root cause of the issue")
    process_category: Optional[str] = Field(None, max_length=20, description="Process category: python, database, web_server, system, other")
    
    # Action taken
    action: str = Field(..., max_length=100, description="Action taken")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Action parameters")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in the action")
    followed_vic20: bool = Field(False, description="Whether VIC-20's recommendation was followed")
    
    # Outcome
    success: bool = Field(..., description="Whether the action was successful")
    improvement: Optional[Dict[str, float]] = Field(None, description="Metrics improvement deltas")
    what_worked: Optional[str] = Field(None, description="What worked in this situation")
    what_failed: Optional[str] = Field(None, description="What failed in this situation")


class AgentLearningRecordCreate(AgentLearningRecordBase):
    """Schema for creating a new learning record"""
    pass


class AgentLearningRecordUpdate(BaseModel):
    """Schema for updating a learning record (partial updates allowed)"""
    success: Optional[bool] = None
    improvement: Optional[Dict[str, float]] = None
    what_worked: Optional[str] = None
    what_failed: Optional[str] = None


class AgentLearningRecordResponse(AgentLearningRecordBase):
    """Schema for learning record responses"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentLearningQuery(BaseModel):
    """Schema for querying learning records"""
    agent_name: Optional[str] = None
    fingerprint_l1: Optional[str] = None
    fingerprint_l2: Optional[str] = None
    fingerprint_l3: Optional[str] = None
    resource_type: Optional[str] = None
    severity: Optional[str] = None
    process_category: Optional[str] = None
    action: Optional[str] = None
    success: Optional[bool] = None
    limit: int = Field(20, ge=1, le=100, description="Maximum number of records to return")


class AgentLearningStats(BaseModel):
    """Schema for learning statistics"""
    agent_name: str
    total_records: int
    success_rate: float
    actions_by_type: Dict[str, int]
    most_successful_action: Optional[str] = None
    most_failed_action: Optional[str] = None
    learning_by_fingerprint: Dict[str, Dict[str, Any]]


class SituationFingerprints(BaseModel):
    """Schema for situation fingerprints"""
    level_1: str = Field(..., description="Broad fingerprint")
    level_2: str = Field(..., description="Medium fingerprint")
    level_3: str = Field(..., description="Specific fingerprint")
    process_category: str = Field(..., description="Process category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "level_1": "cpu_high",
                "level_2": "cpu_high_memory_thrashing",
                "level_3": "cpu_high_memory_thrashing_python",
                "process_category": "python"
            }
        }
