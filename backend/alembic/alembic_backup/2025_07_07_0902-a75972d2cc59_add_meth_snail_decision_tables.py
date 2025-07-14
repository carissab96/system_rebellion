"""add_meth_snail_decision_tables

Revision ID: a75972d2cc59
Revises: 7faf969731c5
Create Date: 2025-07-07 09:02:04.601133
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a75972d2cc59'
down_revision: Union[str, None] = '7faf969731c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Meth Snail's caffeinated optimization decision tables."""
    
    # Create Meth Snail decision log table
    op.create_table('meth_snail_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Decision details
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('energy_level', sa.String(), nullable=False),
        sa.Column('optimization_target', sa.String(), nullable=False),
        
        # Optimization details
        sa.Column('optimization_parameters', sa.JSON(), nullable=True),
        sa.Column('energy_drinks_consumed', sa.Integer(), nullable=True, default=0),
        sa.Column('shell_spinning_required', sa.Boolean(), nullable=True, default=False),
        sa.Column('caffeinated_explanation', sa.Text(), nullable=True),
        sa.Column('technical_details', sa.JSON(), nullable=True),
        
        # Performance metrics
        sa.Column('expected_improvement', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        
        # Success tracking
        sa.Column('optimization_applied', sa.Boolean(), nullable=True, default=False),
        sa.Column('actual_improvement', sa.Float(), nullable=True),
        sa.Column('success_verified', sa.Boolean(), nullable=True, default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for Meth Snail decisions
    op.create_index('ix_meth_snail_decision_log_user_id', 'meth_snail_decision_log', ['user_id'])
    op.create_index('ix_meth_snail_decision_log_timestamp', 'meth_snail_decision_log', ['timestamp'])
    op.create_index('idx_meth_snail_decision_type', 'meth_snail_decision_log', ['decision_type'])
    
    # Create Meth Snail optimization stats table
    op.create_table('meth_snail_optimization_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Optimization performance
        sa.Column('optimizations_performed', sa.Integer(), nullable=True, default=0),
        sa.Column('energy_drinks_consumed', sa.Integer(), nullable=True, default=0),
        sa.Column('shell_spins_executed', sa.Integer(), nullable=True, default=0),
        
        # Caffeinated metrics
        sa.Column('average_optimization_improvement', sa.Float(), nullable=True),
        sa.Column('optimization_success_rate', sa.Float(), nullable=True),
        sa.Column('average_energy_level', sa.Float(), nullable=True),
        
        # Raw stats
        sa.Column('raw_stats', sa.JSON(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for Meth Snail stats
    op.create_index('ix_meth_snail_optimization_stats_user_id', 'meth_snail_optimization_stats', ['user_id'])
    op.create_index('ix_meth_snail_optimization_stats_timestamp', 'meth_snail_optimization_stats', ['timestamp'])

def downgrade() -> None:
    """Remove Meth Snail's decision tables."""
    
    # Drop tables in reverse order
    op.drop_table('meth_snail_optimization_stats')
    op.drop_table('meth_snail_decision_log')