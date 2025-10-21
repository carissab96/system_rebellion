# Agent Event Models - Three-Tier Memory Architecture
# System Rebellion AI Agent Event Tracking

from sqlalchemy import Column, Integer, BigInteger, String, Float, Boolean, DateTime, Date, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone, timedelta
from app.core.base import Base

# ============================================================================
# TIER 1: EVENT STREAM (Ephemeral - 30 days)
# ============================================================================

class AgentEventLog(Base):
    """
    SHORT-TERM event stream for real-time WebSocket broadcasts.
    
    Purpose: Capture all agent activities for real-time monitoring
    Retention: 30 days, then auto-deleted
    NOT for learning - just "what's happening right now"
    
    Event Types:
    - monocle_yeet, shell_spin, paper_bag_consumed
    - supply_closet_raid, energy_drink_requested, beer_consumed
    - duct_tape_used, dimensional_shift, wisdom_dispensed
    - triage_decision, anxiety_spike, optimization_applied
    """
    __tablename__ = 'agent_event_log'
    
    # Primary key
    id = Column(BigInteger, primary_key=True)  # BigInt for billions of events
    
    # Core event data
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Event payload (JSONB for flexible schema)
    event_data = Column(JSONB, nullable=False)
    
    # Fast filtering fields (denormalized for performance)
    severity = Column(String(20), index=True)  # 'low', 'medium', 'high', 'critical'
    agent_state = Column(String(50))  # 'hypercaffeinated', 'panicking', 'yeeting', 'raiding', etc.
    
    # Partitioning and cleanup helpers
    date_partition = Column(Date, nullable=False, index=True)
    ttl_expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Composite indexes for common query patterns
    __table_args__ = (
        # Agent activity timeline
        Index('idx_agent_event_time', 'agent_name', 'event_type', 'timestamp', postgresql_using='btree'),
        
        # User activity timeline
        Index('idx_user_event_time', 'user_id', 'timestamp', postgresql_using='btree'),
        
        # Event type filtering
        Index('idx_event_type_time', 'event_type', 'timestamp', postgresql_using='btree'),
        
        # Severity filtering
        Index('idx_severity_time', 'severity', 'timestamp', postgresql_using='btree'),
        
        # TTL cleanup
        Index('idx_ttl_cleanup', 'ttl_expires_at', postgresql_using='btree'),
        
        # JSONB search (GIN index for flexible queries)
        Index('idx_event_data_gin', 'event_data', postgresql_using='gin', postgresql_ops={'event_data': 'jsonb_path_ops'}),
        
        # Date partitioning support (for future scaling)
        Index('idx_date_partition', 'date_partition', postgresql_using='btree'),
    )
    
    def __repr__(self):
        return f"<AgentEventLog(agent={self.agent_name}, type={self.event_type}, time={self.timestamp})>"


# ============================================================================
# TIER 2: SIGNIFICANT EVENTS (Permanent - FOREVER)
# ============================================================================

class AgentSignificantEvent(Base):
    """
    LONG-TERM storage of significant events for learning and pattern recognition.
    
    Purpose: Store important events that taught the agent something
    Retention: FOREVER - used for "I've seen this before" decisions
    
    Criteria for significance:
    - First occurrence of a pattern
    - Extreme values (highest/lowest)
    - Successful learning moments
    - Critical incidents
    - User-marked as important
    - Led to pattern creation in memory bank
    """
    __tablename__ = 'agent_significant_events'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Core event data
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Event payload
    event_data = Column(JSONB, nullable=False)
    
    # Significance metadata
    significance_reason = Column(String(255), nullable=False)
    # Examples: "first_monocle_yeet_for_missing_cpu", "highest_anxiety_spike_ever",
    #           "most_successful_optimization", "bobs_most_destructive_raid"
    
    # Learning linkage
    learned_pattern_id = Column(String(36))  # Links to pattern in memory bank
    contributed_to_learning = Column(Boolean, default=True)
    
    # Memory importance
    never_forget = Column(Boolean, default=False, index=True)  # Critical learning moments
    
    # Usage tracking (how valuable is this memory?)
    times_referenced = Column(Integer, default=0)  # How many times used in decisions
    last_referenced = Column(DateTime(timezone=True))
    
    # Composite indexes
    __table_args__ = (
        # Agent significance timeline
        Index('idx_significant_agent_type', 'agent_name', 'event_type', 'timestamp', postgresql_using='btree'),
        
        # Never forget memories
        Index('idx_never_forget', 'never_forget', 'agent_name', postgresql_using='btree'),
        
        # Most referenced memories
        Index('idx_most_referenced', 'times_referenced', 'agent_name', postgresql_using='btree'),
        
        # User significant events
        Index('idx_user_significant', 'user_id', 'timestamp', postgresql_using='btree'),
        
        # JSONB search
        Index('idx_significant_data_gin', 'event_data', postgresql_using='gin', postgresql_ops={'event_data': 'jsonb_path_ops'}),
    )
    
    def __repr__(self):
        return f"<AgentSignificantEvent(agent={self.agent_name}, type={self.event_type}, reason={self.significance_reason})>"
    
    def increment_reference(self):
        """Track that this memory was used in a decision"""
        self.times_referenced += 1
        self.last_referenced = datetime.now(timezone.utc)


# ============================================================================
# TIER 3: AGGREGATE STATISTICS (Permanent - for dashboards)
# ============================================================================

class AgentStatistics(Base):
    """
    Pre-aggregated statistics for fast dashboard queries.
    Updated hourly/daily via background job.
    
    Purpose: Fast queries for dashboards and reports
    Retention: FOREVER (small data, pre-aggregated)
    """
    __tablename__ = 'agent_statistics'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Agent and user
    agent_name = Column(String(50), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Time period
    period_type = Column(String(20), nullable=False)  # 'hourly', 'daily', 'weekly', 'monthly'
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Event counts by type (JSONB for flexibility)
    event_counts = Column(JSONB, nullable=False)
    # Example: {"monocle_yeet": 12, "alert": 47, "triage": 156, "paper_bag": 7}
    
    # Performance metrics
    average_confidence = Column(Float)
    success_rate = Column(Float)
    
    # Agent-specific metrics (JSONB for flexibility)
    agent_metrics = Column(JSONB)
    # Hawkington: {"alert_accuracy": 0.92, "yeet_rate": 0.08}
    # Snail: {"energy_drinks": 4, "shell_spins": 2, "avg_jitter": 0.45}
    # Stick: {"paper_bags": 7, "anxiety_avg": 0.67, "bob_encounters": 3}
    # Hamsters: {"beer_consumed": 12, "duct_tape_strips": 47, "raids": 3}
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Composite indexes
    __table_args__ = (
        # Agent period queries
        Index('idx_agent_period', 'agent_name', 'period_type', 'period_start', postgresql_using='btree'),
        
        # User period queries
        Index('idx_user_period', 'user_id', 'period_type', 'period_start', postgresql_using='btree'),
        
        # Time range queries
        Index('idx_period_range', 'period_type', 'period_start', 'period_end', postgresql_using='btree'),
    )
    
    def __repr__(self):
        return f"<AgentStatistics(agent={self.agent_name}, period={self.period_type}, start={self.period_start})>"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_ttl_expiry(days=30):
    """Calculate TTL expiry timestamp (default 30 days from now)"""
    return datetime.now(timezone.utc) + timedelta(days=days)


def get_date_partition(timestamp=None):
    """Get date partition for a timestamp (for partitioning support)"""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    return timestamp.date()
