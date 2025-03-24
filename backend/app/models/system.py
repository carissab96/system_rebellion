from sqlalchemy import Column, String, Boolean, JSON, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.base import Base
from datetime import datetime
import uuid
import enum

class ConfigType(enum.Enum):
    NETWORK = 'NETWORK'
    SYSTEM = 'SYSTEM'
    SECURITY = 'SECURITY'
    PERFORMANCE = 'PERFORMANCE'

class SystemConfiguration(Base):
    __tablename__ = "system_configurations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    config_type = Column(Enum(ConfigType), nullable=False)
    settings = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship with User
    user = relationship("User", back_populates="configurations")

class OptimizationProfile(Base):
    __tablename__ = "optimization_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    settings = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with User
    user = relationship("User", back_populates="optimization_profiles")