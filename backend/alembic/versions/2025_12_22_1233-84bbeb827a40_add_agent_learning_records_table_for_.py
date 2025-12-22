"""add agent_learning_records table for terry v2

Revision ID: 84bbeb827a40
Revises: 9e60a1bdc15d
Create Date: 2025-12-22 12:33:11.008619
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84bbeb827a40'
down_revision: Union[str, None] = '9e60a1bdc15d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create agent_learning_records table for Terry v2 agentic learning."""
    op.create_table(
        'agent_learning_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(length=50), nullable=False),
        
        # Hierarchical fingerprints (3 levels for fallback matching)
        sa.Column('fingerprint_l1', sa.String(length=50), nullable=False),
        sa.Column('fingerprint_l2', sa.String(length=100), nullable=False),
        sa.Column('fingerprint_l3', sa.String(length=150), nullable=False),
        
        # Situation context
        sa.Column('resource_type', sa.String(length=20), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('root_cause', sa.String(length=50), nullable=True),
        sa.Column('process_category', sa.String(length=20), nullable=True),
        
        # Action taken
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('followed_vic20', sa.Boolean(), nullable=True, server_default='false'),
        
        # Outcome
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('improvement', sa.JSON(), nullable=True),
        sa.Column('what_worked', sa.String(), nullable=True),
        sa.Column('what_failed', sa.String(), nullable=True),
        
        # Metadata
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for hierarchical querying (most specific to least specific)
    op.create_index('idx_fingerprint_l3', 'agent_learning_records', ['fingerprint_l3'])
    op.create_index('idx_fingerprint_l2', 'agent_learning_records', ['fingerprint_l2'])
    op.create_index('idx_fingerprint_l1', 'agent_learning_records', ['fingerprint_l1'])
    
    # Create indexes for analysis
    op.create_index('idx_agent_action', 'agent_learning_records', ['agent_name', 'action'])
    op.create_index('idx_success', 'agent_learning_records', ['success'])
    op.create_index('idx_process_category', 'agent_learning_records', ['process_category'])
    op.create_index('idx_created', 'agent_learning_records', ['created_at'])
    
    # Composite index for common query pattern
    op.create_index('idx_agent_fingerprint_success', 'agent_learning_records', 
                    ['agent_name', 'fingerprint_l3', 'success'])


def downgrade() -> None:
    """Drop agent_learning_records table."""
    op.drop_index('idx_agent_fingerprint_success', table_name='agent_learning_records')
    op.drop_index('idx_created', table_name='agent_learning_records')
    op.drop_index('idx_process_category', table_name='agent_learning_records')
    op.drop_index('idx_success', table_name='agent_learning_records')
    op.drop_index('idx_agent_action', table_name='agent_learning_records')
    op.drop_index('idx_fingerprint_l1', table_name='agent_learning_records')
    op.drop_index('idx_fingerprint_l2', table_name='agent_learning_records')
    op.drop_index('idx_fingerprint_l3', table_name='agent_learning_records')
    op.drop_table('agent_learning_records')
