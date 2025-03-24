from sqlalchemy import Column, Integer, Float, DateTime, JSON
from datetime import datetime
from app.core.base import Base

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    network_usage = Column(JSON)
    process_count = Column(Integer)
    additional_metrics = Column(JSON, nullable=True)