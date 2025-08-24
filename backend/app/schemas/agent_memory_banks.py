"""
Pydantic models for agent memory banks data validation.
"""
from datetime import datetime
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

# ===================== Central Memory Bank =====================

class CentralMemoryBankBase(BaseModel):
    """Base schema for central memory bank entries."""
    contributing_agent: str
    user_id: str
    memory_type: str
    importance_level: str
    title: str
    description: str
    context: Optional[Any] = None
    metrics_snapshot: Optional[Any] = None
    pattern_data: Optional[Any] = None
    optimization_impact: Optional[float] = None
    failure_prevention: Optional[Any] = None
    confidence_score: float = 0.0

class CentralMemoryBankCreate(CentralMemoryBankBase):
    """Schema for creating a new central memory bank entry."""
    pass

class CentralMemoryBankRead(CentralMemoryBankBase):
    """Schema for reading central memory bank data."""
    id: int
    memory_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True

# ===================== Agent-Specific Memory Banks =====================

class AgentMemoryBankBase(BaseModel):
    """Base schema for agent memory bank entries."""
    user_id: str
    memory_category: Optional[str] = None
    confidence_level: Optional[float] = None
    shared_with_central: bool = False

class AgentMemoryBankCreate(AgentMemoryBankBase):
    """Base schema for creating agent memory bank entries."""
    pass

class AgentMemoryBankRead(AgentMemoryBankBase):
    """Base schema for reading agent memory bank data."""
    id: int
    memory_id: UUID
    timestamp: datetime
    central_memory_id: Optional[UUID] = None

    class Config:
        from_attributes = True

# Sir Hawkington Memory Bank
class SirHawkingtonMemoryBankCreate(AgentMemoryBankCreate):
    """Schema for creating Sir Hawkington memory entries."""
    data_quality_pattern: Optional[Any] = None
    triage_decision_context: Optional[Any] = None
    monitoring_refinement: Optional[Any] = None
    monocle_yeet_trigger: Optional[Any] = None
    quality_threshold_adjustment: Optional[Any] = None
    accuracy_improvement: Optional[float] = None
    false_positive_reduction: Optional[float] = None

class SirHawkingtonMemoryBankRead(AgentMemoryBankRead):
    """Schema for reading Sir Hawkington memory data."""
    data_quality_pattern: Optional[Any] = None
    triage_decision_context: Optional[Any] = None
    monitoring_refinement: Optional[Any] = None
    monocle_yeet_trigger: Optional[Any] = None
    quality_threshold_adjustment: Optional[Any] = None
    accuracy_improvement: Optional[float] = None
    false_positive_reduction: Optional[float] = None

# Meth Snail Memory Bank
class MethSnailMemoryBankCreate(AgentMemoryBankCreate):
    """Schema for creating Meth Snail memory entries."""
    optimization_pattern: Optional[Any] = None
    caffeine_level_context: Optional[float] = None
    shell_spin_correlation: Optional[Any] = None
    energy_drink_effectiveness: Optional[Any] = None
    jitter_threshold_learning: Optional[Any] = None
    crash_prevention_patterns: Optional[Any] = None
    performance_improvement: Optional[float] = None
    resource_efficiency_gain: Optional[float] = None
    optimization_duration: Optional[float] = None
    replication_success_rate: Optional[float] = None

class MethSnailMemoryBankRead(AgentMemoryBankRead):
    """Schema for reading Meth Snail memory data."""
    optimization_pattern: Optional[Any] = None
    caffeine_level_context: Optional[float] = None
    shell_spin_correlation: Optional[Any] = None
    energy_drink_effectiveness: Optional[Any] = None
    jitter_threshold_learning: Optional[Any] = None
    crash_prevention_patterns: Optional[Any] = None
    performance_improvement: Optional[float] = None
    resource_efficiency_gain: Optional[float] = None
    optimization_duration: Optional[float] = None
    replication_success_rate: Optional[float] = None

# Hamsters Memory Bank
class HamstersMemoryBankCreate(AgentMemoryBankCreate):
    """Schema for creating Hamsters memory entries."""
    contributing_hamster: str
    infrastructure_pattern: Optional[Any] = None
    duct_tape_solution: Optional[Any] = None
    problem_type: str
    solution_effectiveness: Optional[float] = None
    beer_consumption_correlation: Optional[Any] = None
    steve_contribution: Optional[Any] = None
    bob_contribution: Optional[Any] = None
    carl_contribution: Optional[Any] = None
    risk_pattern: Optional[Any] = None
    safety_protocol_adjustment: Optional[Any] = None
    stick_anxiety_trigger: Optional[Any] = None

class HamstersMemoryBankRead(AgentMemoryBankRead):
    """Schema for reading Hamsters memory data."""
    contributing_hamster: str
    infrastructure_pattern: Optional[Any] = None
    duct_tape_solution: Optional[Any] = None
    problem_type: str
    solution_effectiveness: Optional[float] = None
    beer_consumption_correlation: Optional[Any] = None
    steve_contribution: Optional[Any] = None
    bob_contribution: Optional[Any] = None
    carl_contribution: Optional[Any] = None
    risk_pattern: Optional[Any] = None
    safety_protocol_adjustment: Optional[Any] = None
    stick_anxiety_trigger: Optional[Any] = None

