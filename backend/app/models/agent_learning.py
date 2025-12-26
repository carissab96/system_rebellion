#!/usr/bin/env python3
"""
Agent Learning Records Model

Stores learning experiences for agentic decision-making.
Each record captures: situation → action → outcome

Used for hierarchical fingerprint matching to find similar past situations.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AgentLearningRecord(Base):
    """
    Learning record for agent decision-making.
    
    Stores what happened when an agent took an action in a specific situation.
    Used to build confidence and improve future decisions.
    """
    __tablename__ = 'agent_learning_records'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    
    # Hierarchical fingerprints (3 levels for fallback matching)
    fingerprint_l1 = Column(String(50), nullable=False, index=True)   # 'cpu_high'
    fingerprint_l2 = Column(String(100), nullable=False, index=True)  # 'cpu_high_memory_thrashing'
    fingerprint_l3 = Column(String(150), nullable=False, index=True)  # 'cpu_high_memory_thrashing_python'
    
    # Situation context
    resource_type = Column(String(20), nullable=False)
    severity = Column(String(20), nullable=False)
    root_cause = Column(String(500))  # Increased from 50 to 500 for detailed reasoning
    process_category = Column(String(20), index=True)  # 'python', 'database', 'web_server', 'system', 'other'
    
    # Action taken
    action = Column(String(100), nullable=False, index=True)
    parameters = Column(JSON)  # Action parameters as JSON
    confidence = Column(Float)
    followed_vic20 = Column(Boolean, default=False)
    
    # Outcome
    success = Column(Boolean, nullable=False, index=True)
    improvement = Column(JSON)  # Metrics deltas: {'cpu_usage': -15.2, 'memory_usage': -5.1}
    what_worked = Column(String(500))  # Increased from unlimited to 500 for consistency
    what_failed = Column(String(500))  # Increased from unlimited to 500 for consistency
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    def __repr__(self):
        return (
            f"<AgentLearningRecord("
            f"agent={self.agent_name}, "
            f"fingerprint={self.fingerprint_l3}, "
            f"action={self.action}, "
            f"success={self.success})>"
        )
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'agent_name': self.agent_name,
            'fingerprint_l1': self.fingerprint_l1,
            'fingerprint_l2': self.fingerprint_l2,
            'fingerprint_l3': self.fingerprint_l3,
            'resource_type': self.resource_type,
            'severity': self.severity,
            'root_cause': self.root_cause,
            'process_category': self.process_category,
            'action': self.action,
            'parameters': self.parameters,
            'confidence': self.confidence,
            'followed_vic20': self.followed_vic20,
            'success': self.success,
            'improvement': self.improvement,
            'what_worked': self.what_worked,
            'what_failed': self.what_failed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
