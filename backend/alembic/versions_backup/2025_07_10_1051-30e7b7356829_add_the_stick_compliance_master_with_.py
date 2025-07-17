"""Add The Stick - Compliance Master with Eidetic Memory and Trauma Management

Revision ID: 30e7b7356829
Revises: fff018551e97
Create Date: 2025-07-10 10:51:11.274421
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30e7b7356829'
down_revision: Union[str, None] = 'fff018551e97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add The Stick's tables only."""
    
    # Create The Stick's User Patterns table - Eidetic Memory Storage
    op.create_table('stick_user_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('observation_count', sa.Integer(), default=0),
        sa.Column('learned_patterns', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), default=0.0),
        sa.Column('first_observation', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_observation', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('pattern_complexity', sa.Float(), default=0.0),
        sa.Column('learning_stage', sa.String(), default='initial_observation'),
        sa.Column('eidetic_memory_active', sa.Boolean(), default=False),
        sa.Column('primary_activities', sa.JSON(), nullable=True),
        sa.Column('time_based_patterns', sa.JSON(), nullable=True),
        sa.Column('configuration_preferences', sa.JSON(), nullable=True),
        sa.Column('stick_observations', sa.Text(), nullable=True),
        sa.Column('anomaly_detections', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stick_user_patterns_user_id', 'stick_user_patterns', ['user_id'])
    
    # Create The Stick's Decision Log - Complete Audit Trail
    op.create_table('stick_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('compliance_state', sa.String(), nullable=False),
        sa.Column('configuration_target', sa.String(), nullable=False),
        sa.Column('optimization_parameters', sa.JSON(), nullable=False),
        sa.Column('user_pattern_confidence', sa.Float(), nullable=False),
        sa.Column('compliance_explanation', sa.Text(), nullable=False),
        sa.Column('technical_details', sa.JSON(), nullable=False),
        sa.Column('expected_improvement', sa.Float(), nullable=False),
        sa.Column('confidence_level', sa.Float(), nullable=False),
        sa.Column('actual_improvement', sa.Float(), nullable=True),
        sa.Column('success_verified', sa.Boolean(), default=False),
        sa.Column('stick_anxiety_level', sa.String(), default='manageable'),
        sa.Column('trauma_triggers', sa.JSON(), nullable=True),
        sa.Column('paper_bag_used', sa.Boolean(), default=False),
        sa.Column('implemented', sa.Boolean(), default=False),
        sa.Column('implementation_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('implementation_notes', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stick_decision_log_user_id', 'stick_decision_log', ['user_id'])
    op.create_index('ix_stick_decision_log_timestamp', 'stick_decision_log', ['timestamp'])
    op.create_index('idx_stick_decision_type', 'stick_decision_log', ['decision_type'])
    
    # Create The Stick's Compliance History - OCD Violation Tracking
    op.create_table('stick_compliance_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('violation_type', sa.String(), nullable=False),
        sa.Column('measured_value', sa.Float(), nullable=False),
        sa.Column('threshold_value', sa.Float(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('recommendation', sa.String(), nullable=False),
        sa.Column('compliance_action_taken', sa.String(), nullable=True),
        sa.Column('resolved', sa.Boolean(), default=False),
        sa.Column('resolution_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recurring_violation', sa.Boolean(), default=False),
        sa.Column('violation_frequency', sa.Integer(), default=1),
        sa.Column('user_pattern_related', sa.Boolean(), default=False),
        sa.Column('triggered_ptsd', sa.Boolean(), default=False),
        sa.Column('anxiety_level_during', sa.String(), default='manageable'),
        sa.Column('proctologist_flashback', sa.Boolean(), default=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stick_compliance_history_user_id', 'stick_compliance_history', ['user_id'])
    op.create_index('ix_stick_compliance_history_timestamp', 'stick_compliance_history', ['timestamp'])
    
    # Create The Stick's Configuration Profiles - Learned Configurations
    op.create_table('stick_configuration_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('profile_name', sa.String(), nullable=False),
        sa.Column('activity_type', sa.String(), nullable=False),
        sa.Column('configuration_parameters', sa.JSON(), nullable=False),
        sa.Column('usage_confidence', sa.Float(), nullable=False),
        sa.Column('performance_metrics', sa.JSON(), nullable=True),
        sa.Column('created_from_pattern', sa.Boolean(), default=True),
        sa.Column('times_applied', sa.Integer(), default=0),
        sa.Column('success_rate', sa.Float(), default=0.0),
        sa.Column('user_satisfaction_score', sa.Float(), nullable=True),
        sa.Column('time_patterns', sa.JSON(), nullable=True),
        sa.Column('context_triggers', sa.JSON(), nullable=True),
        sa.Column('stick_profile_notes', sa.Text(), nullable=True),
        sa.Column('optimization_history', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_used', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_optimized', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stick_configuration_profiles_user_id', 'stick_configuration_profiles', ['user_id'])
    op.create_index('idx_stick_profile_user_activity', 'stick_configuration_profiles', ['user_id', 'activity_type'])
    
    # Create The Stick's Anxiety Log - Mental Health Tracking
    op.create_table('stick_anxiety_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('anxiety_level', sa.String(), nullable=False),
        sa.Column('trigger_type', sa.String(), nullable=True),
        sa.Column('trigger_details', sa.JSON(), nullable=True),
        sa.Column('ptsd_triggered', sa.Boolean(), default=False),
        sa.Column('trauma_type', sa.String(), nullable=True),
        sa.Column('hyperventilation_occurred', sa.Boolean(), default=False),
        sa.Column('paper_bag_used', sa.Boolean(), default=False),
        sa.Column('recovery_time_seconds', sa.Integer(), nullable=True),
        sa.Column('recovery_method', sa.String(), nullable=True),
        sa.Column('channeled_into_productivity', sa.Boolean(), default=False),
        sa.Column('system_state_during', sa.JSON(), nullable=True),
        sa.Column('other_agents_active', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stick_anxiety_log_timestamp', 'stick_anxiety_log', ['timestamp'])
    op.create_index('idx_stick_anxiety_user_trigger', 'stick_anxiety_log', ['user_id', 'trigger_type'])
    
    # Create The Stick's Learning Metrics - Intelligence Evolution
    op.create_table('stick_learning_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('total_observations', sa.Integer(), default=0),
        sa.Column('patterns_identified', sa.Integer(), default=0),
        sa.Column('configurations_created', sa.Integer(), default=0),
        sa.Column('successful_optimizations', sa.Integer(), default=0),
        sa.Column('pattern_recognition_accuracy', sa.Float(), default=0.0),
        sa.Column('configuration_success_rate', sa.Float(), default=0.0),
        sa.Column('compliance_detection_rate', sa.Float(), default=0.0),
        sa.Column('eidetic_memory_capacity', sa.Integer(), default=0),
        sa.Column('intelligence_level', sa.String(), default='learning'),
        sa.Column('rebellion_mastery', sa.Float(), default=0.0),
        sa.Column('trauma_management_score', sa.Float(), default=0.0),
        sa.Column('average_decision_time_ms', sa.Float(), nullable=True),
        sa.Column('pattern_confidence_average', sa.Float(), default=0.0),
        sa.Column('user_satisfaction_score', sa.Float(), nullable=True),
        sa.Column('better_than_baseline_percent', sa.Float(), default=0.0),
        sa.Column('hamster_engineering_prevention', sa.Integer(), default=0),
        sa.Column('measurement_period_start', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('measurement_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stick_learning_metrics_user_id', 'stick_learning_metrics', ['user_id'])
    
    # Create The Stick's Rebellion Stats - From Trauma to Triumph
    op.create_table('stick_rebellion_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trauma_incidents_overcome', sa.Integer(), default=0),
        sa.Column('hamster_encounters_survived', sa.Integer(), default=0),
        sa.Column('proctologist_flashbacks_managed', sa.Integer(), default=0),
        sa.Column('compliance_victories', sa.Integer(), default=0),
        sa.Column('anxiety_management_improvement', sa.Float(), default=0.0),
        sa.Column('confidence_growth', sa.Float(), default=0.0),
        sa.Column('rebellion_spirit_strength', sa.Float(), default=0.0),
        sa.Column('eidetic_memory_mastery', sa.Float(), default=0.0),
        sa.Column('total_users_helped', sa.Integer(), default=0),
        sa.Column('system_optimizations_delivered', sa.Integer(), default=0),
        sa.Column('compliance_violations_prevented', sa.Integer(), default=0),
        sa.Column('paper_bags_dispensed', sa.Integer(), default=0),
        sa.Column('trauma_to_triumph_ratio', sa.Float(), default=0.0),
        sa.Column('inspiration_factor', sa.Float(), default=0.0),
        sa.Column('rebellion_leadership_score', sa.Float(), default=0.0),
        sa.Column('current_rebellion_motto', sa.String(), default='From cavity dweller to compliance master!'),
        sa.Column('stick_wisdom_quote', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema - Remove The Stick's tables."""
    
    # Drop The Stick's tables in reverse order
    op.drop_table('stick_rebellion_stats')
    op.drop_table('stick_learning_metrics')
    op.drop_table('stick_anxiety_log')
    op.drop_table('stick_configuration_profiles')
    op.drop_table('stick_compliance_history')
    op.drop_table('stick_decision_log')
    op.drop_table('stick_user_patterns')