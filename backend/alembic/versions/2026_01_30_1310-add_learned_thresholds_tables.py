"""add learned thresholds tables

Revision ID: a1b2c3d4e5f6
Revises: 9f7a27569c0a
Create Date: 2026-01-30 13:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9f7a27569c0a'
branch_labels = None
depends_on = None


def upgrade():
    # Create threshold_learning_records table
    op.create_table(
        'threshold_learning_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('system_id', sa.String(length=255), nullable=False),
        sa.Column('agent_name', sa.String(length=50), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('threshold_level', sa.String(length=20), nullable=False),
        sa.Column('action_taken', sa.String(length=100), nullable=True),
        sa.Column('outcome_success', sa.Boolean(), nullable=True),
        sa.Column('system_state', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('time_to_critical', sa.Float(), nullable=True),
        sa.Column('was_false_alarm', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('should_have_acted_sooner', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for threshold_learning_records
    op.create_index('ix_threshold_learning_records_id', 'threshold_learning_records', ['id'])
    op.create_index('ix_threshold_learning_records_system_id', 'threshold_learning_records', ['system_id'])
    op.create_index('ix_threshold_learning_records_agent_name', 'threshold_learning_records', ['agent_name'])
    op.create_index('ix_threshold_learning_records_metric_name', 'threshold_learning_records', ['metric_name'])
    op.create_index('ix_threshold_learning_records_created_at', 'threshold_learning_records', ['created_at'])
    op.create_index('idx_system_metric_time', 'threshold_learning_records', ['system_id', 'metric_name', 'created_at'])
    op.create_index('idx_metric_value', 'threshold_learning_records', ['metric_name', 'metric_value'])
    
    # Create action_outcome_records table
    op.create_table(
        'action_outcome_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('pre_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('post_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('metric_pattern_fingerprint', sa.String(length=255), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('improvement', sa.Float(), nullable=False),
        sa.Column('primary_metric', sa.String(length=100), nullable=True),
        sa.Column('severity_score', sa.Float(), nullable=False),
        sa.Column('other_actions_considered', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for action_outcome_records
    op.create_index('ix_action_outcome_records_id', 'action_outcome_records', ['id'])
    op.create_index('ix_action_outcome_records_agent_name', 'action_outcome_records', ['agent_name'])
    op.create_index('ix_action_outcome_records_action', 'action_outcome_records', ['action'])
    op.create_index('ix_action_outcome_records_metric_pattern_fingerprint', 'action_outcome_records', ['metric_pattern_fingerprint'])
    op.create_index('ix_action_outcome_records_success', 'action_outcome_records', ['success'])
    op.create_index('ix_action_outcome_records_created_at', 'action_outcome_records', ['created_at'])
    op.create_index('idx_agent_action_pattern', 'action_outcome_records', ['agent_name', 'action', 'metric_pattern_fingerprint'])
    op.create_index('idx_pattern_success', 'action_outcome_records', ['metric_pattern_fingerprint', 'success'])
    
    # Create metric_pattern_history table
    op.create_table(
        'metric_pattern_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('system_id', sa.String(length=255), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('starting_value', sa.Float(), nullable=False),
        sa.Column('starting_timestamp', sa.TIMESTAMP(), nullable=False),
        sa.Column('value_15min_later', sa.Float(), nullable=True),
        sa.Column('value_30min_later', sa.Float(), nullable=True),
        sa.Column('value_1hr_later', sa.Float(), nullable=True),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('context_fingerprint', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for metric_pattern_history
    op.create_index('ix_metric_pattern_history_id', 'metric_pattern_history', ['id'])
    op.create_index('ix_metric_pattern_history_system_id', 'metric_pattern_history', ['system_id'])
    op.create_index('ix_metric_pattern_history_metric_name', 'metric_pattern_history', ['metric_name'])
    op.create_index('ix_metric_pattern_history_starting_value', 'metric_pattern_history', ['starting_value'])
    op.create_index('ix_metric_pattern_history_starting_timestamp', 'metric_pattern_history', ['starting_timestamp'])
    op.create_index('ix_metric_pattern_history_context_fingerprint', 'metric_pattern_history', ['context_fingerprint'])
    op.create_index('idx_system_metric_value', 'metric_pattern_history', ['system_id', 'metric_name', 'starting_value'])
    op.create_index('idx_context_pattern', 'metric_pattern_history', ['context_fingerprint', 'starting_value'])


def downgrade():
    # Drop metric_pattern_history table and indexes
    op.drop_index('idx_context_pattern', table_name='metric_pattern_history')
    op.drop_index('idx_system_metric_value', table_name='metric_pattern_history')
    op.drop_index('ix_metric_pattern_history_context_fingerprint', table_name='metric_pattern_history')
    op.drop_index('ix_metric_pattern_history_starting_timestamp', table_name='metric_pattern_history')
    op.drop_index('ix_metric_pattern_history_starting_value', table_name='metric_pattern_history')
    op.drop_index('ix_metric_pattern_history_metric_name', table_name='metric_pattern_history')
    op.drop_index('ix_metric_pattern_history_system_id', table_name='metric_pattern_history')
    op.drop_index('ix_metric_pattern_history_id', table_name='metric_pattern_history')
    op.drop_table('metric_pattern_history')
    
    # Drop action_outcome_records table and indexes
    op.drop_index('idx_pattern_success', table_name='action_outcome_records')
    op.drop_index('idx_agent_action_pattern', table_name='action_outcome_records')
    op.drop_index('ix_action_outcome_records_created_at', table_name='action_outcome_records')
    op.drop_index('ix_action_outcome_records_success', table_name='action_outcome_records')
    op.drop_index('ix_action_outcome_records_metric_pattern_fingerprint', table_name='action_outcome_records')
    op.drop_index('ix_action_outcome_records_action', table_name='action_outcome_records')
    op.drop_index('ix_action_outcome_records_agent_name', table_name='action_outcome_records')
    op.drop_index('ix_action_outcome_records_id', table_name='action_outcome_records')
    op.drop_table('action_outcome_records')
    
    # Drop threshold_learning_records table and indexes
    op.drop_index('idx_metric_value', table_name='threshold_learning_records')
    op.drop_index('idx_system_metric_time', table_name='threshold_learning_records')
    op.drop_index('ix_threshold_learning_records_created_at', table_name='threshold_learning_records')
    op.drop_index('ix_threshold_learning_records_metric_name', table_name='threshold_learning_records')
    op.drop_index('ix_threshold_learning_records_agent_name', table_name='threshold_learning_records')
    op.drop_index('ix_threshold_learning_records_system_id', table_name='threshold_learning_records')
    op.drop_index('ix_threshold_learning_records_id', table_name='threshold_learning_records')
    op.drop_table('threshold_learning_records')
