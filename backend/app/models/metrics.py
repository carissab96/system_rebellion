from sqlalchemy import Column, Integer, Float, DateTime, JSON, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.base import Base

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)  # UUID as string, required to match MetricCreate
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    cpu_usage = Column(Float, nullable=False)  # Required field in MetricCreate
    memory_usage = Column(Float, nullable=False)  # Required field in MetricCreate
    disk_usage = Column(Float, nullable=False)  # Required field in MetricCreate
    network = Column(JSON, nullable=True)  # Optional Dict in MetricCreate
    process_count = Column(Integer, nullable=True)  # Optional int in MetricCreate
    additional_metrics = Column(JSON, nullable=True)  # Optional Dict in MetricCreate
    
    # Relationships
    user = relationship("User", back_populates="metrics")