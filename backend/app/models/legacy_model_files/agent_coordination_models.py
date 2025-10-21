# /models/agent_coordination_models.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from sqlalchemy import func


# NOTE: AgentPerformanceSummary is now centralized in agent_decision_models.py

class CrossAgentCoordination(Base):
    """Store cross-agent coordination events for VIC20 intelligence"""
    __tablename__ = 'cross_agent_coordination'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    
    # Coordination details
    primary_agent = Column(String, nullable=False)
    supporting_agents = Column(JSON, nullable=True)
    coordination_type = Column(String, nullable=False)
    
    # Coordination results
    coordination_success = Column(Boolean, default=False)
    coordination_details = Column(JSON, nullable=True)