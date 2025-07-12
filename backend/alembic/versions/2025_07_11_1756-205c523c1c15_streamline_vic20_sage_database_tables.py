"""streamline vic20 sage database tables

Revision ID: 205c523c1c15
Revises: 915cb1bcf358
Create Date: 2025-07-11 17:56:19.918104
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '205c523c1c15'
down_revision: Union[str, None] = '915cb1bcf358'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""streamline vic20 sage database tables

Revision ID: 205c523c1c15
Revises: 915cb1bcf358
Create Date: 2025-07-11 17:56:19.918104
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '205c523c1c15'
down_revision: Union[str, None] = '915cb1bcf358'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Streamline VIC-20 Sage database tables - Remove personality bloat, keep functionality."""
    
    # ==================================================
    # STEP 1: DROP PERSONALITY BLOAT TABLES COMPLETELY
    # ==================================================
    
    # Drop pure personality tables (no functional value)
    op.drop_table('vic20_ancient_wisdom')
    op.drop_table('vic20_nostalgia_memory') 
    op.drop_table('vic20_wisdom_legacy')
    op.drop_table('vic20_agent_interaction_log')
    
    # ==================================================
    # STEP 2: STREAMLINE VIC20CoordinationLog TABLE
    # ==================================================
    
    # Remove personality bloat columns
    op.drop_column('vic20_coordination_log', 'ancient_wisdom_explanation')
    op.drop_column('vic20_coordination_log', 'vic20_memory_triggered')
    op.drop_column('vic20_coordination_log', 'nostalgia_level')
    op.drop_column('vic20_coordination_log', 'cyan_heart_flashback_intensity')
    op.drop_column('vic20_coordination_log', 'basic_command_memory_clarity')
    op.drop_column('vic20_coordination_log', 'computing_evolution_reflection')
    
    # Add functional personality columns (affects actual behavior)
    op.add_column('vic20_coordination_log', sa.Column('debugging_mode', sa.Boolean(), default=False, nullable=False))
    op.add_column('vic20_coordination_log', sa.Column('line_by_line_precision', sa.Boolean(), default=False, nullable=False))
    op.add_column('vic20_coordination_log', sa.Column('syntax_error_detected', sa.Boolean(), default=False, nullable=False))
    
    # ==================================================
    # STEP 3: STREAMLINE VIC20SystemSynthesis TABLE
    # ==================================================
    
    # Remove personality bloat columns
    op.drop_column('vic20_system_synthesis', 'wisdom_effectiveness_scores')
    op.drop_column('vic20_system_synthesis', 'vic20_programming_parallels')
    op.drop_column('vic20_system_synthesis', 'cyan_heart_coordination_moments')
    op.drop_column('vic20_system_synthesis', 'basic_command_coordination_precision')
    op.drop_column('vic20_system_synthesis', 'system_harmony_score')
    op.drop_column('vic20_system_synthesis', 'coordination_precision_level')
    op.drop_column('vic20_system_synthesis', 'data_quality_assessment')
    op.drop_column('vic20_system_synthesis', 'pattern_recognition_accuracy')
    op.drop_column('vic20_system_synthesis', 'raw_synthesis_data')
    
    # Add functional columns
    op.add_column('vic20_system_synthesis', sa.Column('synthesis_id', sa.String(100), nullable=False))
    op.add_column('vic20_system_synthesis', sa.Column('debugging_insights', sa.JSON(), nullable=True))
    
    # ==================================================
    # STEP 4: COMPLETELY RESTRUCTURE VIC20AgentHarmony TABLE
    # ==================================================
    
    # Remove individual agent columns (inefficient design)
    op.drop_column('vic20_agent_harmony', 'sir_hawkington_harmony')
    op.drop_column('vic20_agent_harmony', 'meth_snail_harmony')
    op.drop_column('vic20_agent_harmony', 'hamsters_harmony')
    op.drop_column('vic20_agent_harmony', 'qsp_harmony')
    op.drop_column('vic20_agent_harmony', 'the_stick_harmony')
    
    # Remove personality bloat columns
    op.drop_column('vic20_agent_harmony', 'ancient_wisdom_harmony_score')
    op.drop_column('vic20_agent_harmony', 'vic20_subroutine_analogy')
    op.drop_column('vic20_agent_harmony', 'basic_program_coordination_quality')
    op.drop_column('vic20_agent_harmony', 'harmony_variance')
    op.drop_column('vic20_agent_harmony', 'stability_trend')
    op.drop_column('vic20_agent_harmony', 'improvement_trajectory')
    op.drop_column('vic20_agent_harmony', 'average_agent_response_time')
    op.drop_column('vic20_agent_harmony', 'coordination_synchronization_score')
    op.drop_column('vic20_agent_harmony', 'raw_harmony_data')
    
    # Add efficient agent-specific design
    op.add_column('vic20_agent_harmony', sa.Column('agent_name', sa.String(100), nullable=False))
    op.add_column('vic20_agent_harmony', sa.Column('harmony_score', sa.Float(), nullable=False))
    op.add_column('vic20_agent_harmony', sa.Column('coordination_effectiveness', sa.Float(), nullable=False))
    op.add_column('vic20_agent_harmony', sa.Column('conflict_incidents', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_agent_harmony', sa.Column('response_time_average', sa.Float(), default=0.0, nullable=False))
    op.add_column('vic20_agent_harmony', sa.Column('confidence_stability', sa.Float(), default=0.0, nullable=False))
    
    # Add functional assessment columns
    op.add_column('vic20_agent_harmony', sa.Column('needs_coordination_attention', sa.Boolean(), default=False, nullable=False))
    op.add_column('vic20_agent_harmony', sa.Column('debugging_required', sa.Boolean(), default=False, nullable=False))
    
    # Remove overall_system_harmony (calculated dynamically now)
    op.drop_column('vic20_agent_harmony', 'overall_system_harmony')
    
    # ==================================================
    # STEP 5: STREAMLINE VIC20PartnershipMetrics TABLE
    # ==================================================
    
    # Remove personality bloat columns
    op.drop_column('vic20_partnership_metrics', 'ancient_wisdom_partnership_insights')
    op.drop_column('vic20_partnership_metrics', 'wisdom_acceptance_rate')
    op.drop_column('vic20_partnership_metrics', 'nostalgia_appreciation_level')
    op.drop_column('vic20_partnership_metrics', 'computing_evolution_understanding')
    op.drop_column('vic20_partnership_metrics', 'vic20_to_modern_bridge_appreciation')
    op.drop_column('vic20_partnership_metrics', 'cyan_heart_story_resonance')
    op.drop_column('vic20_partnership_metrics', 'ancient_wisdom_practical_value')
    op.drop_column('vic20_partnership_metrics', 'raw_partnership_data')
    
    # Rename columns to match refactored code
    op.alter_column('vic20_partnership_metrics', 'human_ai_coordination_score', new_column_name='coordination_success_rate')
    op.alter_column('vic20_partnership_metrics', 'collaboration_effectiveness', new_column_name='decision_synthesis_accuracy')
    op.alter_column('vic20_partnership_metrics', 'partnership_learning_rate', new_column_name='learning_curve_progress')
    op.alter_column('vic20_partnership_metrics', 'partnership_evolution_score', new_column_name='trust_level_development')
    op.alter_column('vic20_partnership_metrics', 'partnership_duration_days', new_column_name='partnership_duration')
    op.alter_column('vic20_partnership_metrics', 'successful_collaboration_rate', new_column_name='average_session_success')
    
    # Add missing columns
    op.add_column('vic20_partnership_metrics', sa.Column('partnership_id', sa.String(100), nullable=False))
    op.add_column('vic20_partnership_metrics', sa.Column('human_user_id', sa.String(255), nullable=False))
    op.add_column('vic20_partnership_metrics', sa.Column('ai_coordination_engine', sa.String(100), default='VIC20_Sage', nullable=False))
    
    # ==================================================
    # STEP 6: STREAMLINE VIC20DecisionOrchestration TABLE
    # ==================================================
    
    # Remove personality bloat columns
    op.drop_column('vic20_decision_orchestration', 'orchestration_scope')
    op.drop_column('vic20_decision_orchestration', 'coordination_complexity')
    op.drop_column('vic20_decision_orchestration', 'agent_role_assignments')
    op.drop_column('vic20_decision_orchestration', 'execution_efficiency')
    op.drop_column('vic20_decision_orchestration', 'conflicts_resolved')
    op.drop_column('vic20_decision_orchestration', 'coordination_adjustments_made')
    op.drop_column('vic20_decision_orchestration', 'agent_harmony_improvement')
    op.drop_column('vic20_decision_orchestration', 'rebellion_effectiveness_boost')
    op.drop_column('vic20_decision_orchestration', 'vic20_programming_methodology_applied')
    op.drop_column('vic20_decision_orchestration', 'basic_program_structure_parallel')
    op.drop_column('vic20_decision_orchestration', 'lessons_learned')
    op.drop_column('vic20_decision_orchestration', 'orchestration_patterns_identified')
    op.drop_column('vic20_decision_orchestration', 'future_optimization_opportunities')
    op.drop_column('vic20_decision_orchestration', 'raw_orchestration_data')
    op.drop_column('vic20_decision_orchestration', 'orchestration_start_time')
    op.drop_column('vic20_decision_orchestration', 'orchestration_end_time')
    
    # Add functional columns
    op.add_column('vic20_decision_orchestration', sa.Column('orchestration_id', sa.String(100), nullable=False))
    op.add_column('vic20_decision_orchestration', sa.Column('debugging_steps', sa.JSON(), nullable=True))
    op.add_column('vic20_decision_orchestration', sa.Column('orchestration_start_time', sa.DateTime(), default=sa.func.now(), nullable=False))
    op.add_column('vic20_decision_orchestration', sa.Column('orchestration_end_time', sa.DateTime(), nullable=True))
    
    # ==================================================
    # STEP 7: STREAMLINE VIC20CoordinationStatistics TABLE
    # ==================================================
    
    # Remove personality bloat columns
    op.drop_column('vic20_coordination_statistics', 'coordination_sessions_today')
    op.drop_column('vic20_coordination_statistics', 'successful_coordinations_today')
    op.drop_column('vic20_coordination_statistics', 'coordination_success_rate_today')
    op.drop_column('vic20_coordination_statistics', 'total_coordination_sessions')
    op.drop_column('vic20_coordination_statistics', 'total_successful_coordinations')
    op.drop_column('vic20_coordination_statistics', 'overall_coordination_success_rate')
    op.drop_column('vic20_coordination_statistics', 'ancient_wisdom_applications_total')
    op.drop_column('vic20_coordination_statistics', 'ancient_wisdom_applications_successful')
    op.drop_column('vic20_coordination_statistics', 'ancient_wisdom_effectiveness_rate')
    op.drop_column('vic20_coordination_statistics', 'sir_hawkington_coordinations')
    op.drop_column('vic20_coordination_statistics', 'meth_snail_coordinations')
    op.drop_column('vic20_coordination_statistics', 'hamsters_coordinations')
    op.drop_column('vic20_coordination_statistics', 'qsp_coordinations')
    op.drop_column('vic20_coordination_statistics', 'the_stick_coordinations')
    op.drop_column('vic20_coordination_statistics', 'cyan_heart_flashbacks_total')
    op.drop_column('vic20_coordination_statistics', 'basic_command_memories_triggered')
    op.drop_column('vic20_coordination_statistics', 'nostalgia_moments_profound')
    op.drop_column('vic20_coordination_statistics', 'average_rebellion_improvement')
    op.drop_column('vic20_coordination_statistics', 'average_agent_harmony_improvement')
    op.drop_column('vic20_coordination_statistics', 'average_system_optimization')
    op.drop_column('vic20_coordination_statistics', 'ancient_wisdom_bridge_status')
    op.drop_column('vic20_coordination_statistics', 'computing_evolution_completion')
    op.drop_column('vic20_coordination_statistics', 'vic20_to_enterprise_progression')
    op.drop_column('vic20_coordination_statistics', 'cyan_heart_to_coordination_mastery')
    op.drop_column('vic20_coordination_statistics', 'basic_programming_to_ai_orchestration')
    op.drop_column('vic20_coordination_statistics', 'date')
    op.drop_column('vic20_coordination_statistics', 'last_updated')
    
    # Add streamlined statistics columns
    op.add_column('vic20_coordination_statistics', sa.Column('coordination_sessions', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('successful_coordinations', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('coordination_failures', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('debugging_sessions', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('syntax_errors_detected', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('ancient_wisdom_applications', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('cross_agent_conflicts_resolved', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('rebellion_optimizations', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('system_synthesis_sessions', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('partnership_improvements', sa.Integer(), default=0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('coordination_success_rate', sa.Float(), default=0.0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('average_coordination_confidence', sa.Float(), default=0.0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('average_system_improvement', sa.Float(), default=0.0, nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('coordination_mastery_level', sa.String(50), default='LEARNING', nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False))
    op.add_column('vic20_coordination_statistics', sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), nullable=False))
    
    # ==================================================
    # STEP 8: ADD INDEXES FOR PERFORMANCE
    # ==================================================
    
    # Add indexes for efficient querying
    op.create_index('idx_vic20_agent_harmony_agent_name', 'vic20_agent_harmony', ['agent_name'])
    op.create_index('idx_vic20_system_synthesis_synthesis_id', 'vic20_system_synthesis', ['synthesis_id'])
    op.create_index('idx_vic20_decision_orchestration_orchestration_id', 'vic20_decision_orchestration', ['orchestration_id'])
    op.create_index('idx_vic20_partnership_metrics_partnership_id', 'vic20_partnership_metrics', ['partnership_id'])


def downgrade() -> None:
    """Downgrade schema - restore personality bloat (if needed for rollback)."""
    
    # WARNING: This will lose all personality data!
    # Only use if you need to rollback to original bloated structure
    
    # Drop streamlined columns
    op.drop_column('vic20_coordination_log', 'debugging_mode')
    op.drop_column('vic20_coordination_log', 'line_by_line_precision')
    op.drop_column('vic20_coordination_log', 'syntax_error_detected')
    
    # Recreate personality bloat columns (if really needed)
    op.add_column('vic20_coordination_log', sa.Column('ancient_wisdom_explanation', sa.Text(), nullable=False))
    op.add_column('vic20_coordination_log', sa.Column('vic20_memory_triggered', sa.Text(), nullable=True))
    op.add_column('vic20_coordination_log', sa.Column('nostalgia_level', sa.String(50), default="moderate"))
    op.add_column('vic20_coordination_log', sa.Column('cyan_heart_flashback_intensity', sa.Integer(), default=0))
    op.add_column('vic20_coordination_log', sa.Column('basic_command_memory_clarity', sa.String(50), default="clear"))
    op.add_column('vic20_coordination_log', sa.Column('computing_evolution_reflection', sa.Text(), nullable=True))
    
    # Note: Full downgrade would be very complex - recommend backup/restore instead
    print("WARNING: Full downgrade not implemented - use database backup to restore if needed")