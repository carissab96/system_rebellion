from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from app.models import Base
from datetime import datetime

class SystemConfiguration(Base):
    __tablename__ = "system_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    config_key = Column(String, nullable=False)
    config_value = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


