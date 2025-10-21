"""Add VIC-20 coordination tables

Revision ID: 9d0c345f9aa9
Revises: c544b25cb99c
Create Date: 2025-07-20 12:58:11.988892
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d0c345f9aa9'
down_revision: Union[str, None] = 'c544b25cb99c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create ALL VIC-20 tables."""
    
    # Create VIC-20 Coordination Log table
    op.create_table('vic20_coordination_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('decision_type', sa.String(100), nullable=False),
        sa.Column('coordination_state', sa.String(50), nullable=False),
        sa.Column('coordination_target', sa.String(255), nullable=False),
        sa.Column('agent_actions', sa.JSON(), nullable=False),
        sa.Column('system_synthesis_confidence', sa.Float(), nullable=False),
        sa.Column('ancient_wisdom_explanation', sa.Text(), nullable=False),
        sa.Column('ancient_wisdom_principle', sa.String(100), nullable=True),
        sa.Column('technical_orchestration', sa.JSON(), nullable=False),
        sa.Column('expected_rebellion_improvement', sa.Float(), nullable=False),
        sa.Column('confidence_level', sa.Float(), nullable=False),
        sa.Column('coordination_executed', sa.Boolean(), nullable=True),
        sa.Column('execution_success', sa.Boolean(), nullable=True),
        sa.Column('actual_improvement', sa.Float(), nullable=True),
        sa.Column('effectiveness_score', sa.Float(), nullable=True),
        sa.Column('system_context_snapshot', sa.JSON(), nullable=True),
        sa.Column('similar_past_decisions', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('effectiveness_measured_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vic20_coordination_log_id'), 'vic20_coordination_log', ['id'], unique=False)
    op.create_index(op.f('ix_vic20_coordination_log_user_id'), 'vic20_coordination_log', ['user_id'], unique=False)
    
    # Create VIC-20 System Synthesis table
    op.create_table('vic20_system_synthesis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('synthesis_id', sa.String(100), nullable=False),
        sa.Column('agent_intelligence_summary', sa.JSON(), nullable=False),
        sa.Column('coordination_opportunities', sa.JSON(), nullable=True),
        sa.Column('system_bottlenecks', sa.JSON(), nullable=True),
        sa.Column('agent_conflicts', sa.JSON(), nullable=True),
        sa.Column('rebellion_effectiveness_score', sa.Float(), nullable=False),
        sa.Column('pattern_recognition_data', sa.JSON(), nullable=True),
        sa.Column('historical_pattern_matches', sa.JSON(), nullable=True),
        sa.Column('synthesis_confidence', sa.Float(), nullable=False),
        sa.Column('ancient_wisdom_applications', sa.JSON(), nullable=True),
        sa.Column('wisdom_effectiveness_tracking', sa.JSON(), nullable=True),
        sa.Column('raw_synthesis_data', sa.JSON(), nullable=False),
        sa.Column('synthesis_learning_notes', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('synthesis_id')
    )
    op.create_index(op.f('ix_vic20_system_synthesis_id'), 'vic20_system_synthesis', ['id'], unique=False)
    op.create_index(op.f('ix_vic20_system_synthesis_user_id'), 'vic20_system_synthesis', ['user_id'], unique=False)
    
    # Create VIC-20 Agent Harmony table
    op.create_table('vic20_agent_harmony',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('harmony_score', sa.Float(), nullable=False),
        sa.Column('coordination_effectiveness', sa.Float(), nullable=False),
        sa.Column('conflict_incidents', sa.Integer(), nullable=True),
        sa.Column('response_time_average', sa.Float(), nullable=True),
        sa.Column('confidence_stability', sa.Float(), nullable=True),
        sa.Column('improvement_trend', sa.String(50), nullable=True),
        sa.Column('coordination_patterns_learned', sa.JSON(), nullable=True),
        sa.Column('effectiveness_history', sa.JSON(), nullable=True),
        sa.Column('needs_coordination_attention', sa.Boolean(), nullable=True),
        sa.Column('coordination_recommendations', sa.JSON(), nullable=True),
        sa.Column('raw_harmony_data', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vic20_agent_harmony_id'), 'vic20_agent_harmony', ['id'], unique=False)
    op.create_index(op.f('ix_vic20_agent_harmony_user_id'), 'vic20_agent_harmony', ['user_id'], unique=False)
    op.create_index(op.f('ix_vic20_agent_harmony_agent_name'), 'vic20_agent_harmony', ['agent_name'], unique=False)
    
    # Create VIC-20 Ancient Wisdom table
    op.create_table('vic20_ancient_wisdom',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('wisdom_principle', sa.String(100), nullable=False),
        sa.Column('modern_application', sa.Text(), nullable=False),
        sa.Column('coordination_context', sa.Text(), nullable=False),
        sa.Column('effectiveness_score', sa.Float(), nullable=False),
        sa.Column('wisdom_confidence', sa.Float(), nullable=False),
        sa.Column('application_success_rate', sa.Float(), nullable=True),
        sa.Column('system_conditions_when_applied', sa.JSON(), nullable=False),
        sa.Column('similar_past_applications', sa.JSON(), nullable=True),
        sa.Column('effectiveness_trend', sa.String(50), nullable=True),
        sa.Column('total_applications', sa.Integer(), nullable=True),
        sa.Column('successful_applications', sa.Integer(), nullable=True),
        sa.Column('coordination_improvements_attributed', sa.JSON(), nullable=True),
        sa.Column('effectiveness_history', sa.JSON(), nullable=True),
        sa.Column('pattern_reliability_score', sa.Float(), nullable=True),
        sa.Column('raw_wisdom_data', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_applied', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vic20_ancient_wisdom_id'), 'vic20_ancient_wisdom', ['id'], unique=False)
    op.create_index(op.f('ix_vic20_ancient_wisdom_user_id'), 'vic20_ancient_wisdom', ['user_id'], unique=False)
    op.create_index(op.f('ix_vic20_ancient_wisdom_wisdom_principle'), 'vic20_ancient_wisdom', ['wisdom_principle'], unique=False)
    
    # Create VIC-20 Partnership Metrics table
    op.create_table('vic20_partnership_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('partnership_id', sa.String(100), nullable=False),
        sa.Column('tasks_completed_with_ai_assistance', sa.Integer(), nullable=True),
        sa.Column('tasks_completed_without_ai_assistance', sa.Integer(), nullable=True),
        sa.Column('average_task_completion_time_with_ai', sa.Float(), nullable=True),
        sa.Column('average_task_completion_time_without_ai', sa.Float(), nullable=True),
        sa.Column('productivity_improvement_percentage', sa.Float(), nullable=True),
        sa.Column('decisions_made_with_ai_coordination', sa.Integer(), nullable=True),
        sa.Column('decisions_made_without_ai_coordination', sa.Integer(), nullable=True),
        sa.Column('average_decision_time_with_ai', sa.Float(), nullable=True),
        sa.Column('average_decision_time_without_ai', sa.Float(), nullable=True),
        sa.Column('decision_reversal_rate_with_ai', sa.Float(), nullable=True),
        sa.Column('decision_reversal_rate_without_ai', sa.Float(), nullable=True),
        sa.Column('problems_identified_by_ai', sa.Integer(), nullable=True),
        sa.Column('problems_identified_by_human', sa.Integer(), nullable=True),
        sa.Column('problems_resolved_collaboratively', sa.Integer(), nullable=True),
        sa.Column('average_problem_resolution_time', sa.Float(), nullable=True),
        sa.Column('problems_prevented_by_ai_early_warning', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vic20_partnership_metrics_id'), 'vic20_partnership_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_vic20_partnership_metrics_user_id'), 'vic20_partnership_metrics', ['user_id'], unique=False)
    op.create_index(op.f('ix_vic20_partnership_metrics_partnership_id'), 'vic20_partnership_metrics', ['partnership_id'], unique=False)
    
    # Create VIC-20 Decision Orchestration table
    op.create_table('vic20_decision_orchestration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('orchestration_id', sa.String(100), nullable=False),
        sa.Column('orchestration_type', sa.String(100), nullable=False),
        sa.Column('agents_coordinated', sa.JSON(), nullable=False),
        sa.Column('coordination_sequence', sa.JSON(), nullable=False),
        sa.Column('orchestration_success', sa.Boolean(), nullable=True),
        sa.Column('timing_precision', sa.Float(), nullable=True),
        sa.Column('conflict_resolution_effectiveness', sa.Float(), nullable=True),
        sa.Column('system_improvement_achieved', sa.Float(), nullable=True),
        sa.Column('expected_vs_actual_improvement', sa.Float(), nullable=True),
        sa.Column('orchestration_patterns_identified', sa.JSON(), nullable=True),
        sa.Column('successful_coordination_sequences', sa.JSON(), nullable=True),
        sa.Column('failed_coordination_lessons', sa.JSON(), nullable=True),
        sa.Column('ancient_wisdom_orchestration_notes', sa.Text(), nullable=True),
        sa.Column('wisdom_effectiveness_in_orchestration', sa.Float(), nullable=True),
        sa.Column('raw_orchestration_data', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('orchestration_start_time', sa.DateTime(), nullable=True),
        sa.Column('orchestration_end_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('orchestration_id')
    )
    op.create_index(op.f('ix_vic20_decision_orchestration_id'), 'vic20_decision_orchestration', ['id'], unique=False)
    op.create_index(op.f('ix_vic20_decision_orchestration_user_id'), 'vic20_decision_orchestration', ['user_id'], unique=False)
    op.create_index(op.f('ix_vic20_decision_orchestration_orchestration_type'), 'vic20_decision_orchestration', ['orchestration_type'], unique=False)
    
    # Create VIC-20 Agent Interaction Log table
    op.create_table('vic20_agent_interaction_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('source_agent', sa.String(100), nullable=False),
        sa.Column('target_agent', sa.String(100), nullable=True),
        sa.Column('interaction_type', sa.String(100), nullable=False),
        sa.Column('message_content', sa.JSON(), nullable=False),
        sa.Column('message_priority', sa.String(50), nullable=True),
        sa.Column('coordination_context', sa.Text(), nullable=True),
        sa.Column('vic20_processing_notes', sa.Text(), nullable=True),
        sa.Column('coordination_impact_assessment', sa.String(100), nullable=True),
        sa.Column('pattern_recognition_triggered', sa.Boolean(), nullable=True),
        sa.Column('interaction_success', sa.Boolean(), nullable=True),
        sa.Column('response_generated', sa.Boolean(), nullable=True),
        sa.Column('coordination_triggered', sa.Boolean(), nullable=True),
        sa.Column('coordination_effectiveness', sa.Float(), nullable=True),
        sa.Column('harmony_impact_positive', sa.Boolean(), nullable=True),
        sa.Column('harmony_impact_negative', sa.Boolean(), nullable=True),
        sa.Column('conflict_resolution_required', sa.Boolean(), nullable=True),
        sa.Column('message_received_timestamp', sa.DateTime(), nullable=True),
        sa.Column('vic20_processing_start', sa.DateTime(), nullable=True),
        sa.Column('vic20_processing_end', sa.DateTime(), nullable=True),
        sa.Column('response_sent_timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vic20_agent_interaction_log_id'), 'vic20_agent_interaction_log', ['id'], unique=False)
    op.create_index(op.f('ix_vic20_agent_interaction_log_user_id'), 'vic20_agent_interaction_log', ['user_id'], unique=False)
    op.create_index(op.f('ix_vic20_agent_interaction_log_source_agent'), 'vic20_agent_interaction_log', ['source_agent'], unique=False)
    op.create_index(op.f('ix_vic20_agent_interaction_log_target_agent'), 'vic20_agent_interaction_log', ['target_agent'], unique=False)
    op.create_index(op.f('ix_vic20_agent_interaction_log_interaction_type'), 'vic20_agent_interaction_log', ['interaction_type'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Remove ALL VIC-20 tables."""
    op.drop_table('vic20_agent_interaction_log')
    op.drop_table('vic20_decision_orchestration')
    op.drop_table('vic20_partnership_metrics')
    op.drop_table('vic20_ancient_wisdom')
    op.drop_table('vic20_agent_harmony')
    op.drop_table('vic20_system_synthesis')
    op.drop_table('vic20_coordination_log')
