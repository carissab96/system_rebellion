from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, Boolean
from app.models import Base
from datetime import datetime
import enum

class AlertSeverity(enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class SystemAlert(Base):
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    metric_type = Column(String)  # 'cpu', 'memory', 'disk', etc.
    severity = Column(Enum(AlertSeverity))
    message = Column(String)
    additional_data = Column(JSON, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)