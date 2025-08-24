# app/models/agent_memory.py
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, DateTime, JSON, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import Base  # must exist in your project
from app.core.types import JSONType


class AgentMemory(Base):
    """
    Canonical per-user/per-agent memory log.
    One table for ALL agents. Filter by user_id + agent_name + memory_type.
    """
    __tablename__ = "agent_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    user = relationship("User", back_populates="agent_memories", lazy="joined")
    agent_name = Column(String, index=True, nullable=False)       # e.g. 'sir_hawkington'
    memory_type = Column(String, index=True, nullable=False)      # e.g. 'episodic' | 'pattern' | 'preference'
    content = Column(JSONType, nullable=False)                    # flexible payload
    importance = Column(Integer, default=5)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)

    __table_args__ = (
        Index('ix_mem_user_agent_type_time', 'user_id', 'agent_name', 'memory_type', 'timestamp'),
    )

class AgentGlobalPattern(Base):
    """
    Cross-user/global learned patterns (aggregates, counters, sketches).
    """
    __tablename__ = "agent_global_patterns"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    pattern_key = Column(String, nullable=False, index=True)      # e.g., 'onboarding_drop_step'
    value = Column(JSON, nullable=False)                          # e.g., {'count': 123, 'by_step': {...}}
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
