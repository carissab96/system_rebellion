# /models/sir_hawkington_models.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
Base = declarative_base()

# NOTE: HawkingtonDecisionLog is now centralized in agent_decision_models.py

class HawkingtonMonitoringStats(Base):
    """Store Sir Hawkington's monitoring performance statistics"""
    __tablename__ = 'hawkington_monitoring_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Monitoring performance
    alerts_generated = Column(Integer, default=0)
    monocle_yeets_performed = Column(Integer, default=0)
    critical_issues_detected = Column(Integer, default=0)
    
    # Aristocratic metrics
    monitoring_precision = Column(Float, nullable=True)
    alert_accuracy_rate = Column(Float, nullable=True)
    user_response_time = Column(Float, nullable=True)
    
    # Raw stats
    raw_stats = Column(JSON, nullable=True)