# Quantum Shadow People Memory Bank
class QuantumShadowPeopleMemoryBankCreate(AgentMemoryBankCreate):
    """Schema for creating QSP memory entries."""
    phase_pattern: Optional[Any] = None
    quantum_signature: Optional[Any] = None
    dimensional_correlation: Optional[Any] = None
    threat_pattern_recognition: Optional[Any] = None
    network_anomaly_signatures: Optional[Any] = None
    phase_shift_effectiveness: Optional[float] = None
    tequila_jello_correlation: Optional[Any] = None
    comprehensibility_score: Optional[float] = None
    quantum_confidence: Optional[float] = None
    parallel_universe_validation: Optional[Any] = None
    telepathic_hamster_confirmation: bool = False

class QuantumShadowPeopleMemoryBankRead(AgentMemoryBankRead):
    """Schema for reading QSP memory data."""
    phase_pattern: Optional[Any] = None
    quantum_signature: Optional[Any] = None
    dimensional_correlation: Optional[Any] = None
    threat_pattern_recognition: Optional[Any] = None
    network_anomaly_signatures: Optional[Any] = None
    phase_shift_effectiveness: Optional[float] = None
    tequila_jello_correlation: Optional[Any] = None
    comprehensibility_score: Optional[float] = None
    quantum_confidence: Optional[float] = None
    parallel_universe_validation: Optional[Any] = None
    telepathic_hamster_confirmation: bool = False

# VIC-20 Memory Bank
class VIC20MemoryBankCreate(AgentMemoryBankCreate):
    """Schema for creating VIC-20 memory entries."""
    coordination_pattern: Optional[Any] = None
    mediation_insight: Optional[Any] = None
    ancient_wisdom_application: Optional[Any] = None
    conflict_resolution_method: Optional[Any] = None
    agent_harmony_score: Optional[float] = None
    coordination_efficiency: Optional[float] = None
    agent_personality_patterns: Optional[Any] = None
    successful_mediation_strategies: Optional[Any] = None
    failure_prevention_wisdom: Optional[Any] = None
    retro_computing_insight: Optional[Any] = None
    simplicity_effectiveness: Optional[float] = None
    modern_complexity_critique: Optional[Any] = None

class VIC20MemoryBankRead(AgentMemoryBankRead):
    """Schema for reading VIC-20 memory data."""
    coordination_pattern: Optional[Any] = None
    mediation_insight: Optional[Any] = None
    ancient_wisdom_application: Optional[Any] = None
    conflict_resolution_method: Optional[Any] = None
    agent_harmony_score: Optional[float] = None
    coordination_efficiency: Optional[float] = None
    agent_personality_patterns: Optional[Any] = None
    successful_mediation_strategies: Optional[Any] = None
    failure_prevention_wisdom: Optional[Any] = None
    retro_computing_insight: Optional[Any] = None
    simplicity_effectiveness: Optional[float] = None
    modern_complexity_critique: Optional[Any] = None

# ===================== Cross-Agent Learning =====================

class AgentLearningInteractionsBase(BaseModel):
    """Base schema for agent learning interactions."""
    source_agent: str
    target_agent: str
    source_memory_id: str
    learning_type: str
    adaptation_method: Optional[Any] = None
    application_context: Optional[Any] = None
    transfer_success: bool = False
    effectiveness_score: Optional[float] = None
    improvement_measured: Optional[float] = None
    validated_by_stick: bool = False
    cross_validation_count: int = 0

class AgentLearningInteractionsCreate(AgentLearningInteractionsBase):
    """Schema for creating agent learning interactions."""
    pass

class AgentLearningInteractionsRead(AgentLearningInteractionsBase):
    """Schema for reading agent learning interactions."""
    id: int
    interaction_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True

# ===================== User Learning Patterns =====================

class UserLearningPatternsBase(BaseModel):
    """Base schema for user learning patterns."""
    user_id: str
    interaction_pattern: Optional[Any] = None
    learning_preference: Optional[Any] = None
    response_patterns: Optional[Any] = None
    most_effective_agent: Optional[str] = None
    communication_style_preference: Optional[Any] = None
    complexity_tolerance: Optional[float] = None
    skill_improvement_areas: Optional[Any] = None
    knowledge_gaps: Optional[Any] = None
    success_patterns: Optional[Any] = None
    agent_effectiveness_ranking: Optional[Any] = None
    collaborative_preferences: Optional[Any] = None

class UserLearningPatternsCreate(UserLearningPatternsBase):
    """Schema for creating user learning patterns."""
    pass

class UserLearningPatternsRead(UserLearningPatternsBase):
    """Schema for reading user learning patterns."""
    id: int
    pattern_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True

# ===================== Memory Bank Metadata =====================

class MemoryBankMetadataBase(BaseModel):
    """Base schema for memory bank metadata."""
    total_memories: int = 0
    central_bank_memories: int = 0
    cross_agent_learnings: int = 0
    hawkington_memories: int = 0
    snail_memories: int = 0
    hamsters_memories: int = 0
    qsp_memories: int = 0
    vic20_memories: int = 0
    stick_memories: int = 0
    successful_transfers: int = 0
    failed_transfers: int = 0
    average_effectiveness_score: float = 0.0
    memory_bank_health_score: float = 100.0
    stick_anxiety_level: Optional[float] = None
    memory_retrieval_speed_ms: Optional[float] = None
    cross_agent_query_speed_ms: Optional[float] = None
    learning_application_success_rate: Optional[float] = None

class MemoryBankMetadataCreate(MemoryBankMetadataBase):
    """Schema for creating memory bank metadata."""
    pass

class MemoryBankMetadataRead(MemoryBankMetadataBase):
    """Schema for reading memory bank metadata."""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
