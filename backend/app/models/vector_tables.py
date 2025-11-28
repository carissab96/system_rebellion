"""
Vector Database Tables for Semantic Search
===========================================

SQLAlchemy models for pgvector-powered semantic search tables.
These store embeddings of agent decisions, patterns, and interactions.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import UserDefinedType
from app.core.base import Base
from datetime import datetime, timezone
import uuid


class Vector(UserDefinedType):
    """Custom SQLAlchemy type for pgvector"""
    cache_ok = True
    
    def __init__(self, dim=384):
        self.dim = dim
    
    def get_col_spec(self):
        return f"vector({self.dim})"
    
    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return value
            # Convert list to pgvector format
            if isinstance(value, list):
                return f"[{','.join(str(x) for x in value)}]"
            return value
        return process
    
    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return value
            # Parse pgvector format to list
            if isinstance(value, str):
                return [float(x) for x in value.strip('[]').split(',')]
            return value
        return process


class AgentDecisionVectors(Base):
    """
    Vector embeddings of agent decisions for semantic search.
    Enables finding similar past decisions across all agents.
    """
    __tablename__ = "agent_decision_vectors"
    
    # Primary key
    vector_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Agent and decision metadata
    agent_name = Column(String, nullable=False, index=True)
    decision_type = Column(String, nullable=False, index=True)
    decision_text = Column(String, nullable=False)  # Searchable text representation
    
    # Vector embedding (384 dimensions for all-MiniLM-L6-v2)
    embedding = Column(Vector(384), nullable=False)
    
    # Temporal data
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # User context
    user_id = Column(String, nullable=False, index=True)
    
    # Decision context
    event_type = Column(String, nullable=True)
    priority = Column(Integer, nullable=True)
    context_metadata = Column("metadata", JSON, nullable=True)
    
    # Link back to SQL tables
    sql_memory_id = Column(String, nullable=True)  # UUID of central_memory_bank entry
    
    # Decision quality metrics
    confidence_score = Column(Float, nullable=True)
    decision_summary = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # HNSW index for fast similarity search
    __table_args__ = (
        Index(
            'idx_decision_vectors_hnsw',
            'embedding',
            postgresql_using='hnsw',
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
        Index('idx_decision_agent_time', 'agent_name', 'occurred_at'),
        Index('idx_decision_user_time', 'user_id', 'occurred_at'),
    )


class AgentPatternVectors(Base):
    """
    Vector embeddings of learned patterns for pattern matching.
    Enables finding similar behavioral patterns across time and agents.
    """
    __tablename__ = "agent_pattern_vectors"
    
    # Primary key
    vector_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Pattern metadata
    agent_name = Column(String, nullable=False, index=True)
    pattern_type = Column(String, nullable=False, index=True)
    pattern_text = Column(String, nullable=False)  # Searchable text representation
    
    # Vector embedding
    embedding = Column(Vector(384), nullable=False)
    
    # Temporal data
    first_observed = Column(DateTime(timezone=True), nullable=False)
    last_observed = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # User context
    user_id = Column(String, nullable=False, index=True)
    
    # Pattern strength
    occurrence_count = Column(Integer, default=1)
    confidence_score = Column(Float, nullable=True)
    
    # Pattern details
    context_metadata = Column("metadata", JSON, nullable=True)
    pattern_summary = Column(String, nullable=True)
    
    # Link to learning tables
    sql_pattern_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # HNSW index
    __table_args__ = (
        Index(
            'idx_pattern_vectors_hnsw',
            'embedding',
            postgresql_using='hnsw',
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
        Index('idx_pattern_agent_time', 'agent_name', 'last_observed'),
        Index('idx_pattern_user_time', 'user_id', 'last_observed'),
    )


class AgentInteractionVectors(Base):
    """
    Vector embeddings of agent interactions for relationship analysis.
    Enables finding similar multi-agent coordination patterns.
    """
    __tablename__ = "agent_interaction_vectors"
    
    # Primary key
    vector_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Interaction metadata
    primary_agent = Column(String, nullable=False, index=True)
    secondary_agent = Column(String, nullable=False, index=True)
    interaction_type = Column(String, nullable=False, index=True)
    interaction_text = Column(String, nullable=False)  # Searchable text representation
    
    # Vector embedding
    embedding = Column(Vector(384), nullable=False)
    
    # Temporal data
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # User context
    user_id = Column(String, nullable=False, index=True)
    
    # Interaction outcome
    outcome = Column(String, nullable=True)
    success_score = Column(Float, nullable=True)
    
    # Interaction details
    context_metadata = Column("metadata", JSON, nullable=True)
    interaction_summary = Column(String, nullable=True)
    
    # Link to SQL tables
    sql_interaction_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # HNSW index
    __table_args__ = (
        Index(
            'idx_interaction_vectors_hnsw',
            'embedding',
            postgresql_using='hnsw',
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
        Index('idx_interaction_agents_time', 'primary_agent', 'secondary_agent', 'occurred_at'),
        Index('idx_interaction_user_time', 'user_id', 'occurred_at'),
    )
