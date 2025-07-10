"""add_agent_coordination_tables

Revision ID: fff018551e97
Revises: 633cccd31585
Create Date: 2025-07-07 10:09:59.581150
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fff018551e97'
down_revision: Union[str, None] = '633cccd31585'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add agent coordination and cross-agent performance tables."""
    
    # Create Agent Performance Summary table
    op.create_table('agent_performance_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Agent performance metrics
        sa.Column('agent_name', sa.String(), nullable=False),
        sa.Column('total_decisions', sa.Integer(), nullable=True, default=0),
        sa.Column('successful_decisions', sa.Integer(), nullable=True, default=0),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('average_confidence', sa.Float(), nullable=True),
        sa.Column('last_decision_timestamp', sa.DateTime(), nullable=True),
        
        # Performance stats
        sa.Column('performance_stats', sa.JSON(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for agent performance
    op.create_index('ix_agent_performance_summary_user_id', 'agent_performance_summary', ['user_id'])
    op.create_index('ix_agent_performance_summary_agent_name', 'agent_performance_summary', ['agent_name'])
    op.create_index('idx_agent_performance_user_agent', 'agent_performance_summary', ['user_id', 'agent_name'])
    
    # Create Cross Agent Coordination table
    op.create_table('cross_agent_coordination',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Coordination details
        sa.Column('primary_agent', sa.String(), nullable=False),
        sa.Column('supporting_agents', sa.JSON(), nullable=True),
        sa.Column('coordination_type', sa.String(), nullable=False),
        
        # Coordination results
        sa.Column('coordination_success', sa.Boolean(), nullable=True, default=False),
        sa.Column('coordination_details', sa.JSON(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for cross agent coordination
    op.create_index('ix_cross_agent_coordination_user_id', 'cross_agent_coordination', ['user_id'])
    op.create_index('ix_cross_agent_coordination_timestamp', 'cross_agent_coordination', ['timestamp'])
    op.create_index('idx_cross_agent_primary', 'cross_agent_coordination', ['primary_agent'])

def downgrade() -> None:
    """Remove agent coordination tables."""
    
    # Drop tables in reverse order
    op.drop_table('cross_agent_coordination')
    op.drop_table('agent_performance_summary')