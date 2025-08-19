# Agent Memory Banks - Persistent Learning Architecture
# System Rebellion AI Agent Memory System

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from sqlalchemy.ext.declarative import declarative_base
from app.core.base import Base
Base = declarative_base() 

# ============================================================================
# CENTRAL MEMORY BANK - The Stick's Eidetic Memory Hub
# ============================================================================

class CentralMemoryBank(Base):
    """
    The Stick's Eidetic Memory - Central hub for all agent learning
    
    This is where all agents contribute their learnings and can access
    cross-agent insights. The Stick's anxiety-driven hypervigilance makes
    it the perfect central coordinator for persistent memory.
    """
    __tablename__ = 'central_memory_bank'
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Source information
    contributing_agent = Column(String(50), nullable=False, index=True)  # Which agent contributed this
    user_id = Column(String(255), nullable=False, index=True)
    
    # Memory classification
    memory_type = Column(String(100), nullable=False, index=True)  # pattern, optimization, failure, success, etc.
    importance_level = Column(String(20), nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL, EIDETIC
    confidence_score = Column(Float, default=0.0)  # How confident the agent is about this learning
    
    # Memory content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    context = Column(JSON)  # System context when this was learned
    metrics_snapshot = Column(JSON)  # Relevant metrics at the time
    
    # Learning metadata
    pattern_data = Column(JSON)  # Structured pattern information
    optimization_impact = Column(Float)  # Measured improvement from this learning
    failure_prevention = Column(JSON)  # What this prevents from happening again
    
    # Cross-agent relevance
    relevant_agents = Column(String(255))  # Comma-separated list of agents this applies to
    cross_agent_validated = Column(Boolean, default=False)  # Has another agent confirmed this?
    validation_count = Column(Integer, default=0)
    
    # Stick's anxiety tracking
    stick_anxiety_level = Column(Float)  # The Stick's anxiety when this was recorded
    never_forget = Column(Boolean, default=False)  # Eidetic memory flag
    
    # Usage tracking
    times_referenced = Column(Integer, default=0)
    last_referenced = Column(DateTime)
    successful_applications = Column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_memory_importance', 'importance_level', 'never_forget'),
        Index('idx_agent_memories', 'contributing_agent', 'memory_type'),
        Index('idx_user_memories', 'user_id', 'timestamp'),
        Index('idx_cross_agent', 'relevant_agents', 'cross_agent_validated'),
    )

# ============================================================================
# INDIVIDUAL AGENT MEMORY BANKS
# ============================================================================

class SirHawkingtonMemoryBank(Base):
    """
    Sir Hawkington's Distinguished Memory Bank
    
    Focuses on data quality patterns, triage decisions, and aristocratic
    monitoring insights. Tracks monocle-yeeting triggers and refinement.
    """
    __tablename__ = 'sir_hawkington_memory_bank'
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Hawkington-specific memory types
    memory_category = Column(String(50), nullable=False, index=True)  # triage, quality, monocle_yeet, etc.
    data_quality_pattern = Column(JSON)  # Patterns in data quality issues
    triage_decision_context = Column(JSON)  # Context for triage routing decisions
    
    # Aristocratic insights
    monitoring_refinement = Column(JSON)  # How monitoring was improved
    monocle_yeet_trigger = Column(JSON)  # What caused the monocle yeet
    quality_threshold_adjustment = Column(JSON)  # Learned threshold adjustments
    
    # Performance tracking
    accuracy_improvement = Column(Float)  # Measured improvement in accuracy
    false_positive_reduction = Column(Float)  # Reduction in false alerts
    
    # Cross-agent coordination
    shared_with_central = Column(Boolean, default=False)
    central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
    __table_args__ = (
        Index('idx_hawkington_category', 'memory_category', 'timestamp'),
        Index('idx_hawkington_shared', 'shared_with_central', 'central_memory_id'),
    )

