# Agent Memory Banks - Persistent Learning Architecture
# System Rebellion AI Agent Memory System

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy import func
from app.core.types import PG_JSONB, SA_JSON
from sqlalchemy.dialects.postgresql import JSONB

# ============================================================================
# CENTRAL MEMORY BANK - The Stick's Eidetic Memory Hub
# ============================================================================

class CentralMemoryBank(Base):
    """
    Central hub for all agent memories and learnings.
    Single source of truth with mixed BTREE (filters/sorts) + GIN (JSONBCompat) indexes.
    """
    __tablename__ = "central_memory_bank"

    # --- identifiers
    id = Column(Integer, primary_key=True)
    memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)

    # --- timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # --- source / ownership
    agent_name = Column(String(50), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    # NOTE: ensure User model has: central_memories = relationship("CentralMemoryBank", back_populates="user", ...)
    user = relationship("User", back_populates="central_memories", lazy="joined")

    # --- classification
    event_type = Column(String(100), nullable=False, index=True)
    subject_kind = Column(String(50), index=True)
    subject_id = Column(String(36), index=True)
    priority = Column(Integer, default=2, index=True)

    # --- content
    title = Column(String(255))
    description = Column(Text)
    details = Column(PG_JSONB, nullable=True)          # primary payload
    metadata_ = Column("metadata", PG_JSONB, nullable=True)  # extra payload (column name is "metadata")

    @property
    def content(self):
        """Alias for details (back-compat)."""
        return self.details

    # --- references / tracing
    correlation_id = Column(String(36))
    trace_id = Column(String(36))
    parent_memory_id = Column(String(36), ForeignKey("central_memory_bank.memory_id"))

    parent_memory = relationship(
        "CentralMemoryBank",
        remote_side=[memory_id],
        backref=backref("related_memories", lazy="dynamic"),
    )

    # --- measurements
    numeric_value = Column(Float)
    string_value = Column(Text)
    tags = Column(PG_JSONB, nullable=True)             # flexible filtering (labels, facets)

    # --- agent-specific metadata
    agent_metadata = Column(PG_JSONB, nullable=True)

    # --- cross-agent flags
    relevant_agents = Column(String(255))
    cross_agent_validated = Column(Boolean, default=False)
    validation_count = Column(Integer, default=0)

    # --- retention / usage
    stick_anxiety_level = Column(Float)
    never_forget = Column(Boolean, default=False)
    times_referenced = Column(Integer, default=0)
    last_referenced = Column(DateTime)
    successful_applications = Column(Integer, default=0)

    # --- indexes (BTREE + GIN split)
    __table_args__ = (
        # Common filters / sorts (BTREE)
        Index("idx_agent_event_time", "agent_name", "event_type", "occurred_at", postgresql_using="btree"),
        Index("idx_user_events", "user_id", "occurred_at", postgresql_using="btree"),
        Index("idx_metric_queries", "event_type", "occurred_at", "subject_kind", postgresql_using="btree"),
        Index("idx_event_timestamp", "event_type", "occurred_at", postgresql_using="btree"),
        Index("idx_agent_user", "agent_name", "user_id", postgresql_using="btree"),
        Index("idx_subject_reference", "subject_kind", "subject_id", postgresql_using="btree"),
        Index("idx_priority_access", "priority", "last_referenced", postgresql_using="btree"),
        Index("idx_memory_importance", "priority", "never_forget", postgresql_using="btree"),
        Index("idx_correlation", "correlation_id", "trace_id", postgresql_using="btree"),

        # JSONBCompat search (GIN). You can choose 'jsonb_path_ops' if you mostly do containment/exists queries.
        Index(
            "idx_cmb_details_gin",
            "details",
            postgresql_using="gin",
            postgresql_ops={"details": "jsonb_path_ops"},
        ),
        Index(
            "idx_cmb_metadata_gin",
            "metadata",
            postgresql_using="gin",
            postgresql_ops={"metadata": "jsonb_path_ops"},
        ),
        Index(
            "idx_cmb_tags_gin",
            "tags",
            postgresql_using="gin",
            postgresql_ops={"tags": "jsonb_path_ops"},
        ),
    )
# ============================================================================
# INDIVIDUAL AGENT MEMORY BANKS
# ============================================================================

# class SirHawkingtonMemoryBank(Base):
#     """
#     Sir Hawkington's Distinguished Memory Bank
    
#     Focuses on data quality patterns, triage decisions, and aristocratic
#     monitoring insights. Tracks monocle-yeeting triggers and refinement.
#     """
#     __abstract__ = True
#     __tablename__ = 'sir_hawkington_memory_bank'
    
#     id = Column(Integer, primary_key=True)
#     memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
#     user_id = Column(String(255), nullable=False, index=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
#     # Hawkington-specific memory types
#     memory_category = Column(String(50), nullable=False, index=True)  # triage, quality, monocle_yeet, etc.
#     data_quality_pattern = Column(JSON)  # Patterns in data quality issues
#     triage_decision_context = Column(JSON)  # Context for triage routing decisions
    
#     # Cross-references to other tables
#     # monitoring_stats_id = Column(Integer, ForeignKey('hawkington_monitoring_stats.id'), index=True)
#     # monitoring_stats = relationship(
#     #     "HawkingtonMonitoringStats", 
#     #     back_populates="memory_entries",
#     #     foreign_keys=[monitoring_stats_id]
#     # )
    
#     # Relationship to user model
#     user = relationship(
#         "User", 
#         back_populates="sir_hawkington_memories",
#         foreign_keys=[user_id]
#     )
    
#     quality_threshold_adjustment = Column(JSON)  # Learned threshold adjustments
    
#     # Performance tracking
#     accuracy_improvement = Column(Float)  # Measured improvement in accuracy
#     false_positive_reduction = Column(Float)  # Reduction in false alerts
    
#     # Cross-agent coordination
#     shared_with_central = Column(Boolean, default=False)
#     central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
#     __table_args__ = (
#         Index('idx_hawkington_category', 'memory_category', 'timestamp'),
#         Index('idx_hawkington_shared', 'shared_with_central', 'central_memory_id'),
#     )

# class MethSnailMemoryBank(Base):
#     """Meth Snail's Caffeinated Memory Bank
    
#     Tracks optimization patterns, energy drink effectiveness, and shell-spinning
#     insights. Learns from caffeine-fueled optimization sessions.
#     """
#     __abstract__ = True
#     __tablename__ = 'meth_snail_memory_bank'
    
#     id = Column(Integer, primary_key=True)
#     memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
#     user_id = Column(String(255), nullable=False, index=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
#     # Snail-specific memory types
#     optimization_pattern = Column(JSON)  # Learned optimization patterns
#     caffeine_level_context = Column(Float)  # Caffeine level when learning occurred
#     shell_spin_correlation = Column(JSON)  # Correlation between spinning and performance
    
#     # Energy drink insights
#     energy_drink_effectiveness = Column(JSON)  # Which drinks work best for what
#     jitter_threshold_learning = Column(JSON)  # Optimal jitter levels for different tasks
#     crash_prevention_patterns = Column(JSON)  # How to avoid caffeine crashes
    
#     # Optimization results
#     performance_improvement = Column(Float)  # Measured performance gain
#     resource_efficiency_gain = Column(Float)  # Resource usage improvement
#     optimization_duration = Column(Float)  # How long the optimization took
    
#     # Learning metadata
#     confidence_level = Column(Float)  # How confident about this optimization
#     replication_success_rate = Column(Float)  # Success rate when applied elsewhere
    
#     # Cross-agent coordination
#     shared_with_central = Column(Boolean, default=False)
#     central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
#     __table_args__ = (
#         Index('idx_snail_optimization', 'optimization_pattern', 'performance_improvement'),
#         Index('idx_snail_caffeine', 'caffeine_level_context', 'timestamp'),
#     )

# class HamstersMemoryBank(Base):
#     """Hamsters Collective Memory Bank (Steve, Bob, and Carl)
    
#     Tracks infrastructure patterns, duct tape solutions, and beer-fueled
#     engineering insights. Includes individual and collective learnings.
#     """
#     __abstract__ = True
#     __tablename__ = 'hamsters_memory_bank'
    
#     id = Column(Integer, primary_key=True)
#     memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
#     user_id = Column(String(255), nullable=False, index=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
#     # Hamster-specific memory
#     contributing_hamster = Column(String(10), nullable=False, index=True)  # steve, bob, carl, or collective
#     infrastructure_pattern = Column(JSON)  # Infrastructure-related patterns
#     duct_tape_solution = Column(JSON)  # Duct tape engineering solutions
    
#     # Engineering insights
#     problem_type = Column(String(100), nullable=False, index=True)  # disk, hardware, mystery, etc.
#     solution_effectiveness = Column(Float)  # How well the solution worked
#     beer_consumption_correlation = Column(JSON)  # Beer levels vs solution quality
    
#     # Individual hamster contributions
#     steve_contribution = Column(JSON)  # Steve's careful measurements
#     bob_contribution = Column(JSON)  # Bob's wild ideas and supply raids
#     carl_contribution = Column(JSON)  # Carl's duct tape calculations
    
#     # Risk assessment learning
#     risk_pattern = Column(JSON)  # Learned risk patterns
#     safety_protocol_adjustment = Column(JSON)  # Safety improvements
#     stick_anxiety_trigger = Column(JSON)  # What causes The Stick anxiety
    
#     # Cross-agent coordination
#     shared_with_central = Column(Boolean, default=False)
#     central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
#     __table_args__ = (
#         Index('idx_hamsters_contributor', 'contributing_hamster', 'problem_type'),
#         Index('idx_hamsters_effectiveness', 'solution_effectiveness', 'timestamp'),
#     )

# class QuantumShadowPeopleMemoryBank(Base):
#     """Quantum Shadow People's Incomprehensible Memory Bank
    
#     Tracks network security patterns, phase-shift insights, and quantum
#     threat detection. Deliberately cryptic but functionally effective.
#     """
#     __abstract__ = True
#     __tablename__ = 'quantum_shadow_people_memory_bank'
    
#     id = Column(Integer, primary_key=True)
#     memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
#     user_id = Column(String(255), nullable=False, index=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
#     # QSP-specific memory (deliberately cryptic)
#     phase_pattern = Column(JSON)  # Network phase patterns
#     quantum_signature = Column(JSON)  # Quantum threat signatures
#     dimensional_correlation = Column(JSON)  # Multi-dimensional security correlations
    
#     # Security insights
#     threat_pattern_recognition = Column(JSON)  # Learned threat patterns
#     network_anomaly_signatures = Column(JSON)  # Network anomaly patterns
#     phase_shift_effectiveness = Column(Float)  # Effectiveness of phase shifts
    
#     # Incomprehensible but functional data
#     tequila_jello_correlation = Column(JSON)  # Mysterious but effective correlations
#     comprehensibility_score = Column(Float)  # How incomprehensible this is (lower = better)
#     quantum_confidence = Column(Float)  # Quantum confidence level
    
#     # Cross-dimensional learning
#     parallel_universe_validation = Column(JSON)  # Validation from other dimensions
#     telepathic_hamster_confirmation = Column(Boolean, default=False)  # Hamster telepathy confirmation
    
#     # Cross-agent coordination
#     shared_with_central = Column(Boolean, default=False)
#     central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
#     __table_args__ = (
#         Index('idx_qsp_phase', 'phase_pattern', 'quantum_confidence'),
#         Index('idx_qsp_comprehensibility', 'comprehensibility_score', 'phase_shift_effectiveness'),
#     )

# class VIC20MemoryBank(Base):
#     """VIC-20's Ancient Wisdom Memory Bank
    
#     Tracks coordination patterns, mediation insights, and ancient computing
#     wisdom. Learns from conflicts and successful coordinations.
#     """
#     __abstract__ = True
#     __tablename__ = 'vic20_memory_bank'
    
#     id = Column(Integer, primary_key=True)
#     memory_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
#     user_id = Column(String(255), nullable=False, index=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
#     # VIC-20 specific memory
#     coordination_pattern = Column(JSON)  # Agent coordination patterns
#     mediation_insight = Column(JSON)  # Conflict mediation learnings
#     ancient_wisdom_application = Column(JSON)  # How ancient wisdom applies
    
#     # Coordination learning
#     conflict_resolution_method = Column(JSON)  # Successful conflict resolutions
#     agent_harmony_score = Column(Float)  # Measured harmony improvement
#     coordination_efficiency = Column(Float)  # Coordination efficiency gains
    
#     # Mediation insights
#     agent_personality_patterns = Column(JSON)  # Learned agent personality patterns
#     successful_mediation_strategies = Column(JSON)  # What mediation strategies work
#     failure_prevention_wisdom = Column(JSON)  # Ancient wisdom for preventing failures
    
#     # 8-bit wisdom
#     retro_computing_insight = Column(JSON)  # Insights from ancient computing
#     simplicity_effectiveness = Column(Float)  # How effective simple solutions are
#     modern_complexity_critique = Column(JSON)  # Critiques of modern overcomplexity
    
#     # Cross-agent coordination
#     shared_with_central = Column(Boolean, default=False)
#     central_memory_id = Column(String(36), ForeignKey('central_memory_bank.memory_id'))
    
#     __table_args__ = (
#         Index('idx_vic20_coordination', 'coordination_pattern', 'agent_harmony_score'),
#         Index('idx_vic20_mediation', 'mediation_insight', 'coordination_efficiency'),
#     )

# ============================================================================
# CROSS-AGENT LEARNING TABLES
# ============================================================================

class AgentLearningInteractions(Base):
    """
    Track how agents learn from each other's experiences
    """
    __tablename__ = 'agent_learning_interactions'

    id = Column(Integer, primary_key=True)
    interaction_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Learning transfer
    source_agent = Column(String(50), nullable=False, index=True)
    target_agent = Column(String(50), nullable=False, index=True)
    source_memory_id = Column(String(36), nullable=False)

    # Transfer details
    learning_type = Column(String(100), nullable=False)
    adaptation_method = Column(PG_JSONB, nullable=True)       # JSONBCompat
    application_context = Column(PG_JSONB, nullable=True)     # JSONBCompat

    # Effectiveness tracking
    transfer_success = Column(Boolean, default=False)
    effectiveness_score = Column(Float)
    improvement_measured = Column(Float)

    # Validation
    validated_by_stick = Column(Boolean, default=False)
    cross_validation_count = Column(Integer, default=0)

    __table_args__ = (
        # BTREE (simple scalars)
        Index('idx_learning_transfer', 'source_agent', 'target_agent', 'learning_type', postgresql_using='btree'),
        Index('idx_learning_effectiveness', 'effectiveness_score', 'transfer_success', postgresql_using='btree'),

        # GIN on JSONBCompat payloads (optional but recommended if you query into these)
        Index('idx_ali_adaptation_gin', 'adaptation_method',  # <- typo? use the correct column name below
              postgresql_using='gin',
              postgresql_ops={'adaptation_method': 'jsonb_path_ops'}),  # if you mostly do containment
        Index('idx_ali_appctx_gin', 'application_context',
              postgresql_using='gin',
              postgresql_ops={'application_context': 'jsonb_path_ops'}),
    )

class UserLearningPatterns(Base):
    """
    Patterns in how users interact/learn so agents can adapt.
    """
    __tablename__ = 'user_learning_patterns'

    id = Column(Integer, primary_key=True)
    pattern_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)

    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    user = relationship("User", back_populates="user_learning_patterns", lazy="joined")

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # User behavior patterns (JSONBCompat)
    interaction_pattern = Column(PG_JSONB, nullable=True)
    learning_preference = Column(PG_JSONB, nullable=True)  # JSONB -> GIN
    response_patterns = Column(PG_JSONB, nullable=True)

    # Agent adaptation
    most_effective_agent = Column(String(50), nullable=True)
    communication_style_preference = Column(PG_JSONB, nullable=True)
    complexity_tolerance = Column(Float, nullable=True)

    # Learning outcomes
    skill_improvement_areas = Column(PG_JSONB, nullable=True)
    knowledge_gaps = Column(PG_JSONB, nullable=True)
    success_patterns = Column(PG_JSONB, nullable=True)

    # Cross-agent insights
    agent_effectiveness_ranking = Column(PG_JSONB, nullable=True)
    collaborative_preferences = Column(PG_JSONB, nullable=True)

    __table_args__ = (
        # BTREE on scalars
        Index('idx_user_patterns', 'user_id', 'most_effective_agent', postgresql_using='btree'),
        Index('idx_user_complexity', 'user_id', 'complexity_tolerance', postgresql_using='btree'),

        # GIN on JSONBCompat fields you actually query into
        Index('idx_ulp_learning_pref_gin', 'learning_preference',
              postgresql_using='gin',
              postgresql_ops={'learning_preference': 'jsonb_path_ops'}),
        # add others if you filter on them:
        # Index('idx_ulp_interaction_pattern_gin', 'interaction_pattern', postgresql_using='gin',
        #       postgresql_ops={'interaction_pattern': 'jsonb_path_ops'}),
    )

