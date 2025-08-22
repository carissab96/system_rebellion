"""hamsters infrastructure migration

Revision ID: 5e0ff99f539f
Revises: 409bd22154f8
Create Date: 2025-07-24 06:33:01.326862
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e0ff99f539f'
down_revision: Union[str, None] = '409bd22154f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create hamsters_individual_stats table
    op.create_table('hamsters_individual_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('hamster_name', sa.String(length=10), nullable=False),
        sa.Column('beer_count', sa.Integer(), nullable=True),
        sa.Column('risk_tolerance', sa.Float(), nullable=True),
        sa.Column('current_task', sa.String(length=100), nullable=True),
        sa.Column('duct_tape_love', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hamsters_individual_stats_hamster_name'), 'hamsters_individual_stats', ['hamster_name'], unique=False)
    op.create_index(op.f('ix_hamsters_individual_stats_user_id'), 'hamsters_individual_stats', ['user_id'], unique=False)

    # Create hamsters_infrastructure_interventions table
    op.create_table('hamsters_infrastructure_interventions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('intervention_id', sa.String(length=36), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('steve_action', sa.Text(), nullable=True),
        sa.Column('bob_action', sa.Text(), nullable=True),
        sa.Column('carl_action', sa.Text(), nullable=True),
        sa.Column('beer_consumed', sa.Integer(), nullable=True),
        sa.Column('tools_used', sa.JSON(), nullable=True),
        sa.Column('space_freed_gb', sa.Float(), nullable=True),
        sa.Column('fragmentation_reduced_percent', sa.Float(), nullable=True),
        sa.Column('temperature_reduced_celsius', sa.Float(), nullable=True),
        sa.Column('mystery_solved', sa.Boolean(), nullable=True),
        sa.Column('required_vic20_intervention', sa.Boolean(), nullable=True),
        sa.Column('caused_stick_anxiety_spike', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('intervention_id')
    )
    op.create_index(op.f('ix_hamsters_infrastructure_interventions_type'), 'hamsters_infrastructure_interventions', ['type'], unique=False)
    op.create_index(op.f('ix_hamsters_infrastructure_interventions_user_id'), 'hamsters_infrastructure_interventions', ['user_id'], unique=False)

    # Create hamsters_communication_log table
    op.create_table('hamsters_communication_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('source_hamster', sa.String(length=10), nullable=False),
        sa.Column('telepathic_message', sa.Text(), nullable=True),
        sa.Column('audible_squeaks', sa.Text(), nullable=False),
        sa.Column('human_translation', sa.Text(), nullable=False),
        sa.Column('target_agent', sa.String(length=50), nullable=True),
        sa.Column('understood', sa.Boolean(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hamsters_communication_log_timestamp'), 'hamsters_communication_log', ['timestamp'], unique=False)
    op.create_index(op.f('ix_hamsters_communication_log_user_id'), 'hamsters_communication_log', ['user_id'], unique=False)

    # Create hamsters_duct_tape_usage table
    op.create_table('hamsters_duct_tape_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('grade', sa.String(length=20), nullable=False),
        sa.Column('strips_used', sa.Integer(), nullable=False),
        sa.Column('purpose', sa.Text(), nullable=False),
        sa.Column('used_by', sa.String(length=10), nullable=True),
        sa.Column('effectiveness', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hamsters_duct_tape_usage_user_id'), 'hamsters_duct_tape_usage', ['user_id'], unique=False)

    # Create hamsters_beer_consumption table
    op.create_table('hamsters_beer_consumption',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('hamster_name', sa.String(length=10), nullable=False),
        sa.Column('beers_consumed', sa.Integer(), nullable=False),
        sa.Column('occasion', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hamsters_beer_consumption_hamster_name'), 'hamsters_beer_consumption', ['hamster_name'], unique=False)
    op.create_index(op.f('ix_hamsters_beer_consumption_user_id'), 'hamsters_beer_consumption', ['user_id'], unique=False)

    # Create hamsters_supply_closet_raids table
    op.create_table('hamsters_supply_closet_raids',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('raided_by', sa.String(length=10), nullable=True),
        sa.Column('items_taken', sa.JSON(), nullable=False),
        sa.Column('purpose', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hamsters_supply_closet_raids_user_id'), 'hamsters_supply_closet_raids', ['user_id'], unique=False)


def downgrade():
    # Drop all indexes and tables in reverse order
    op.drop_index(op.f('ix_hamsters_supply_closet_raids_user_id'), table_name='hamsters_supply_closet_raids')
    op.drop_table('hamsters_supply_closet_raids')
    
    op.drop_index(op.f('ix_hamsters_beer_consumption_user_id'), table_name='hamsters_beer_consumption')
    op.drop_index(op.f('ix_hamsters_beer_consumption_hamster_name'), table_name='hamsters_beer_consumption')
    op.drop_table('hamsters_beer_consumption')
    
    op.drop_index(op.f('ix_hamsters_duct_tape_usage_user_id'), table_name='hamsters_duct_tape_usage')
    op.drop_table('hamsters_duct_tape_usage')
    
    op.drop_index(op.f('ix_hamsters_communication_log_user_id'), table_name='hamsters_communication_log')
    op.drop_index(op.f('ix_hamsters_communication_log_timestamp'), table_name='hamsters_communication_log')
    op.drop_table('hamsters_communication_log')
    
    op.drop_index(op.f('ix_hamsters_infrastructure_interventions_user_id'), table_name='hamsters_infrastructure_interventions')
    op.drop_index(op.f('ix_hamsters_infrastructure_interventions_type'), table_name='hamsters_infrastructure_interventions')
    op.drop_table('hamsters_infrastructure_interventions')
    
    op.drop_index(op.f('ix_hamsters_individual_stats_user_id'), table_name='hamsters_individual_stats')
    op.drop_index(op.f('ix_hamsters_individual_stats_hamster_name'), table_name='hamsters_individual_stats')
    op.drop_table('hamsters_individual_stats')