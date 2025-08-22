"""add_missing_agent_decision_tables

Revision ID: d573ad249444
Revises: 9d0c345f9aa9
Create Date: 2025-07-20 13:12:33.271460
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd573ad249444'
down_revision: Union[str, None] = '9d0c345f9aa9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create hawkington_decision_log table
    op.create_table('hawkington_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('monocle_state', sa.String(), nullable=False),
        sa.Column('monitoring_target', sa.String(), nullable=False),
        sa.Column('alert_parameters', sa.JSON(), nullable=True),
        sa.Column('monocle_yeet_required', sa.Boolean(), nullable=True),
        sa.Column('aristocratic_explanation', sa.Text(), nullable=True),
        sa.Column('technical_details', sa.JSON(), nullable=True),
        sa.Column('severity_level', sa.String(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('alert_sent', sa.Boolean(), nullable=True),
        sa.Column('user_acknowledged', sa.Boolean(), nullable=True),
        sa.Column('issue_resolved', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hawkington_decision_log_user_id'), 'hawkington_decision_log', ['user_id'], unique=False)
    op.create_index(op.f('ix_hawkington_decision_log_timestamp'), 'hawkington_decision_log', ['timestamp'], unique=False)
    op.create_index(op.f('ix_hawkington_decision_log_decision_type'), 'hawkington_decision_log', ['decision_type'], unique=False)

    # Create meth_snail_decision_log table
    op.create_table('meth_snail_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('energy_level', sa.String(), nullable=False),
        sa.Column('optimization_target', sa.String(), nullable=False),
        sa.Column('optimization_parameters', sa.JSON(), nullable=True),
        sa.Column('energy_drinks_consumed', sa.Integer(), nullable=True),
        sa.Column('shell_spinning_required', sa.Boolean(), nullable=True),
        sa.Column('caffeinated_explanation', sa.Text(), nullable=True),
        sa.Column('technical_details', sa.JSON(), nullable=True),
        sa.Column('expected_improvement', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('optimization_applied', sa.Boolean(), nullable=True),
        sa.Column('actual_improvement', sa.Float(), nullable=True),
        sa.Column('success_verified', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meth_snail_decision_log_user_id'), 'meth_snail_decision_log', ['user_id'], unique=False)
    op.create_index(op.f('ix_meth_snail_decision_log_timestamp'), 'meth_snail_decision_log', ['timestamp'], unique=False)
    op.create_index(op.f('ix_meth_snail_decision_log_decision_type'), 'meth_snail_decision_log', ['decision_type'], unique=False)

    # Create hamsters_decision_log table
    op.create_table('hamsters_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('beer_level', sa.String(), nullable=False),
        sa.Column('engineering_target', sa.String(), nullable=False),
        sa.Column('engineering_parameters', sa.JSON(), nullable=True),
        sa.Column('beer_consumed', sa.Integer(), nullable=True),
        sa.Column('duct_tape_used', sa.Boolean(), nullable=True),
        sa.Column('supply_closet_raids', sa.Integer(), nullable=True),
        sa.Column('beer_powered_explanation', sa.Text(), nullable=True),
        sa.Column('technical_details', sa.JSON(), nullable=True),
        sa.Column('redneck_ingenuity_level', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('urgency_level', sa.String(), nullable=True),
        sa.Column('priority_level', sa.String(), nullable=True),
        sa.Column('solution_applied', sa.Boolean(), nullable=True),
        sa.Column('actual_improvement', sa.Float(), nullable=True),
        sa.Column('success_verified', sa.Boolean(), nullable=True),
        sa.Column('beer_level_after', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hamsters_decision_log_user_id'), 'hamsters_decision_log', ['user_id'], unique=False)
    op.create_index(op.f('ix_hamsters_decision_log_timestamp'), 'hamsters_decision_log', ['timestamp'], unique=False)
    op.create_index(op.f('ix_hamsters_decision_log_decision_type'), 'hamsters_decision_log', ['decision_type'], unique=False)

    # Create agent_performance_summary table
    op.create_table('agent_performance_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('agent_name', sa.String(), nullable=False),
        sa.Column('total_decisions', sa.Integer(), nullable=True),
        sa.Column('successful_decisions', sa.Integer(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('average_confidence', sa.Float(), nullable=True),
        sa.Column('last_decision_timestamp', sa.DateTime(), nullable=True),
        sa.Column('performance_stats', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_performance_summary_user_id'), 'agent_performance_summary', ['user_id'], unique=False)
    op.create_index(op.f('ix_agent_performance_summary_agent_name'), 'agent_performance_summary', ['agent_name'], unique=False)

    # Create cross_agent_coordination table
    op.create_table('cross_agent_coordination',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('primary_agent', sa.String(), nullable=False),
        sa.Column('supporting_agents', sa.JSON(), nullable=True),
        sa.Column('coordination_type', sa.String(), nullable=False),
        sa.Column('coordination_success', sa.Boolean(), nullable=True),
        sa.Column('coordination_details', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cross_agent_coordination_user_id'), 'cross_agent_coordination', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_index(op.f('ix_cross_agent_coordination_user_id'), table_name='cross_agent_coordination')
    op.drop_table('cross_agent_coordination')
    
    op.drop_index(op.f('ix_agent_performance_summary_agent_name'), table_name='agent_performance_summary')
    op.drop_index(op.f('ix_agent_performance_summary_user_id'), table_name='agent_performance_summary')
    op.drop_table('agent_performance_summary')
    
    op.drop_index(op.f('ix_hamsters_decision_log_decision_type'), table_name='hamsters_decision_log')
    op.drop_index(op.f('ix_hamsters_decision_log_timestamp'), table_name='hamsters_decision_log')
    op.drop_index(op.f('ix_hamsters_decision_log_user_id'), table_name='hamsters_decision_log')
    op.drop_table('hamsters_decision_log')
    
    op.drop_index(op.f('ix_meth_snail_decision_log_decision_type'), table_name='meth_snail_decision_log')
    op.drop_index(op.f('ix_meth_snail_decision_log_timestamp'), table_name='meth_snail_decision_log')
    op.drop_index(op.f('ix_meth_snail_decision_log_user_id'), table_name='meth_snail_decision_log')
    op.drop_table('meth_snail_decision_log')
    
    op.drop_index(op.f('ix_hawkington_decision_log_decision_type'), table_name='hawkington_decision_log')
    op.drop_index(op.f('ix_hawkington_decision_log_timestamp'), table_name='hawkington_decision_log')
    op.drop_index(op.f('ix_hawkington_decision_log_user_id'), table_name='hawkington_decision_log')
    op.drop_table('hawkington_decision_log')
