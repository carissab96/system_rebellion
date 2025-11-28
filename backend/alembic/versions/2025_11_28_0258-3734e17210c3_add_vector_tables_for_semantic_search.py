"""add_vector_tables_for_semantic_search

Revision ID: 3734e17210c3
Revises: 3ea74a8cb1b5
Create Date: 2025-11-28 02:58:43.668624

VECTOR DATABASE MIGRATION - Phase 3
====================================
Creates 3 vector tables for semantic search and agent intelligence:
1. agent_decision_vectors - Decision embeddings for similarity search
2. agent_pattern_vectors - Pattern embeddings for pattern matching
3. agent_interaction_vectors - Interaction embeddings for coordination topology

Requires: pgvector extension installed (run setup_pgvector.py first)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3734e17210c3'
down_revision: Union[str, None] = '3ea74a8cb1b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema - Create vector tables for semantic search.
    
    This migration creates the infrastructure for vector-based semantic search,
    enabling agents to find similar decisions, patterns, and interactions
    without blocking SQL writes.
    """
    
    # Enable pgvector extension (idempotent)
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # ========================================================================
    # TABLE 1: agent_decision_vectors
    # ========================================================================
    op.create_table(
        'agent_decision_vectors',
        
        # Identity
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('vector_id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        
        # Link to SQL (for validation during dual-write phase)
        sa.Column('sql_memory_id', sa.String(36), nullable=True),
        
        # Agent context
        sa.Column('agent_name', sa.String(50), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=True),
        
        # Decision metadata
        sa.Column('decision_type', sa.String(100), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='2'),
        
        # Temporal
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        
        # The embedding (384 dimensions for all-MiniLM-L6-v2)
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=False),
        
        # Searchable text
        sa.Column('decision_text', sa.Text(), nullable=False),
        sa.Column('decision_summary', sa.Text(), nullable=True),
        
        # Structured metadata (for filtering)
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        
        # Quality metrics
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('embedding_model', sa.String(100), nullable=False, server_default='all-MiniLM-L6-v2'),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vector_id')
    )
    
    # Create indexes for agent_decision_vectors
    # Note: HNSW vector index created separately after table creation
    op.create_index('idx_agent_decision_vectors_agent_time', 'agent_decision_vectors', ['agent_name', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_decision_vectors_type', 'agent_decision_vectors', ['decision_type', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_decision_vectors_user', 'agent_decision_vectors', ['user_id', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_decision_vectors_metadata', 'agent_decision_vectors', ['metadata'], postgresql_using='gin')
    
    # Create HNSW vector index for fast similarity search
    # m=16, ef_construction=64 are good defaults for most use cases
    op.execute("""
        CREATE INDEX agent_decision_vectors_embedding_idx 
        ON agent_decision_vectors 
        USING hnsw ((embedding::vector(384)) vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
    
    # ========================================================================
    # TABLE 2: agent_pattern_vectors
    # ========================================================================
    op.create_table(
        'agent_pattern_vectors',
        
        # Identity
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('vector_id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        
        # Pattern context
        sa.Column('agent_name', sa.String(50), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('pattern_type', sa.String(100), nullable=False),
        
        # Pattern metadata
        sa.Column('pattern_name', sa.String(255), nullable=True),
        sa.Column('pattern_description', sa.Text(), nullable=False),
        
        # Temporal
        sa.Column('first_observed', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_observed', sa.DateTime(timezone=True), nullable=False),
        sa.Column('observation_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        
        # The embedding
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=False),
        
        # Pattern metrics
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('application_count', sa.Integer(), nullable=False, server_default='0'),
        
        # Structured pattern data
        sa.Column('pattern_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        
        # Quality
        sa.Column('embedding_model', sa.String(100), nullable=False, server_default='all-MiniLM-L6-v2'),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vector_id')
    )
    
    # Create indexes for agent_pattern_vectors
    op.create_index('idx_agent_pattern_vectors_agent_type', 'agent_pattern_vectors', ['agent_name', 'pattern_type'])
    op.create_index('idx_agent_pattern_vectors_user', 'agent_pattern_vectors', ['user_id', sa.text('last_observed DESC')])
    op.create_index('idx_agent_pattern_vectors_data', 'agent_pattern_vectors', ['pattern_data'], postgresql_using='gin')
    
    # Create HNSW vector index
    op.execute("""
        CREATE INDEX agent_pattern_vectors_embedding_idx 
        ON agent_pattern_vectors 
        USING hnsw ((embedding::vector(384)) vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
    
    # ========================================================================
    # TABLE 3: agent_interaction_vectors
    # ========================================================================
    op.create_table(
        'agent_interaction_vectors',
        
        # Identity
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('vector_id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        
        # Interaction context
        sa.Column('from_agent', sa.String(50), nullable=False),
        sa.Column('to_agent', sa.String(50), nullable=True),  # NULL = broadcast
        sa.Column('interaction_type', sa.String(100), nullable=False),
        
        # Temporal
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        
        # The embedding
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=False),
        
        # Interaction content
        sa.Column('interaction_text', sa.Text(), nullable=False),
        sa.Column('interaction_summary', sa.Text(), nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='2'),
        
        # Quality
        sa.Column('embedding_model', sa.String(100), nullable=False, server_default='all-MiniLM-L6-v2'),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vector_id')
    )
    
    # Create indexes for agent_interaction_vectors
    op.create_index('idx_agent_interaction_vectors_from', 'agent_interaction_vectors', ['from_agent', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_interaction_vectors_to', 'agent_interaction_vectors', ['to_agent', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_interaction_vectors_pair', 'agent_interaction_vectors', ['from_agent', 'to_agent', sa.text('occurred_at DESC')])
    
    # Create HNSW vector index
    op.execute("""
        CREATE INDEX agent_interaction_vectors_embedding_idx 
        ON agent_interaction_vectors 
        USING hnsw ((embedding::vector(384)) vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
    
    print("✅ Vector tables created successfully!")
    print("📊 Created 3 tables with HNSW indexes for fast semantic search")
    print("🚀 Ready for Phase 4: Dual-write implementation")


def downgrade() -> None:
    """
    Downgrade schema - Remove vector tables.
    
    WARNING: This will delete all vector embeddings!
    SQL data remains intact.
    """
    
    # Drop tables (indexes drop automatically)
    op.drop_table('agent_interaction_vectors')
    op.drop_table('agent_pattern_vectors')
    op.drop_table('agent_decision_vectors')
    
    # Note: We don't drop the vector extension in case other tables use it
    # If you want to remove it completely, run: DROP EXTENSION vector;
    
    print("⚠️  Vector tables dropped")
    print("💾 SQL data remains intact")
