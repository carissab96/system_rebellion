"""add Meth Snail energy consumption adn jitter level tracking tables

Revision ID: e05a2d49ffff
Revises: 3b0875496f2e
Create Date: 2025-08-05 20:21:17.505074
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e05a2d49ffff'
down_revision: Union[str, None] = '3b0875496f2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Add Meth Snail energy consumption and jitter level tracking tables"""
    
    # Create meth_snail_energy_consumption table
    op.create_table(
        'meth_snail_energy_consumption',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('energy_drink_type', sa.String(length=50), nullable=False),
        sa.Column('caffeine_mg', sa.Float(), nullable=False),
        sa.Column('authorization_requested', sa.Boolean(), nullable=True),
        sa.Column('authorization_granted', sa.Boolean(), nullable=True),
        sa.Column('authorized_by', sa.String(length=50), nullable=True),
        sa.Column('energy_drinks_consumed_today', sa.Integer(), nullable=True),
        sa.Column('time_since_last_drink_minutes', sa.Integer(), nullable=True),
        sa.Column('consumption_reason', sa.String(length=100), nullable=True),
        sa.Column('authorization_request_timestamp', sa.DateTime(), nullable=True),
        sa.Column('authorization_response_timestamp', sa.DateTime(), nullable=True),
        sa.Column('authorization_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_meth_snail_energy_consumption_user_id', 'meth_snail_energy_consumption', ['user_id'], unique=False)
    op.create_index('ix_meth_snail_energy_consumption_timestamp', 'meth_snail_energy_consumption', ['timestamp'], unique=False)

    # Create meth_snail_jitter_levels table
    op.create_table(
        'meth_snail_jitter_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('current_jitter_level', sa.Float(), nullable=False),
        sa.Column('peak_jitter_level', sa.Float(), nullable=False),
        sa.Column('baseline_jitter_level', sa.Float(), nullable=False),
        sa.Column('caffeine_level_mg', sa.Float(), nullable=False),
        sa.Column('is_decaffeinated', sa.Boolean(), nullable=True),
        sa.Column('time_since_caffeine_minutes', sa.Integer(), nullable=True),
        sa.Column('shell_spin_probability', sa.Float(), nullable=False),
        sa.Column('optimization_effectiveness', sa.Float(), nullable=True),
        sa.Column('focus_level', sa.Float(), nullable=False),
        sa.Column('hypercaffeinated', sa.Boolean(), nullable=True),
        sa.Column('requires_stick_intervention', sa.Boolean(), nullable=True),
        sa.Column('vic20_mediation_requested', sa.Boolean(), nullable=True),
        sa.Column('energy_source', sa.String(length=50), nullable=True),
        sa.Column('jitter_trend', sa.String(length=20), nullable=True),
        sa.Column('raw_jitter_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_meth_snail_jitter_levels_user_id', 'meth_snail_jitter_levels', ['user_id'], unique=False)
    op.create_index('ix_meth_snail_jitter_levels_timestamp', 'meth_snail_jitter_levels', ['timestamp'], unique=False)


def downgrade():
    """Remove Meth Snail energy consumption and jitter level tracking tables"""
    
    # Drop indexes first
    op.drop_index('ix_meth_snail_jitter_levels_timestamp', table_name='meth_snail_jitter_levels')
    op.drop_index('ix_meth_snail_jitter_levels_user_id', table_name='meth_snail_jitter_levels')
    op.drop_index('ix_meth_snail_energy_consumption_timestamp', table_name='meth_snail_energy_consumption')
    op.drop_index('ix_meth_snail_energy_consumption_user_id', table_name='meth_snail_energy_consumption')
    
    # Drop tables
    op.drop_table('meth_snail_jitter_levels')
    op.drop_table('meth_snail_energy_consumption')
