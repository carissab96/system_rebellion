from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from app.models import Base
from datetime import datetime

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    network_usage = Column(Float)
    process_count = Column(Integer)
    additional_metrics = Column(JSON, nullable=True)

class MetricThresholds(Base):
    __tablename__ = "metric_thresholds"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    metric_type = Column(String)  # 'cpu', 'memory', 'disk', etc.
    threshold_value = Column(Float)
    severity = Column(String)  # 'low', 'medium', 'high', 'critical'