from sqlalchemy import Column, String, DateTime, JSON, Enum, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.base import Base
from datetime import datetime
import enum
import uuid

class AlertSeverity(enum.Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'

class SystemAlert(Base):
    __tablename__ = "system_alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    timestamp = Column(DateTime, default=datetime.now)
    is_read = Column(Boolean, default=False)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with User
    user = relationship("User", back_populates="alerts")