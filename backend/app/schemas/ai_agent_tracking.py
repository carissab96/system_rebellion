"""
Pydantic models for AI agent tracking data validation.
"""
from datetime import datetime
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

# ===================== AI Agent Metrics =====================

class AIAgentMetricsBase(BaseModel):
    """Base schema for AI agent metrics."""
    user_id: Optional[str] = None
    agent_name: str
    decision_type: Optional[str] = None
    decision_confidence: Optional[float] = None
    decision_rationale: Optional[str] = None
    actions_taken: Optional[Any] = None
    estimated_impact: Optional[Any] = None
    urgency_level: Optional[str] = None
    data_quality_score: Optional[float] = None
    missing_metrics: Optional[Any] = None
    invalid_metrics: Optional[Any] = None
    incident_count: int = 0
    incident_type: Optional[str] = None
    incident_reason: Optional[str] = None
    analysis_duration_ms: Optional[int] = None
    successful_analysis: bool = True
    analysis_depth: Optional[str] = None
    agent_version: Optional[str] = None

class AIAgentMetricsCreate(AIAgentMetricsBase):
    """Schema for creating AI agent metrics."""
    pass

class AIAgentMetricsRead(AIAgentMetricsBase):
    """Schema for reading AI agent metrics."""
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# ===================== Agent-Specific Incident Tracking =====================

class AgentIncidentBase(BaseModel):
    """Base schema for agent incidents."""
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    hour_start: Optional[datetime] = None
    date: Optional[datetime] = None

# Meth Snail Shell Spins
class MethSnailShellSpinsCreate(AgentIncidentBase):
    """Schema for creating Meth Snail shell spin incidents."""
    spin_duration_ms: int
    optimization_attempted: str
    optimization_success: bool
    jitter_level: float
    system_load: Optional[Any] = None
    caffeine_level_mg: float
    memory_usage: float
    cpu_usage: float
    network_io: Optional[Any] = None
    error_message: Optional[str] = None

class MethSnailShellSpinsRead(AgentIncidentBase):
    """Schema for reading Meth Snail shell spin incidents."""
    id: int
    spin_duration_ms: int
    optimization_attempted: str
    optimization_success: bool
    jitter_level: float
    system_load: Optional[Any] = None
    caffeine_level_mg: float
    memory_usage: float
    cpu_usage: float
    network_io: Optional[Any] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Sir Hawkington Monocle Yeets
class SirHawkingtonMonocleYeetsCreate(AgentIncidentBase):
    """Schema for creating Sir Hawkington monocle yeet incidents."""
    yeet_trigger: str
    yeet_intensity: str
    system_state: Optional[Any] = None
    expected_behavior: Optional[Any] = None
    actual_behavior: Optional[Any] = None
    concern_level: Optional[str] = None

class SirHawkingtonMonocleYeetsRead(AgentIncidentBase):
    """Schema for reading Sir Hawkington monocle yeet incidents."""
    id: int
    yeet_trigger: str
    yeet_intensity: str
    system_state: Optional[Any] = None
    expected_behavior: Optional[Any] = None
    actual_behavior: Optional[Any] = None
    concern_level: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# The Stick Hyperventilations
class TheStickHyperventilationsCreate(AgentIncidentBase):
    """Schema for creating The Stick hyperventilation incidents."""
    anxiety_trigger: str
    anxiety_level: str
    compliance_issue: Optional[Any] = None
    policy_violated: Optional[str] = None
    risk_assessment: Optional[Any] = None
    recommended_actions: Optional[Any] = None
    paper_bags_used: int = 1
    recovery_time_seconds: Optional[int] = None

class TheStickHyperventilationsRead(AgentIncidentBase):
    """Schema for reading The Stick hyperventilation incidents."""
    id: int
    anxiety_trigger: str
    anxiety_level: str
    compliance_issue: Optional[Any] = None
    policy_violated: Optional[str] = None
    risk_assessment: Optional[Any] = None
    recommended_actions: Optional[Any] = None
    paper_bags_used: int = 1
    recovery_time_seconds: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# Quantum Shadow Phasings
class QuantumShadowPhasingsCreate(AgentIncidentBase):
    """Schema for creating Quantum Shadow Phasing incidents."""
    phase_type: str
    phase_reason: Optional[str] = None
    destination_dimension: Optional[str] = None
    network_issue: Optional[Any] = None
    quantum_solution: Optional[Any] = None
    router_status: Optional[str] = None
    solution_comprehensibility: Optional[float] = None
    effectiveness_rating: Optional[float] = None

class QuantumShadowPhasingsRead(AgentIncidentBase):
    """Schema for reading Quantum Shadow Phasing incidents."""
    id: int
    phase_type: str
    phase_reason: Optional[str] = None
    destination_dimension: Optional[str] = None
    network_issue: Optional[Any] = None
    quantum_solution: Optional[Any] = None
    router_status: Optional[str] = None
    solution_comprehensibility: Optional[float] = None
    effectiveness_rating: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

# VIC20 Wisdom
class VIC20WisdomCreate(AgentIncidentBase):
    """Schema for creating VIC20 wisdom entries."""
    wisdom_type: str
    wisdom_content: str
    relevance_score: Optional[float] = None
    problem_addressed: Optional[str] = None
    historical_reference: Optional[str] = None
    wisdom_followed: Optional[bool] = None
    outcome_success: Optional[bool] = None

class VIC20WisdomRead(AgentIncidentBase):
    """Schema for reading VIC20 wisdom entries."""
    id: int
    wisdom_type: str
    wisdom_content: str
    relevance_score: Optional[float] = None
    problem_addressed: Optional[str] = None
    historical_reference: Optional[str] = None
    wisdom_followed: Optional[bool] = None
    outcome_success: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
