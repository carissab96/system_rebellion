# app/models/metrics_aggregates.py
from sqlalchemy import Column, Integer, Float, DateTime, String, JSON, Index
from app.core.base import Base
from datetime import datetime

class MetricsHourly(Base):
    """Hourly aggregated metrics - The Meth Snail's first optimization layer"""
    __tablename__ = "metrics_hourly"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    hour_start = Column(DateTime, nullable=False, index=True)
    
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
    
    # Daily aggregates
    cpu_avg = Column(Float)
    cpu_peak_time = Column(DateTime)
    cpu_peak_value = Column(Float)
    
    memory_avg = Column(Float)
    memory_peak_time = Column(DateTime)
    memory_peak_value = Column(Float)
    
    disk_avg = Column(Float)
    network_bytes_total = Column(Float)
    
    # AI Summary for the day
    ai_summary = Column(JSON)  # Sir Hawkington's daily report
    total_concerns = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)
    
    # Pattern detection
    usage_pattern = Column(JSON)  # Peak hours, quiet periods, etc.
    
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
    )