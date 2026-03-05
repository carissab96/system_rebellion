"""
Vector Database Tables for Semantic Search
===========================================

SQLAlchemy models for pgvector-powered semantic search tables.
These store embeddings of agent decisions, patterns, and interactions.
"""

from sqlalchemy import Column, String, Integer, BigInteger, Float, DateTime, JSON, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    embedding_model = Column(String(100), nullable=False, default='all-MiniLM-L6-v2')
    
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
    
    # Primary key - matches database schema
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    vector_id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    
    # Pattern metadata
    agent_name = Column(String(50), nullable=False, index=True)
    user_id = Column(String(255), nullable=True)
    pattern_type = Column(String(100), nullable=False, index=True)
    pattern_name = Column(String(255), nullable=True)
    pattern_description = Column(Text, nullable=False)
    
    # Temporal data
    first_observed = Column(DateTime(timezone=True), nullable=False)
    last_observed = Column(DateTime(timezone=True), nullable=False, index=True)
    observation_count = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Vector embedding
    embedding = Column(Vector(384), nullable=False)
    
    # Pattern effectiveness tracking
    confidence_score = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)
    application_count = Column(Integer, nullable=False, default=0)
    
    # Pattern details
    pattern_data = Column(JSONB, nullable=False)
    embedding_model = Column(String(100), nullable=False, default='all-MiniLM-L6-v2')
    
    # HNSW index and other indexes
    __table_args__ = (
        Index(
            'agent_pattern_vectors_embedding_idx',
            'embedding',
            postgresql_using='hnsw',
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
        Index('idx_agent_pattern_vectors_agent_type', 'agent_name', 'pattern_type'),
        Index('idx_agent_pattern_vectors_user', 'user_id', 'last_observed'),
        Index('idx_agent_pattern_vectors_data', 'pattern_data', postgresql_using='gin'),
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
