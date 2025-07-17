# app/models/metrics_aggregates.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Index
from sqlalchemy import func

class MetricsHourly(Base):
    """Hourly aggregated metrics - The Meth Snail's first optimization layer"""
    __tablename__ = "metrics_hourly"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    hour_start = Column(DateTime, nullable=False, index=True)

    #AI Agent Incident Tracking
    meth_snail_shell_spins = Column(Integer, default=0)
    hawkington_monocle_yeets = Column(Integer, default=0)
    stick_hyperventilations = Column(Integer, default=0)
    quantum_shadow_phasings = Column(Integer, default=0)
    vic20_wisdom_dispensed = Column(Integer, default=0)
    
    #overall AI Health
    ai_agent_incident_count = Column(Integer, default=0)
    ai_agent_incident_type = Column(String)
    ai_agent_incident_reason = Column(String)
    ai_agent_incident_data_quality_score = Column(Float)
    ai_agent_incident_summary = Column(JSON)

    
    # Aggregated values
    cpu_avg = Column(Float)
    cpu_max = Column(Float)
    cpu_min = Column(Float)
    
    memory_avg = Column(Float)
    memory_max = Column(Float)
    memory_min = Column(Float)
    
    disk_avg = Column(Float)
    network_bytes_total = Column(Float)
    
    # AI insights for this hour
    ai_events = Column(JSON)  # Sir Hawkington's concerns/alerts
    anomaly_count = Column(Integer, default=0)
    
    # Metadata
    sample_count = Column(Integer)  # How many raw samples in this hour
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_hour', 'user_id', 'hour_start'),
    )

class MetricsDaily(Base):
    """Daily rollups - The Meth Snail's second optimization layer"""
    __tablename__ = "metrics_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    #meth snail shell spins
    daily_meth_snail_shell_spins = Column(Integer, default=0)
    daily_hawkington_monocle_yeets = Column(Integer, default=0)
    daily_stick_hyperventilations = Column(Integer, default=0)
    daily_quantum_shadow_phasings = Column(Integer, default=0)
    daily_vic20_wisdom_dispensed = Column(Integer, default=0)
    
    # Daily AI health
    daily_ai_incident_count = Column(Integer, default=0)
    daily_ai_incident_type = Column(String)
    daily_ai_incident_reason = Column(String)
    daily_ai_incident_data_quality_score = Column(Float)
    daily_ai_incident_summary = Column(JSON)
    
    # Daily aggregates
    cpu_avg = Column(Float)
    cpu_peak_time = Column(DateTime)
    cpu_peak_value = Column(Float)
    
    memory_avg = Column(Float)
    memory_peak_time = Column(DateTime)
    memory_peak_value = Column(Float)
    
    disk_avg = Column(Float)
    network_bytes_total = Column(Float)
    
    # Pattern detection
    usage_pattern = Column(JSON)  # Peak hours, quiet periods, etc.
    
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
        Index('idx_ai_incident_count', 'daily_ai_incident_count', 'daily_ai_incident_type', 'daily_ai_incident_reason')
    )