"""add anxiety-driven tables for The Stick

Revision ID: f717dcc399f9
Revises: 5e0ff99f539f
Create Date: 2025-07-24 11:51:20.430215
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f717dcc399f9'
down_revision: Union[str, None] = '5e0ff99f539f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""Add anxiety-driven tables for The Stick

Revision ID: stick_anxiety_upgrade
Revises: previous_revision
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # # Create anxiety log table
    # op.create_table('stick_anxiety_log',
    #     sa.Column('id', sa.Integer(), nullable=False),
    #     sa.Column('timestamp', sa.DateTime(), nullable=True),
    #     sa.Column('trigger', sa.String(length=255), nullable=False),
    #     sa.Column('anxiety_level_before', sa.Float(), nullable=False),
    #     sa.Column('anxiety_level_after', sa.Float(), nullable=False),
    #     sa.Column('multiplier', sa.Float(), nullable=True),
    #     sa.Column('paper_bags_consumed', sa.Integer(), nullable=True),
    #     sa.Column('hamster_involved', sa.Boolean(), nullable=True),
    #     sa.Column('resolution', sa.String(length=100), nullable=True),
    #     sa.PrimaryKeyConstraint('id')
    # )
    # op.create_index(op.f('ix_stick_anxiety_log_timestamp'), 'stick_anxiety_log', ['timestamp'], unique=False)
    
    # Create hamster encounters table
    op.create_table('stick_hamster_encounters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('hamsters_present', sa.String(length=100), nullable=True),
        sa.Column('steve_location', sa.String(length=255), nullable=True),
        sa.Column('bob_location', sa.String(length=255), nullable=True),
        sa.Column('carl_location', sa.String(length=255), nullable=True),
        sa.Column('anxiety_multiplier', sa.Float(), nullable=False),
        sa.Column('panic_level', sa.String(length=50), nullable=False),
        sa.Column('infrastructure_risk', sa.String(length=100), nullable=True),
        sa.Column('stick_response', sa.Text(), nullable=True),
        sa.Column('paper_bags_consumed', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stick_hamster_encounters_timestamp'), 'stick_hamster_encounters', ['timestamp'], unique=False)
    op.create_index(op.f('ix_stick_hamster_encounters_user_id'), 'stick_hamster_encounters', ['user_id'], unique=False)
    
    # Create paper bag usage table
    op.create_table('stick_paper_bag_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('bags_consumed', sa.Integer(), nullable=True),
        sa.Column('bags_added', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('anxiety_level_at_time', sa.Float(), nullable=True),
        sa.Column('hamster_related', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stick_paper_bag_usage_timestamp'), 'stick_paper_bag_usage', ['timestamp'], unique=False)
    
    # Create memory bank table
    op.create_table('stick_memory_bank',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('anxiety_level', sa.Float(), nullable=True),
        sa.Column('importance', sa.String(length=50), nullable=True),
        sa.Column('related_hamsters', sa.String(length=100), nullable=True),
        sa.Column('compliance_impact', sa.String(length=100), nullable=True),
        sa.Column('never_forget', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stick_memory_bank_timestamp'), 'stick_memory_bank', ['timestamp'], unique=False)
    op.create_index('idx_never_forget', 'stick_memory_bank', ['never_forget', 'importance'], unique=False)
    op.create_index('idx_hamster_memories', 'stick_memory_bank', ['related_hamsters'], unique=False)
    
    # Create squeak translations table
    op.create_table('stick_squeak_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('hamster_source', sa.String(length=50), nullable=True),
        sa.Column('original_squeak', sa.String(length=255), nullable=True),
        sa.Column('translation', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('anxiety_level_during_translation', sa.Float(), nullable=True),
        sa.Column('stick_reaction', sa.Text(), nullable=True),
        sa.Column('paper_bags_consumed', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create emergency protocols table
    op.create_table('stick_emergency_protocols',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('protocol_name', sa.String(length=100), nullable=True),
        sa.Column('trigger_condition', sa.String(length=255), nullable=True),
        sa.Column('activation_count', sa.Integer(), nullable=True),
        sa.Column('last_activated', sa.DateTime(), nullable=True),
        sa.Column('anxiety_threshold', sa.Float(), nullable=True),
        sa.Column('response_actions', sa.JSON(), nullable=True),
        sa.Column('hamster_specific', sa.Boolean(), nullable=True),
        sa.Column('paper_bags_required', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('protocol_name')
    )
    
    # Update existing tables with new columns
    op.add_column('stick_decision_log', sa.Column('anxiety_level', sa.String(length=50), nullable=True))
    op.add_column('stick_decision_log', sa.Column('anxiety_explanation', sa.Text(), nullable=True))
    op.add_column('stick_decision_log', sa.Column('paper_bags_consumed', sa.Integer(), nullable=True))
    
    op.add_column('stick_compliance_history', sa.Column('anxiety_adjusted_threshold', sa.Float(), nullable=True))
    op.add_column('stick_compliance_history', sa.Column('anxiety_impact', sa.Float(), nullable=True))
    op.add_column('stick_compliance_history', sa.Column('paper_bags_triggered', sa.Integer(), nullable=True))
    
    op.add_column('stick_user_patterns', sa.Column('anxiety_correlation', sa.Float(), nullable=True))
    
    op.add_column('stick_configuration_profiles', sa.Column('anxiety_level_when_created', sa.Float(), nullable=True))
    op.add_column('stick_configuration_profiles', sa.Column('stick_notes', sa.JSON(), nullable=True))
    
    # Insert initial paper bag inventory
    op.execute(
        "INSERT INTO stick_paper_bag_usage (timestamp, bags_added, reason) "
        "VALUES (NOW(), 100, 'Initial inventory for The Stick')"
    )
    
 # Insert emergency protocols
    op.execute(
        "INSERT INTO stick_emergency_protocols (protocol_name, trigger_condition, anxiety_threshold, response_actions, hamster_specific, paper_bags_required) "
        "VALUES ('BOB_PROXIMITY', 'Bob detected within system', 80.0, '{\"actions\": [\"hide_configs\", \"backup_everything\", \"panic_mode\"]}', true, 3)"
    )
    op.execute(
        "INSERT INTO stick_emergency_protocols (protocol_name, trigger_condition, anxiety_threshold, response_actions, hamster_specific, paper_bags_required) "
        "VALUES ('MULTI_HAMSTER', 'Multiple hamsters active', 90.0, '{\"actions\": [\"maximum_vigilance\", \"document_everything\", \"prepare_for_chaos\"]}', true, 5)"
    )
    op.execute(
        "INSERT INTO stick_emergency_protocols (protocol_name, trigger_condition, anxiety_threshold, response_actions, hamster_specific, paper_bags_required) "
        "VALUES ('PAPER_BAG_DEPLETION', 'Paper bags < 10', 70.0, '{\"actions\": [\"emergency_resupply\", \"conservation_mode\"]}', false, 0)"
    )
    op.execute(
        "INSERT INTO stick_emergency_protocols (protocol_name, trigger_condition, anxiety_threshold, response_actions, hamster_specific, paper_bags_required) "
        "VALUES ('COMPLIANCE_CASCADE', 'Multiple violations detected', 85.0, '{\"actions\": [\"hyperfocus_mode\", \"aggressive_enforcement\"]}', false, 2)"
    )
def downgrade():
    # Remove new columns from existing tables
    op.drop_column('stick_configuration_profiles', 'stick_notes')
    op.drop_column('stick_configuration_profiles', 'anxiety_level_when_created')
    op.drop_column('stick_user_patterns', 'anxiety_correlation')
    op.drop_column('stick_compliance_history', 'paper_bags_triggered')
    op.drop_column('stick_compliance_history', 'anxiety_impact')
    op.drop_column('stick_compliance_history', 'anxiety_adjusted_threshold')
    op.drop_column('stick_decision_log', 'paper_bags_consumed')
    op.drop_column('stick_decision_log', 'anxiety_explanation')
    op.drop_column('stick_decision_log', 'anxiety_level')
    
    # Drop new tables
    op.drop_table('stick_emergency_protocols')
    op.drop_table('stick_squeak_translations')
    op.drop_index('idx_hamster_memories', table_name='stick_memory_bank')
    op.drop_index('idx_never_forget', table_name='stick_memory_bank')
    op.drop_index(op.f('ix_stick_memory_bank_timestamp'), table_name='stick_memory_bank')
    op.drop_table('stick_memory_bank')
    op.drop_index(op.f('ix_stick_paper_bag_usage_timestamp'), table_name='stick_paper_bag_usage')
    op.drop_table('stick_paper_bag_usage')
    op.drop_index(op.f('ix_stick_hamster_encounters_user_id'), table_name='stick_hamster_encounters')
    op.drop_index(op.f('ix_stick_hamster_encounters_timestamp'), table_name='stick_hamster_encounters')
    op.drop_table('stick_hamster_encounters')
    op.drop_index(op.f('ix_stick_anxiety_log_timestamp'), table_name='stick_anxiety_log')
    op.drop_table('stick_anxiety_log')