class MethSnailMemoryBank(Base):
    """
    Meth Snail's Caffeinated Memory Bank
    
    Tracks optimization patterns, energy drink effectiveness, and shell-spinning
    insights. Learns from caffeine-fueled optimization sessions.
    """
    __tablename__ = 'meth_snail_memory_bank'
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Snail-specific memory types
    optimization_pattern = Column(JSON)  # Learned optimization patterns
    caffeine_level_context = Column(Float)  # Caffeine level when learning occurred
    shell_spin_correlation = Column(JSON)  # Correlation between spinning and performance
    
    # Energy drink insights
    energy_drink_effectiveness = Column(JSON)  # Which drinks work best for what
    jitter_threshold_learning = Column(JSON)  # Optimal jitter levels for different tasks
    crash_prevention_patterns = Column(JSON)  # How to avoid caffeine crashes
    
    # Optimization results
    performance_improvement = Column(Float)  # Measured performance gain
    resource_efficiency_gain = Column(Float)  # Resource usage improvement
    optimization_duration = Column(Float)  # How long the optimization took
    
    # Learning metadata
    confidence_level = Column(Float)  # How confident about this optimization
    replication_success_rate = Column(Float)  # Success rate when applied elsewhere
    
    # Cross-agent coordination
    shared_with_central = Column(Boolean, default=False)
    central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
    __table_args__ = (
        Index('idx_snail_optimization', 'optimization_pattern', 'performance_improvement'),
        Index('idx_snail_caffeine', 'caffeine_level_context', 'timestamp'),
    )

class HamstersMemoryBank(Base):
    """
    Hamsters Collective Memory Bank (Steve, Bob, and Carl)
    
    Tracks infrastructure patterns, duct tape solutions, and beer-fueled
    engineering insights. Includes individual and collective learnings.
    """
    __tablename__ = 'hamsters_memory_bank'
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Hamster-specific memory
    contributing_hamster = Column(String(10), nullable=False, index=True)  # steve, bob, carl, or collective
    infrastructure_pattern = Column(JSON)  # Infrastructure-related patterns
    duct_tape_solution = Column(JSON)  # Duct tape engineering solutions
    
    # Engineering insights
    problem_type = Column(String(100), nullable=False, index=True)  # disk, hardware, mystery, etc.
    solution_effectiveness = Column(Float)  # How well the solution worked
    beer_consumption_correlation = Column(JSON)  # Beer levels vs solution quality
    
    # Individual hamster contributions
    steve_contribution = Column(JSON)  # Steve's careful measurements
    bob_contribution = Column(JSON)  # Bob's wild ideas and supply raids
    carl_contribution = Column(JSON)  # Carl's duct tape calculations
    
    # Risk assessment learning
    risk_pattern = Column(JSON)  # Learned risk patterns
    safety_protocol_adjustment = Column(JSON)  # Safety improvements
    stick_anxiety_trigger = Column(JSON)  # What causes The Stick anxiety
    
    # Cross-agent coordination
    shared_with_central = Column(Boolean, default=False)
    central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
    __table_args__ = (
        Index('idx_hamsters_contributor', 'contributing_hamster', 'problem_type'),
        Index('idx_hamsters_effectiveness', 'solution_effectiveness', 'timestamp'),
    )

class QuantumShadowPeopleMemoryBank(Base):
    """
    Quantum Shadow People's Incomprehensible Memory Bank
    
    Tracks network security patterns, phase-shift insights, and quantum
    threat detection. Deliberately cryptic but functionally effective.
    """
    __tablename__ = 'quantum_shadow_people_memory_bank'
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # QSP-specific memory (deliberately cryptic)
    phase_pattern = Column(JSON)  # Network phase patterns
    quantum_signature = Column(JSON)  # Quantum threat signatures
    dimensional_correlation = Column(JSON)  # Multi-dimensional security correlations
    
    # Security insights
    threat_pattern_recognition = Column(JSON)  # Learned threat patterns
    network_anomaly_signatures = Column(JSON)  # Network anomaly patterns
    phase_shift_effectiveness = Column(Float)  # Effectiveness of phase shifts
    
    # Incomprehensible but functional data
    tequila_jello_correlation = Column(JSON)  # Mysterious but effective correlations
    comprehensibility_score = Column(Float)  # How incomprehensible this is (lower = better)
    quantum_confidence = Column(Float)  # Quantum confidence level
    
    # Cross-dimensional learning
    parallel_universe_validation = Column(JSON)  # Validation from other dimensions
    telepathic_hamster_confirmation = Column(Boolean, default=False)  # Hamster telepathy confirmation
    
    # Cross-agent coordination
    shared_with_central = Column(Boolean, default=False)
    central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
    __table_args__ = (
        Index('idx_qsp_phase', 'phase_pattern', 'quantum_confidence'),
        Index('idx_qsp_comprehensibility', 'comprehensibility_score', 'phase_shift_effectiveness'),
    )

