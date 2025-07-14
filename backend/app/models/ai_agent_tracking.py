from sqlalchemy import Column, Integer, Float, DateTime, String, JSON, Index, Boolean, Text
from app.core.base import Base
from datetime import datetime

class AIAgentMetrics(Base):
    """Track AI agent performance, decisions, and data quality incidents"""
    __tablename__ = "ai_agent_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)  # Some decisions might be system-wide
    agent_name = Column(String(50), nullable=False, index=True)  # 'sir_hawkington', 'meth_snail', etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Decision tracking
    decision_type = Column(String(50))  # 'normal', 'concern', 'alert', 'balanced', 'aggressive', etc.
    decision_confidence = Column(Float)  # 0.0 to 1.0
    decision_rationale = Column(Text)    # The agent's reasoning
    actions_taken = Column(JSON)         # List of actions
    estimated_impact = Column(JSON)      # Expected improvements
    urgency_level = Column(String(20))   # 'immediate', 'soon', 'eventual'
    
    # Data quality tracking
    data_quality_score = Column(Float)   # 0.0 to 1.0
    missing_metrics = Column(JSON)       # ['cpu_usage', 'memory_usage']
    invalid_metrics = Column(JSON)       # ['cpu_usage=150', 'memory_usage=-5']
    
    # Agent-specific incident tracking
    incident_count = Column(Integer, default=0)     # How many times the agent had issues
    incident_type = Column(String(50))              # 'shell_spin', 'monocle_yeet', 'paper_bag_hyperventilate', etc.
    incident_reason = Column(Text)                  # Why the incident occurred
    
    # Performance metrics
    analysis_duration_ms = Column(Integer)          # How long the analysis took
    successful_analysis = Column(Boolean, default=True)
    
    # Metadata
    analysis_depth = Column(String(20))             # 'basic', 'standard', 'thorough'
    agent_version = Column(String(20))              # Track which version of the agent
    
    __table_args__ = (
        Index('idx_agent_user_time', 'agent_name', 'user_id', 'timestamp'),
        Index('idx_agent_incidents', 'agent_name', 'incident_type', 'timestamp'),
    )

class MethSnailShellSpins(Base):
    """Dedicated tracking for Meth Snail's shell spinning incidents"""
    __tablename__ = "meth_snail_shell_spins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Shell spin specifics
    missing_metrics = Column(JSON)       # ['cpu_usage', 'memory_usage']
    invalid_metrics = Column(JSON)       # ['cpu_usage=150']
    reason = Column(Text)                # Detailed reason for shell spinning
    
    # Context
    metrics_attempted = Column(JSON)     # What metrics were in the request
    analysis_depth = Column(String(20))  # What type of analysis was attempted
    
    # Aggregation helpers
    hour_start = Column(DateTime)        # For hourly aggregation
    date = Column(DateTime)              # For daily aggregation
    
    __table_args__ = (
        Index('idx_shell_spin_user_time', 'user_id', 'timestamp'),
        Index('idx_shell_spin_hourly', 'hour_start'),
    )

class SirHawkingtonMonocleYeets(Base):
    """Track Sir Hawkington's monocle yeeting incidents"""
    __tablename__ = "sir_hawkington_monocle_yeets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Monocle yeet specifics
    yeet_trigger = Column(String(100))   # What caused the yeet
    yeet_intensity = Column(String(20))  # 'polite', 'concerned', 'alarmed', 'utterly_appalled'
    system_state = Column(JSON)          # System metrics at time of yeet
    
    # Analysis context
    expected_behavior = Column(JSON)     # What Sir Hawkington expected
    actual_behavior = Column(JSON)       # What actually happened
    concern_level = Column(String(20))   # 'minor', 'moderate', 'severe', 'catastrophic'
    
    # Aggregation helpers
    hour_start = Column(DateTime)
    date = Column(DateTime)
    
    __table_args__ = (
        Index('idx_monocle_yeet_user_time', 'user_id', 'timestamp'),
        Index('idx_monocle_yeet_intensity', 'yeet_intensity', 'timestamp'),
    )

class TheStickHyperventilations(Base):
    """Track The Stick's paper bag hyperventilation incidents"""
    __tablename__ = "the_stick_hyperventilations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Hyperventilation specifics
    anxiety_trigger = Column(String(100))    # What caused the anxiety
    anxiety_level = Column(String(20))       # 'mild', 'moderate', 'severe', 'panic'
    compliance_issue = Column(JSON)          # What compliance issue was detected
    
    # Context
    policy_violated = Column(String(100))    # Which policy/rule was violated
    risk_assessment = Column(JSON)           # The Stick's risk analysis
    recommended_actions = Column(JSON)       # What The Stick recommends
    
    # Recovery tracking
    paper_bags_used = Column(Integer, default=1)  # How many paper bags were needed
    recovery_time_seconds = Column(Integer)       # How long to calm down
    
    # Aggregation helpers
    hour_start = Column(DateTime)
    date = Column(DateTime)
    
    __table_args__ = (
        Index('idx_stick_anxiety_user_time', 'user_id', 'timestamp'),
        Index('idx_stick_anxiety_level', 'anxiety_level', 'timestamp'),
    )

class QuantumShadowPhasings(Base):
    """Track Quantum Shadow People's dimensional phase incidents"""
    __tablename__ = "quantum_shadow_phasings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Phasing specifics
    phase_type = Column(String(50))          # 'dimensional_shift', 'router_jello_shot', 'quantum_entanglement'
    phase_reason = Column(Text)              # Why they phased
    destination_dimension = Column(String(100))  # Where they went
    
    # Network context (they handle network stuff)
    network_issue = Column(JSON)             # What network problem occurred
    quantum_solution = Column(JSON)          # Their mysterious solution
    router_status = Column(String(50))       # 'upside_down_in_jello', 'quantum_entangled', 'normal'
    
    # Mystery tracking
    solution_comprehensibility = Column(Float)  # 0.0 (nobody understands) to 1.0 (makes sense)
    effectiveness_rating = Column(Float)        # 0.0 (didn't work) to 1.0 (brilliant)
    
    # Aggregation helpers
    hour_start = Column(DateTime)
    date = Column(DateTime)
    
    __table_args__ = (
        Index('idx_quantum_phase_user_time', 'user_id', 'timestamp'),
        Index('idx_quantum_phase_type', 'phase_type', 'timestamp'),
    )

class VIC20Wisdom(Base):
    """Track VIC20 Sage's wisdom dispensing incidents"""
    __tablename__ = "vic20_wisdom"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Wisdom specifics
    wisdom_type = Column(String(50))         # 'ancient_knowledge', 'war_games_reference', 'basic_command'
    wisdom_content = Column(Text)            # The actual wisdom
    relevance_score = Column(Float)          # How relevant to current problem
    
    # Context
    problem_addressed = Column(Text)         # What problem triggered the wisdom
    historical_reference = Column(String(100))  # 'war_games', 'commodore_64', 'punch_cards'
    
    # Impact tracking
    wisdom_followed = Column(Boolean)        # Did anyone listen?
    outcome_success = Column(Boolean)        # Did it work?
    
    # Aggregation helpers
    hour_start = Column(DateTime)
    date = Column(DateTime)
    
    __table_args__ = (
        Index('idx_wisdom_user_time', 'user_id', 'timestamp'),
        Index('idx_wisdom_type', 'wisdom_type', 'timestamp'),
    )