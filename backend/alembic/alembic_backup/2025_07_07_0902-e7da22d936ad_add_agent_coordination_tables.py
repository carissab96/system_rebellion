"""add_agent_coordination_tables

Revision ID: e7da22d936ad
Revises: a75972d2cc59
Create Date: 2025-07-07 09:02:42.796077
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7da22d936ad'
down_revision: Union[str, None] = 'a75972d2cc59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# revision identifiers, used by Alembic.
revision: str = '[keep_auto_generated]'
down_revision: Union[str, None] = '[meth_snail_revision_id]'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Add The Hamsters' beer-powered engineering decision tables."""
    
    # Create Hamsters decision log table
    op.create_table('hamsters_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Decision details
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('beer_level', sa.String(), nullable=False),
        sa.Column('engineering_target', sa.String(), nullable=False),
        
        # Engineering details
        sa.Column('engineering_parameters', sa.JSON(), nullable=True),
        sa.Column('beer_consumed', sa.Integer(), nullable=True, default=0),
        sa.Column('duct_tape_used', sa.Boolean(), nullable=True, default=False),
        sa.Column('supply_closet_raids', sa.Integer(), nullable=True, default=0),
        sa.Column('beer_powered_explanation', sa.Text(), nullable=True),
        sa.Column('technical_details', sa.JSON(), nullable=True),
        
        # Engineering metrics
        sa.Column('redneck_ingenuity_level', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('urgency_level', sa.String(), nullable=True),
        sa.Column('priority_level', sa.String(), nullable=True),
        
        # Success tracking
        sa.Column('solution_applied', sa.Boolean(), nullable=True, default=False),
        sa.Column('actual_improvement', sa.Float(), nullable=True),
        sa.Column('success_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('beer_level_after', sa.String(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for Hamsters decisions
    op.create_index('ix_hamsters_decision_log_user_id', 'hamsters_decision_log', ['user_id'])
    op.create_index('ix_hamsters_decision_log_timestamp', 'hamsters_decision_log', ['timestamp'])
    op.create_index('idx_hamsters_decision_type', 'hamsters_decision_log', ['decision_type'])
    
    # Create Hamsters engineering stats table
    op.create_table('hamsters_engineering_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Engineering performance
        sa.Column('engineering_solutions_deployed', sa.Integer(), nullable=True, default=0),
        sa.Column('beer_consumed_total', sa.Integer(), nullable=True, default=0),
        sa.Column('duct_tape_rolls_used', sa.Integer(), nullable=True, default=0),
        sa.Column('supply_closet_raids_total', sa.Integer(), nullable=True, default=0),
        
        # Beer-powered metrics
        sa.Column('average_redneck_ingenuity', sa.Float(), nullable=True),
        sa.Column('engineering_success_rate', sa.Float(), nullable=True),
        sa.Column('average_beer_efficiency', sa.Float(), nullable=True),
        
        # Raw stats
        sa.Column('raw_stats', sa.JSON(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for Hamsters stats
    op.create_index('ix_hamsters_engineering_stats_user_id', 'hamsters_engineering_stats', ['user_id'])
    op.create_index('ix_hamsters_engineering_stats_timestamp', 'hamsters_engineering_stats', ['timestamp'])

def downgrade() -> None:
    """Remove The Hamsters' decision tables."""
    
    # Drop tables in reverse order
    op.drop_table('cross_agent_coordination')
    op.drop_table('agent_performance_summary')