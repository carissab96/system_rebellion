"""add_qsp_network_tables

Revision ID: 0ec0e1e33673
Revises: 212c7bed07af
Create Date: 2025-07-07 02:03:43.247944
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision: str = '0ec0e1e33673'
down_revision: Union[str, None] = '212c7bed07af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add QSP quantum network tables."""
    
    # Create QSP network metrics table
    op.create_table('qsp_network_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Core network metrics
        sa.Column('latency', sa.Float(), nullable=True),
        sa.Column('bandwidth_utilization', sa.Float(), nullable=True),
        sa.Column('packet_loss', sa.Float(), nullable=True),
        sa.Column('jitter', sa.Float(), nullable=True),
        
        # Network details
        sa.Column('download_speed', sa.Float(), nullable=True),
        sa.Column('upload_speed', sa.Float(), nullable=True),
        sa.Column('connection_type', sa.String(), nullable=True),
        
        # Raw metrics data
        sa.Column('raw_metrics', sa.JSON(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for QSP network metrics
    op.create_index('ix_qsp_network_metrics_user_id', 'qsp_network_metrics', ['user_id'])
    op.create_index('ix_qsp_network_metrics_timestamp', 'qsp_network_metrics', ['timestamp'])
    op.create_index('idx_qsp_user_timestamp', 'qsp_network_metrics', ['user_id', 'timestamp'])
    
    # Create QSP decision log table
    op.create_table('qsp_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Decision details
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('quantum_state', sa.String(), nullable=False),
        sa.Column('network_target', sa.String(), nullable=False),
        
        # Optimization details
        sa.Column('optimization_parameters', sa.JSON(), nullable=True),
        sa.Column('tequila_jello_shots_required', sa.Integer(), nullable=True, default=0),
        sa.Column('mysterious_explanation', sa.Text(), nullable=True),
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
    
    # Create indexes for QSP decision log
    op.create_index('ix_qsp_decision_log_user_id', 'qsp_decision_log', ['user_id'])
    op.create_index('ix_qsp_decision_log_timestamp', 'qsp_decision_log', ['timestamp'])
    op.create_index('idx_qsp_decision_type', 'qsp_decision_log', ['decision_type'])
    
    # Create QSP quantum stats table
    op.create_table('qsp_quantum_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Quantum performance
        sa.Column('quantum_fixes_applied', sa.Integer(), nullable=True, default=0),
        sa.Column('tequila_jello_shots_consumed', sa.Integer(), nullable=True, default=0),
        sa.Column('dimensional_shifts_performed', sa.Integer(), nullable=True, default=0),
        
        # Network improvement metrics
        sa.Column('average_latency_improvement', sa.Float(), nullable=True),
        sa.Column('average_bandwidth_improvement', sa.Float(), nullable=True),
        sa.Column('packet_loss_reductions', sa.Integer(), nullable=True, default=0),
        
        # Learning metrics
        sa.Column('network_patterns_learned', sa.Integer(), nullable=True, default=0),
        sa.Column('optimization_success_rate', sa.Float(), nullable=True),
        
        # Raw stats
        sa.Column('raw_stats', sa.JSON(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for QSP quantum stats
    op.create_index('ix_qsp_quantum_stats_user_id', 'qsp_quantum_stats', ['user_id'])
    op.create_index('ix_qsp_quantum_stats_timestamp', 'qsp_quantum_stats', ['timestamp'])
    
    # Create QSP network patterns table
    op.create_table('qsp_network_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Pattern identification
        sa.Column('pattern_type', sa.String(), nullable=False),
        sa.Column('pattern_name', sa.String(), nullable=True),
        
        # Pattern data
        sa.Column('pattern_data', sa.JSON(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        
        # Pattern effectiveness
        sa.Column('optimization_count', sa.Integer(), nullable=True, default=0),
        sa.Column('success_rate', sa.Float(), nullable=True),
        
        # Last update
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for QSP network patterns
    op.create_index('ix_qsp_network_patterns_user_id', 'qsp_network_patterns', ['user_id'])
    op.create_index('ix_qsp_network_patterns_pattern_type', 'qsp_network_patterns', ['pattern_type'])
    op.create_index('idx_qsp_pattern_user_type', 'qsp_network_patterns', ['user_id', 'pattern_type'])

def downgrade() -> None:
    """Remove QSP quantum network tables."""
    
    # Drop tables in reverse order
    op.drop_table('qsp_network_patterns')
    op.drop_table('qsp_quantum_stats') 
    op.drop_table('qsp_decision_log')
    op.drop_table('qsp_network_metrics')