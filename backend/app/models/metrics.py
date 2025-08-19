from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import func
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