class MemoryBankMetadata(Base):
    """
    Metadata about the memory system (health, effectiveness).
    """
    __tablename__ = 'memory_bank_metadata'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # System-wide statistics
    total_memories = Column(Integer, default=0)
    central_bank_memories = Column(Integer, default=0)
    cross_agent_learnings = Column(Integer, default=0)

    # Per-agent counts
    hawkington_memories = Column(Integer, default=0)
    snail_memories = Column(Integer, default=0)
    hamsters_memories = Column(Integer, default=0)
    qsp_memories = Column(Integer, default=0)
    vic20_memories = Column(Integer, default=0)
    stick_memories = Column(Integer, default=0)

    # Learning effectiveness
    successful_transfers = Column(Integer, default=0)
    failed_transfers = Column(Integer, default=0)
    average_effectiveness_score = Column(Float, default=0.0)

    # Memory bank health
    memory_bank_health_score = Column(Float, default=100.0)
    stick_anxiety_level = Column(Float)

    # Performance metrics
    memory_retrieval_speed_ms = Column(Float)
    cross_agent_query_speed_ms = Column(Float)
    learning_application_success_rate = Column(Float)

    __table_args__ = (
        Index('idx_memory_health', 'memory_bank_health_score', 'timestamp', postgresql_using='btree'),
        # renamed to avoid collisions with other tables’ names:
        Index('idx_mb_effectiveness', 'average_effectiveness_score', 'successful_transfers', postgresql_using='btree'),
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
