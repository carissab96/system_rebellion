#!/usr/bin/env python3
"""
Learned Thresholds Models

Stores threshold learning records for autonomous threshold adaptation.
Each system learns its own optimal thresholds based on outcomes.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base


class ThresholdLearningRecord(Base):
    """
    Record of what happened when a metric crossed a value.
    
    Used to learn system-specific thresholds:
    - If false alarm: threshold was too low, increase it
    - If acted too late: threshold was too high, decrease it
    - If just right: increase confidence in current threshold
    """
    __tablename__ = 'threshold_learning_records'
    
    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(String(255), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    
    # Metric information
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    threshold_level = Column(String(20), nullable=False)  # 'monitor', 'warning', 'critical', 'emergency'
    
    # Action and outcome
    action_taken = Column(String(100))  # NULL if just monitored
    outcome_success = Column(Boolean)
    
    # Context at the time
    system_state = Column(JSON)  # Other metrics at the time
    context = Column(JSON)  # Time of day, day of week, system load, etc.
    
    # Learning signals
    time_to_critical = Column(Float)  # Minutes until became critical (if it did)
    was_false_alarm = Column(Boolean, default=False)  # Resolved without intervention
    should_have_acted_sooner = Column(Boolean, default=False)  # Became critical too fast
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_system_metric_time', 'system_id', 'metric_name', 'created_at'),
        Index('idx_metric_value', 'metric_name', 'metric_value'),
    )
    
    def __repr__(self):
        return (
            f"<ThresholdLearningRecord("
            f"system={self.system_id}, "
            f"metric={self.metric_name}={self.metric_value:.1f}, "
            f"false_alarm={self.was_false_alarm}, "
            f"too_late={self.should_have_acted_sooner})>"
        )


class ActionOutcomeRecord(Base):
    """
    Record of an action and its outcome.
    
    Used to learn which actions work in which metric patterns.
    Not "restart_service is aggressive" but "restart_service has X% success
    when metrics look like THIS."
    """
    __tablename__ = 'action_outcome_records'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    
    # Link back to CentralMemoryBank for vector similarity queries
    central_memory_id = Column(String(36), index=True)
    
    # Metrics before and after
    pre_metrics = Column(JSON, nullable=False)
    post_metrics = Column(JSON, nullable=False)
    
    # Pattern fingerprint for similarity matching
    metric_pattern_fingerprint = Column(String(255), nullable=False, index=True)
    
    # Outcome
    success = Column(Boolean, nullable=False, index=True)
    improvement = Column(Float, nullable=False)  # % improvement in primary metric
    primary_metric = Column(String(100))  # Which metric was targeted
    
    # Context
    severity_score = Column(Float, nullable=False)
    other_actions_considered = Column(JSON)  # List of alternative actions
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_agent_action_pattern', 'agent_name', 'action', 'metric_pattern_fingerprint'),
        Index('idx_pattern_success', 'metric_pattern_fingerprint', 'success'),
    )
    
    def __repr__(self):
        return (
            f"<ActionOutcomeRecord("
            f"agent={self.agent_name}, "
            f"action={self.action}, "
            f"success={self.success}, "
            f"improvement={self.improvement:.1%})>"
        )


class MetricPatternHistory(Base):
    """
    Historical patterns for forecasting.
    
    Stores: "When metric was at X, it became Y after 15min/30min/1hr"
    Used for pattern-based forecasting.
    """
    __tablename__ = 'metric_pattern_history'
    
    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(String(255), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    
    # Starting point
    starting_value = Column(Float, nullable=False, index=True)
    starting_timestamp = Column(TIMESTAMP, nullable=False, index=True)
    
    # Future values
    value_15min_later = Column(Float)
    value_30min_later = Column(Float)
    value_1hr_later = Column(Float)
    
    # Context for pattern matching
    context = Column(JSON)  # Time of day, day of week, system load, growth rate
    
    # Pattern fingerprint
    context_fingerprint = Column(String(255), index=True)
    
    __table_args__ = (
        Index('idx_system_metric_value', 'system_id', 'metric_name', 'starting_value'),
        Index('idx_context_pattern', 'context_fingerprint', 'starting_value'),
    )
    
    def __repr__(self):
        return (
            f"<MetricPatternHistory("
            f"system={self.system_id}, "
            f"metric={self.metric_name}, "
            f"start={self.starting_value:.1f}, "
            f"15min={self.value_15min_later:.1f})>"
        )


class LearnedSequence(Base):
    """
    A learned execution sequence — an ordered list of primitives that
    has proven effective for a given goal in a given context.

    Lifecycle: cold_start → experience → stick_validated → promoted
                                                         → deprecated

    This is NOT an action outcome record. It's a strategy composed from
    multiple action outcomes. It has its own confidence tracking, sample
    size, and Stick validation status. Sequences are discovered when cold
    start hypotheses succeed and promoted when The Stick validates them.
    """
    __tablename__ = 'learned_sequences'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    system_id = Column(String(255), nullable=False, index=True)
    goal = Column(String(100), nullable=False, index=True)   # From goal vocabulary

    # The sequence itself — ordered list of primitive names
    primitives = Column(JSON, nullable=False)

    # Effectiveness tracking
    effectiveness_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)         # Based on sample size
    sample_size = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)       # success_count / sample_size
    avg_improvement = Column(Float, default=0.0)
    avg_duration_seconds = Column(Float, default=0.0)

    # Intervention context — for predictive engine (post-launch)
    # Sparsely populated until predictive engine comes online.
    # Costs nothing now, saves a migration later.
    intervention_type = Column(String(20), default='reactive')  # reactive, preemptive, maintenance
    trigger_severity = Column(Float, nullable=True)   # 0.0-1.0, avg severity at trigger
    trigger_trend = Column(String(20), nullable=True) # rising, stable, falling

    # Lifecycle
    first_discovered = Column(TIMESTAMP, server_default=func.now())
    last_used = Column(TIMESTAMP, nullable=True)
    stick_validated = Column(Boolean, default=False)
    promoted = Column(Boolean, default=False)           # Promoted for general use
    deprecated = Column(Boolean, default=False)         # No longer effective
    deprecated_reason = Column(String(500), nullable=True)

    # Provenance
    learned_from = Column(String(50), default='experience')  # experience, cross_agent, cold_start
    parent_sequence_id = Column(Integer, nullable=True)      # If evolved from another sequence

    __table_args__ = (
        Index('idx_learned_seq_agent_goal', 'agent_name', 'goal'),
        Index('idx_learned_seq_system_goal', 'system_id', 'goal'),
        Index('idx_learned_seq_active', 'agent_name', 'goal', 'deprecated', 'confidence'),
    )

    def __repr__(self):
        return (
            f"<LearnedSequence("
            f"id={self.id}, "
            f"agent={self.agent_name}, "
            f"goal='{self.goal}', "
            f"primitives={self.primitives}, "
            f"effectiveness={self.effectiveness_score:.2f}, "
            f"samples={self.sample_size})>"
        )