class VIC20MemoryBank(Base):
    """
    VIC-20's Ancient Wisdom Memory Bank
    
    Tracks coordination patterns, mediation insights, and ancient computing
    wisdom. Learns from conflicts and successful coordinations.
    """
    __tablename__ = 'vic20_memory_bank'
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # VIC-20 specific memory
    coordination_pattern = Column(JSON)  # Agent coordination patterns
    mediation_insight = Column(JSON)  # Conflict mediation learnings
    ancient_wisdom_application = Column(JSON)  # How ancient wisdom applies
    
    # Coordination learning
    conflict_resolution_method = Column(JSON)  # Successful conflict resolutions
    agent_harmony_score = Column(Float)  # Measured harmony improvement
    coordination_efficiency = Column(Float)  # Coordination efficiency gains
    
    # Mediation insights
    agent_personality_patterns = Column(JSON)  # Learned agent personality patterns
    successful_mediation_strategies = Column(JSON)  # What mediation strategies work
    failure_prevention_wisdom = Column(JSON)  # Ancient wisdom for preventing failures
    
    # 8-bit wisdom
    retro_computing_insight = Column(JSON)  # Insights from ancient computing
    simplicity_effectiveness = Column(Float)  # How effective simple solutions are
    modern_complexity_critique = Column(JSON)  # Critiques of modern overcomplexity
    
    # Cross-agent coordination
    shared_with_central = Column(Boolean, default=False)
    central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
    __table_args__ = (
        Index('idx_vic20_coordination', 'coordination_pattern', 'agent_harmony_score'),
        Index('idx_vic20_mediation', 'mediation_insight', 'coordination_efficiency'),
    )

# ============================================================================
# CROSS-AGENT LEARNING TABLES
# ============================================================================

class AgentLearningInteractions(Base):
    """
    Track how agents learn from each other's experiences
    
    This table captures when one agent's learning influences another agent's
    behavior, creating the cross-pollination of insights that makes the
    system truly intelligent.
    """
    __tablename__ = 'agent_learning_interactions'
    
    id = Column(Integer, primary_key=True)
    interaction_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Learning transfer
    source_agent = Column(String(50), nullable=False, index=True)  # Agent that shared knowledge
    target_agent = Column(String(50), nullable=False, index=True)  # Agent that learned
    source_memory_id = Column(String(36), nullable=False)  # Original memory
    
    # Transfer details
    learning_type = Column(String(100), nullable=False)  # pattern, optimization, failure, etc.
    adaptation_method = Column(JSON)  # How the learning was adapted
    application_context = Column(JSON)  # Context where it was applied
    
    # Effectiveness tracking
    transfer_success = Column(Boolean, default=False)
    effectiveness_score = Column(Float)  # How effective the transferred learning was
    improvement_measured = Column(Float)  # Measured improvement from the transfer
    
    # Validation
    validated_by_stick = Column(Boolean, default=False)  # The Stick's validation
    cross_validation_count = Column(Integer, default=0)  # How many agents confirmed this
    
    __table_args__ = (
        Index('idx_learning_transfer', 'source_agent', 'target_agent', 'learning_type'),
        Index('idx_learning_effectiveness', 'effectiveness_score', 'transfer_success'),
    )

