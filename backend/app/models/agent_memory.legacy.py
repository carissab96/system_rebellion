from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime, timezone
from app.core.base import Base

class AgentGlobalPattern(Base):
    __tablename__ = "agent_global_patterns"

    agent_name = Column(String, primary_key=True)
    pattern_key = Column(String, primary_key=True)
    value = Column(JSON)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
