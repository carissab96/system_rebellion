# /models/sir_hawkington_models.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
Base = declarative_base()

class HawkingtonDecisionLog(Base):
    """Store Sir Hawkington's aristocratic monitoring decisions"""
    __tablename__ = 'hawkington_decision_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Decision details
    decision_type = Column(String, nullable=False, index=True)
    monocle_state = Column(String, nullable=False)
    monitoring_target = Column(String, nullable=False)
    
    # Alert details
    alert_parameters = Column(JSON, nullable=True)
    monocle_yeet_required = Column(Boolean, default=False)
    aristocratic_explanation = Column(Text, nullable=True)
    technical_details = Column(JSON, nullable=True)
    
    # Performance metrics
    severity_level = Column(String, nullable=True)
    confidence_level = Column(Float, nullable=True)
    
    # Success tracking
    alert_sent = Column(Boolean, default=False)
    user_acknowledged = Column(Boolean, default=False)
    issue_resolved = Column(Boolean, default=False)

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