# app/models/triage_decision_models.py
"""
Triage Decision Database Models
For storing Sir Hawkington's aristocratic triage decisions
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import Base
from datetime import datetime, timezone


class TriageDecisionLog(Base):
    """
    Sir Hawkington's Triage Decision Log
    Records every aristocratic triage decision for pattern analysis
    """
    __tablename__ = "triage_decision_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Triage Assessment
    triage_severity = Column(String(50), nullable=False, index=True)  # normal, medium, high, emergency
    routing_decision = Column(String(100), nullable=False, index=True)  # stick_direct, vic20_coordination, etc.
    target_agents = Column(JSON, nullable=False)  # List of target agent names
    reasoning = Column(Text, nullable=False)  # Sir Hawkington's reasoning
    
    # Decision Quality
    monocle_yeeted = Column(Boolean, default=False, nullable=False, index=True)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    hawkington_decision_id = Column(Integer, ForeignKey("hawkington_decision_logs.id"), nullable=True)
    
    # Processing Information  
    processing_time = Column(Float, nullable=False)  # Seconds
    success = Column(Boolean, default=True, nullable=False)
    routing_results = Column(JSON, nullable=True)  # Results from routed agents
    
    # Metadata
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    hawkington_decision = relationship("HawkingtonDecisionLog", back_populates="triage_decisions")

class TriageStatistics(Base):
    """
    Triage Engine Performance Statistics
    Tracks Sir Hawkington's triage performance over time
    """
    __tablename__ = "triage_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Time Period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    
    # Decision Counts
    total_decisions = Column(Integer, default=0, nullable=False)
    normal_decisions = Column(Integer, default=0, nullable=False)
    medium_decisions = Column(Integer, default=0, nullable=False)
    high_decisions = Column(Integer, default=0, nullable=False)
    emergency_decisions = Column(Integer, default=0, nullable=False)
    
    # Routing Statistics
    stick_direct_count = Column(Integer, default=0, nullable=False)
    vic20_coordination_count = Column(Integer, default=0, nullable=False)
    vic20_emergency_count = Column(Integer, default=0, nullable=False)
    cpu_specialist_count = Column(Integer, default=0, nullable=False)
    
    # Quality Metrics
    monocle_yeet_count = Column(Integer, default=0, nullable=False)
    successful_routing_count = Column(Integer, default=0, nullable=False)
    failed_routing_count = Column(Integer, default=0, nullable=False)
    
    # Performance Metrics
    average_processing_time = Column(Float, nullable=False)
    average_confidence = Column(Float, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

# Update the HawkingtonDecisionLog model to include the triage relationship
# ADD THIS TO: app/models/agent_decision_models.py

# In the HawkingtonDecisionLog class, add this relationship:
# triage_decisions = relationship("TriageDecisionLog", back_populates="hawkington_decision")