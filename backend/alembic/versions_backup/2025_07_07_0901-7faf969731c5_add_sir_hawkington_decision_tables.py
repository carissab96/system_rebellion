"""add_sir_hawkington_decision_tables

Revision ID: 7faf969731c5
Revises: 0ec0e1e33673
Create Date: 2025-07-07 09:01:40.320327
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7faf969731c5'
down_revision: Union[str, None] = '0ec0e1e33673'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Sir Hawkington's aristocratic monitoring decision tables."""
    
    # Create Hawkington decision log table
    op.create_table('hawkington_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Decision details
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('monocle_state', sa.String(), nullable=False),
        sa.Column('monitoring_target', sa.String(), nullable=False),
        
        # Alert details
        sa.Column('alert_parameters', sa.JSON(), nullable=True),
        sa.Column('monocle_yeet_required', sa.Boolean(), nullable=True, default=False),
        sa.Column('aristocratic_explanation', sa.Text(), nullable=True),
        sa.Column('technical_details', sa.JSON(), nullable=True),
        
        # Performance metrics
        sa.Column('severity_level', sa.String(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        
        # Success tracking
        sa.Column('alert_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('user_acknowledged', sa.Boolean(), nullable=True, default=False),
        sa.Column('issue_resolved', sa.Boolean(), nullable=True, default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for Hawkington decisions
    op.create_index('ix_hawkington_decision_log_user_id', 'hawkington_decision_log', ['user_id'])
    op.create_index('ix_hawkington_decision_log_timestamp', 'hawkington_decision_log', ['timestamp'])
    op.create_index('idx_hawkington_decision_type', 'hawkington_decision_log', ['decision_type'])
    
    # Create Hawkington monitoring stats table
    op.create_table('hawkington_monitoring_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Monitoring performance
        sa.Column('alerts_generated', sa.Integer(), nullable=True, default=0),
        sa.Column('monocle_yeets_performed', sa.Integer(), nullable=True, default=0),
        sa.Column('critical_issues_detected', sa.Integer(), nullable=True, default=0),
        
        # Aristocratic metrics
        sa.Column('monitoring_precision', sa.Float(), nullable=True),
        sa.Column('alert_accuracy_rate', sa.Float(), nullable=True),
        sa.Column('user_response_time', sa.Float(), nullable=True),
        
        # Raw stats
        sa.Column('raw_stats', sa.JSON(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for Hawkington stats
    op.create_index('ix_hawkington_monitoring_stats_user_id', 'hawkington_monitoring_stats', ['user_id'])
    op.create_index('ix_hawkington_monitoring_stats_timestamp', 'hawkington_monitoring_stats', ['timestamp'])

def downgrade() -> None:
    """Remove Sir Hawkington's decision tables."""
    
    # Drop tables in reverse order
    op.drop_table('hawkington_monitoring_stats')
    op.drop_table('hawkington_decision_log')