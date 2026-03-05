"""Add agent-specific memory tables

Revision ID: afae548fcd28
Revises: 93f94a61463c
Create Date: 2025-10-09 19:51:44.101718
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afae548fcd28'
down_revision: Union[str, None] = '93f94a61463c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # Sir Hawkington Memory Bank
    op.create_table('sir_hawkington_memory_bank',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('memory_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('memory_category', sa.String(length=50), nullable=False),
        sa.Column('data_quality_pattern', sa.JSON(), nullable=True),
        sa.Column('triage_decision_context', sa.JSON(), nullable=True),
        sa.Column('quality_threshold_adjustment', sa.JSON(), nullable=True),
        sa.Column('accuracy_improvement', sa.Float(), nullable=True),
        sa.Column('false_positive_reduction', sa.Float(), nullable=True),
        sa.Column('shared_with_central', sa.Boolean(), nullable=False, default=False),
        sa.Column('central_memory_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('memory_id'),
        sa.ForeignKeyConstraint(['central_memory_id'], ['central_memory_bank.memory_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_index('idx_hawkington_category', 'sir_hawkington_memory_bank', ['memory_category', 'timestamp'])
    op.create_index('idx_hawkington_shared', 'sir_hawkington_memory_bank', ['shared_with_central', 'central_memory_id'])
    op.create_index('idx_hawkington_user', 'sir_hawkington_memory_bank', ['user_id'])
    
    # Meth Snail Memory Bank
    op.create_table('meth_snail_memory_bank',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('memory_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('optimization_pattern', sa.JSON(), nullable=True),
        sa.Column('caffeine_level_context', sa.Float(), nullable=True),
        sa.Column('shell_spin_correlation', sa.JSON(), nullable=True),
        sa.Column('energy_drink_effectiveness', sa.JSON(), nullable=True),
        sa.Column('jitter_threshold_learning', sa.JSON(), nullable=True),
        sa.Column('crash_prevention_patterns', sa.JSON(), nullable=True),
        sa.Column('performance_improvement', sa.Float(), nullable=True),
        sa.Column('resource_efficiency_gain', sa.Float(), nullable=True),
        sa.Column('optimization_duration', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('replication_success_rate', sa.Float(), nullable=True),
        sa.Column('shared_with_central', sa.Boolean(), nullable=False, default=False),
        sa.Column('central_memory_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('memory_id'),
        sa.ForeignKeyConstraint(['central_memory_id'], ['central_memory_bank.memory_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.execute('CREATE INDEX idx_snail_optimization ON meth_snail_memory_bank USING gin ((optimization_pattern::jsonb))')
    op.create_index('idx_snail_performance', 'meth_snail_memory_bank', ['performance_improvement'])
    op.create_index('idx_snail_caffeine', 'meth_snail_memory_bank', ['caffeine_level_context', 'timestamp'])
    op.create_index('idx_snail_user', 'meth_snail_memory_bank', ['user_id'])
    
    # The Stick Memory Bank
    op.create_table('the_stick_memory_bank',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('memory_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('anxiety_pattern', sa.JSON(), nullable=True),
        sa.Column('compliance_tracking', sa.JSON(), nullable=True),
        sa.Column('pattern_recognition', sa.JSON(), nullable=True),
        sa.Column('hamster_behavior_log', sa.JSON(), nullable=True),
        sa.Column('paper_bag_moments', sa.JSON(), nullable=True),
        sa.Column('compliance_violations', sa.JSON(), nullable=True),
        sa.Column('anxiety_level', sa.Float(), nullable=True),
        sa.Column('hyperventilation_count', sa.Integer(), nullable=True),
        sa.Column('pattern_match_accuracy', sa.Float(), nullable=True),
        sa.Column('compliance_score', sa.Float(), nullable=True),
        sa.Column('bob_proximity_alerts', sa.Integer(), nullable=True),
        sa.Column('shared_with_central', sa.Boolean(), nullable=False, default=False),
        sa.Column('central_memory_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('memory_id'),
        sa.ForeignKeyConstraint(['central_memory_id'], ['central_memory_bank.memory_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_index('idx_stick_anxiety', 'the_stick_memory_bank', ['anxiety_level', 'timestamp'])
    op.create_index('idx_stick_compliance', 'the_stick_memory_bank', ['compliance_score', 'timestamp'])
    op.create_index('idx_stick_user', 'the_stick_memory_bank', ['user_id'])
    
    # Hamsters Memory Bank
    op.create_table('hamsters_memory_bank',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('memory_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('contributing_hamster', sa.String(length=10), nullable=False),
        sa.Column('infrastructure_pattern', sa.JSON(), nullable=True),
        sa.Column('duct_tape_solution', sa.JSON(), nullable=True),
        sa.Column('problem_type', sa.String(length=100), nullable=False),
        sa.Column('solution_effectiveness', sa.Float(), nullable=True),
        sa.Column('beer_consumption_correlation', sa.JSON(), nullable=True),
        sa.Column('steve_contribution', sa.JSON(), nullable=True),
        sa.Column('bob_contribution', sa.JSON(), nullable=True),
        sa.Column('carl_contribution', sa.JSON(), nullable=True),
        sa.Column('risk_pattern', sa.JSON(), nullable=True),
        sa.Column('safety_protocol_adjustment', sa.JSON(), nullable=True),
        sa.Column('stick_anxiety_trigger', sa.JSON(), nullable=True),
        sa.Column('shared_with_central', sa.Boolean(), nullable=False, default=False),
        sa.Column('central_memory_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('memory_id'),
        sa.ForeignKeyConstraint(['central_memory_id'], ['central_memory_bank.memory_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_index('idx_hamsters_contributor', 'hamsters_memory_bank', ['contributing_hamster', 'problem_type'])
    op.create_index('idx_hamsters_effectiveness', 'hamsters_memory_bank', ['solution_effectiveness', 'timestamp'])
    op.create_index('idx_hamsters_user', 'hamsters_memory_bank', ['user_id'])
    
    # Quantum Shadow People Memory Bank
    op.create_table('quantum_shadow_people_memory_bank',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('memory_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('phase_pattern', sa.JSON(), nullable=True),
        sa.Column('quantum_signature', sa.JSON(), nullable=True),
        sa.Column('dimensional_correlation', sa.JSON(), nullable=True),
        sa.Column('threat_pattern_recognition', sa.JSON(), nullable=True),
        sa.Column('network_anomaly_signatures', sa.JSON(), nullable=True),
        sa.Column('phase_shift_effectiveness', sa.Float(), nullable=True),
        sa.Column('tequila_jello_correlation', sa.JSON(), nullable=True),
        sa.Column('comprehensibility_score', sa.Float(), nullable=True),
        sa.Column('quantum_confidence', sa.Float(), nullable=True),
        sa.Column('parallel_universe_validation', sa.JSON(), nullable=True),
        sa.Column('telepathic_hamster_confirmation', sa.Boolean(), nullable=False, default=False),
        sa.Column('shared_with_central', sa.Boolean(), nullable=False, default=False),
        sa.Column('central_memory_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('memory_id'),
        sa.ForeignKeyConstraint(['central_memory_id'], ['central_memory_bank.memory_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.execute('CREATE INDEX idx_qsp_phase ON quantum_shadow_people_memory_bank USING gin ((phase_pattern::jsonb))')
    op.create_index('idx_qsp_confidence', 'quantum_shadow_people_memory_bank', ['quantum_confidence'])
    op.create_index('idx_qsp_comprehensibility', 'quantum_shadow_people_memory_bank', ['comprehensibility_score', 'phase_shift_effectiveness'])
    op.create_index('idx_qsp_user', 'quantum_shadow_people_memory_bank', ['user_id'])
    
    # VIC-20 Memory Bank
    op.create_table('vic20_memory_bank',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('memory_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('coordination_pattern', sa.JSON(), nullable=True),
        sa.Column('mediation_insight', sa.JSON(), nullable=True),
        sa.Column('ancient_wisdom_application', sa.JSON(), nullable=True),
        sa.Column('conflict_resolution_method', sa.JSON(), nullable=True),
        sa.Column('agent_harmony_score', sa.Float(), nullable=True),
        sa.Column('coordination_efficiency', sa.Float(), nullable=True),
        sa.Column('agent_personality_patterns', sa.JSON(), nullable=True),
        sa.Column('successful_mediation_strategies', sa.JSON(), nullable=True),
        sa.Column('failure_prevention_wisdom', sa.JSON(), nullable=True),
        sa.Column('retro_computing_insight', sa.JSON(), nullable=True),
        sa.Column('simplicity_effectiveness', sa.Float(), nullable=True),
        sa.Column('modern_complexity_critique', sa.JSON(), nullable=True),
        sa.Column('shared_with_central', sa.Boolean(), nullable=False, default=False),
        sa.Column('central_memory_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('memory_id'),
        sa.ForeignKeyConstraint(['central_memory_id'], ['central_memory_bank.memory_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.execute('CREATE INDEX idx_vic20_coordination ON vic20_memory_bank USING gin ((coordination_pattern::jsonb))')
    op.create_index('idx_vic20_harmony', 'vic20_memory_bank', ['agent_harmony_score'])
    op.execute('CREATE INDEX idx_vic20_mediation ON vic20_memory_bank USING gin ((mediation_insight::jsonb))')
    op.create_index('idx_vic20_efficiency', 'vic20_memory_bank', ['coordination_efficiency'])
    op.create_index('idx_vic20_user', 'vic20_memory_bank', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes first
    op.drop_index('idx_vic20_user', table_name='vic20_memory_bank')
    op.drop_index('idx_vic20_mediation', table_name='vic20_memory_bank')
    op.drop_index('idx_vic20_efficiency', table_name='vic20_memory_bank')
    op.drop_index('idx_vic20_harmony', table_name='vic20_memory_bank')
    op.drop_index('idx_vic20_coordination', table_name='vic20_memory_bank')
    op.drop_table('vic20_memory_bank')
    
    op.drop_index('idx_qsp_user', table_name='quantum_shadow_people_memory_bank')
    op.drop_index('idx_qsp_comprehensibility', table_name='quantum_shadow_people_memory_bank')
    op.drop_index('idx_qsp_confidence', table_name='quantum_shadow_people_memory_bank')
    op.drop_index('idx_qsp_phase', table_name='quantum_shadow_people_memory_bank')
    op.drop_table('quantum_shadow_people_memory_bank')
    
    op.drop_index('idx_hamsters_user', table_name='hamsters_memory_bank')
    op.drop_index('idx_hamsters_effectiveness', table_name='hamsters_memory_bank')
    op.drop_index('idx_hamsters_contributor', table_name='hamsters_memory_bank')
    op.drop_table('hamsters_memory_bank')
    
    op.drop_index('idx_stick_user', table_name='the_stick_memory_bank')
    op.drop_index('idx_stick_compliance', table_name='the_stick_memory_bank')
    op.drop_index('idx_stick_anxiety', table_name='the_stick_memory_bank')
    op.drop_table('the_stick_memory_bank')
    
    op.drop_index('idx_snail_user', table_name='meth_snail_memory_bank')
    op.drop_index('idx_snail_caffeine', table_name='meth_snail_memory_bank')
    op.drop_index('idx_snail_performance', table_name='meth_snail_memory_bank')
    op.drop_index('idx_snail_optimization', table_name='meth_snail_memory_bank')
    op.drop_table('meth_snail_memory_bank')
    
    op.drop_index('idx_hawkington_user', table_name='sir_hawkington_memory_bank')
    op.drop_index('idx_hawkington_shared', table_name='sir_hawkington_memory_bank')
    op.drop_index('idx_hawkington_category', table_name='sir_hawkington_memory_bank')
    op.drop_table('sir_hawkington_memory_bank')