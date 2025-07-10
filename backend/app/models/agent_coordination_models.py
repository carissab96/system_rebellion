# /models/agent_coordination_models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AgentPerformanceSummary(Base):
    """Store cross-agent performance summary for intelligence coordination"""
    __tablename__ = 'agent_performance_summary'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    
    # Agent performance metrics
    agent_name = Column(String, nullable=False, index=True)
    total_decisions = Column(Integer, default=0)
    successful_decisions = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    average_confidence = Column(Float, nullable=True)
    last_decision_timestamp = Column(DateTime, nullable=True)
    
    # Performance stats
    performance_stats = Column(JSON, nullable=True)

class CrossAgentCoordination(Base):
    """Store cross-agent coordination events for VIC20 intelligence"""
    __tablename__ = 'cross_agent_coordination'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    
    # Coordination details
    primary_agent = Column(String, nullable=False)
    supporting_agents = Column(JSON, nullable=True)
    coordination_type = Column(String, nullable=False)
    
    # Coordination results
    coordination_success = Column(Boolean, default=False)
    coordination_details = Column(JSON, nullable=True)