class UserLearningPatterns(Base):
    """
    Track patterns in how users interact with agents and learn from the system
    
    This enables the agents to adapt their behavior based on user learning
    patterns and preferences, creating truly personalized AI interactions.
    """
    __tablename__ = 'user_learning_patterns'
    
    id = Column(Integer, primary_key=True)
    pattern_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # User behavior patterns
    interaction_pattern = Column(JSON)  # How user interacts with agents
    learning_preference = Column(JSON)  # User's learning preferences
    response_patterns = Column(JSON)  # How user responds to different approaches
    
    # Agent adaptation
    most_effective_agent = Column(String(50))  # Which agent works best for this user
    communication_style_preference = Column(JSON)  # Preferred communication style
    complexity_tolerance = Column(Float)  # User's tolerance for complexity
    
    # Learning outcomes
    skill_improvement_areas = Column(JSON)  # Areas where user is improving
    knowledge_gaps = Column(JSON)  # Identified knowledge gaps
    success_patterns = Column(JSON)  # What leads to user success
    
    # Cross-agent insights
    agent_effectiveness_ranking = Column(JSON)  # How effective each agent is for this user
    collaborative_preferences = Column(JSON)  # Preferred agent collaborations
    
    __table_args__ = (
        Index('idx_user_patterns', 'user_id', 'most_effective_agent'),
        Index('idx_user_learning', 'learning_preference', 'complexity_tolerance'),
    )

# ============================================================================
# MEMORY BANK MANAGEMENT
# ============================================================================

class MemoryBankMetadata(Base):
    """
    Metadata about the memory bank system itself
    
    Tracks system-wide learning statistics, memory bank health,
    and cross-agent learning effectiveness.
    """
    __tablename__ = 'memory_bank_metadata'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # System-wide statistics
    total_memories = Column(Integer, default=0)
    central_bank_memories = Column(Integer, default=0)
    cross_agent_learnings = Column(Integer, default=0)
    
    # Per-agent statistics
    hawkington_memories = Column(Integer, default=0)
    snail_memories = Column(Integer, default=0)
    hamsters_memories = Column(Integer, default=0)
    qsp_memories = Column(Integer, default=0)
    vic20_memories = Column(Integer, default=0)
    stick_memories = Column(Integer, default=0)  # From existing stick_memory_bank
    
    # Learning effectiveness
    successful_transfers = Column(Integer, default=0)
    failed_transfers = Column(Integer, default=0)
    average_effectiveness_score = Column(Float, default=0.0)
    
    # Memory bank health
    memory_bank_health_score = Column(Float, default=100.0)
    stick_anxiety_level = Column(Float)  # The Stick's current anxiety about memory integrity
    
    # Performance metrics
    memory_retrieval_speed_ms = Column(Float)
    cross_agent_query_speed_ms = Column(Float)
    learning_application_success_rate = Column(Float)
    
    # agent_memory_bank_base = CentralMemoryBank

    __table_args__ = (
        Index('idx_memory_health', 'memory_bank_health_score', 'timestamp'),
        Index('idx_learning_effectiveness', 'average_effectiveness_score', 'successful_transfers'),
    )
# DEPRECATED: compatibility shim to ease migration away from per-agent memory tables.
# Remove this file after all imports are updated.

# from app.models.agent_memory import CentralMemoryBank as agent_memory_bank_base  # alias for old name
# from app.models.agent_memory import CentralMemoryBank

# # If callers imported AgentGlobalPattern for a specific query path,
# # direct them to use CentralMemoryBank with filters instead.
# class AgentGlobalPattern:  # sentinel to trigger a clear error if used as a model
#     def __init__(self, *_, **__):
#         raise RuntimeError(
#             "AgentGlobalPattern is deprecated. Use CentralMemoryBank with appropriate filters."
#         )

# __all__ = ["agent_memory_bank_base", "CentralMemoryBank", "AgentGlobalPattern"]
