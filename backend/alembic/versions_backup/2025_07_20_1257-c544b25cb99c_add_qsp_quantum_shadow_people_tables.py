"""Add QSP (Quantum Shadow People) tables

Revision ID: c544b25cb99c
Revises: 2d1f221c727c
Create Date: 2025-07-20 12:57:04.672418
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c544b25cb99c'
down_revision: Union[str, None] = '2d1f221c727c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create QSP (Quantum Shadow People) tables."""
    
    # Create QSP Network Metrics table
    op.create_table('qsp_network_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('latency', sa.Float(), nullable=True),
        sa.Column('bandwidth_utilization', sa.Float(), nullable=True),
        sa.Column('packet_loss', sa.Float(), nullable=True),
        sa.Column('jitter', sa.Float(), nullable=True),
        sa.Column('download_speed', sa.Float(), nullable=True),
        sa.Column('upload_speed', sa.Float(), nullable=True),
        sa.Column('connection_type', sa.String(), nullable=True),
        sa.Column('raw_metrics', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_qsp_network_metrics_user_id'), 'qsp_network_metrics', ['user_id'], unique=False)
    op.create_index(op.f('ix_qsp_network_metrics_timestamp'), 'qsp_network_metrics', ['timestamp'], unique=False)
    
    # Create QSP Decision Log table
    op.create_table('qsp_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('quantum_state', sa.String(), nullable=False),
        sa.Column('network_target', sa.String(), nullable=False),
        sa.Column('optimization_parameters', sa.JSON(), nullable=True),
        sa.Column('tequila_jello_shots_required', sa.Integer(), nullable=True),
        sa.Column('mysterious_explanation', sa.Text(), nullable=True),
        sa.Column('technical_details', sa.JSON(), nullable=True),
        sa.Column('expected_improvement', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('optimization_applied', sa.Boolean(), nullable=True),
        sa.Column('actual_improvement', sa.Float(), nullable=True),
        sa.Column('success_verified', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_qsp_decision_log_user_id'), 'qsp_decision_log', ['user_id'], unique=False)
    op.create_index(op.f('ix_qsp_decision_log_timestamp'), 'qsp_decision_log', ['timestamp'], unique=False)
    op.create_index(op.f('ix_qsp_decision_log_decision_type'), 'qsp_decision_log', ['decision_type'], unique=False)
    
    # Create QSP Quantum Stats table
    op.create_table('qsp_quantum_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('quantum_fixes_applied', sa.Integer(), nullable=True),
        sa.Column('tequila_jello_shots_consumed', sa.Integer(), nullable=True),
        sa.Column('dimensional_shifts_performed', sa.Integer(), nullable=True),
        sa.Column('average_latency_improvement', sa.Float(), nullable=True),
        sa.Column('average_bandwidth_improvement', sa.Float(), nullable=True),
        sa.Column('packet_loss_reductions', sa.Integer(), nullable=True),
        sa.Column('network_patterns_learned', sa.Integer(), nullable=True),
        sa.Column('optimization_success_rate', sa.Float(), nullable=True),
        sa.Column('raw_stats', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_qsp_quantum_stats_user_id'), 'qsp_quantum_stats', ['user_id'], unique=False)
    op.create_index(op.f('ix_qsp_quantum_stats_timestamp'), 'qsp_quantum_stats', ['timestamp'], unique=False)
    
    # Create QSP Network Patterns table
    op.create_table('qsp_network_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('pattern_type', sa.String(), nullable=False),
        sa.Column('pattern_name', sa.String(), nullable=True),
        sa.Column('pattern_data', sa.JSON(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('optimization_count', sa.Integer(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_qsp_network_patterns_user_id'), 'qsp_network_patterns', ['user_id'], unique=False)
    op.create_index(op.f('ix_qsp_network_patterns_pattern_type'), 'qsp_network_patterns', ['pattern_type'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Remove QSP tables."""
    op.drop_table('qsp_network_patterns')
    op.drop_table('qsp_quantum_stats')
    op.drop_table('qsp_decision_log')
    op.drop_table('qsp_network_metrics')
