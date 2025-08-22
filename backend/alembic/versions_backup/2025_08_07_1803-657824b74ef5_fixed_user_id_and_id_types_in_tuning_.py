"""fixed user_id and id types in tuning history table

Revision ID: 657824b74ef5
Revises: 5252a4dd6395
Create Date: 2025-08-07 18:03:45.326226
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '657824b74ef5'
down_revision: Union[str, None] = '5252a4dd6395'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Fix tuning_history data types for UUID compatibility."""
    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    
    # Create new table with correct data types
    op.create_table('tuning_history_new',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('parameter', sa.String(), nullable=False),
        sa.Column('old_value', sa.String(), nullable=True),
        sa.Column('new_value', sa.String(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('metrics_before', sa.JSON(), nullable=True),
        sa.Column('metrics_after', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('beer_consumed', sa.Integer(), nullable=True),
        sa.Column('duct_tape_used', sa.Boolean(), nullable=True),
        sa.Column('supply_closet_raids', sa.Integer(), nullable=True),
        sa.Column('redneck_ingenuity_level', sa.Float(), nullable=True),
        sa.Column('engineering_solution', sa.String(), nullable=True),
        sa.Column('beer_level_before', sa.String(), nullable=True),
        sa.Column('beer_level_after', sa.String(), nullable=True),
        sa.Column('duct_tape_inventory_used', sa.Integer(), nullable=True),
        sa.Column('supply_closet_items', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('urgency_level', sa.String(), nullable=True),
        sa.Column('priority_level', sa.String(), nullable=True),
        sa.Column('pattern_confidence', sa.Float(), nullable=True),
        sa.Column('learned_from_patterns', sa.Boolean(), nullable=True),
        sa.Column('historical_data_points', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        
    )
    
    # Copy data from old table to new table (if any exists)
    op.execute("""
        INSERT INTO tuning_history_new 
        SELECT 
            CAST(id AS TEXT) as id,
            CAST(user_id AS TEXT) as user_id,
            parameter, old_value, new_value, success, error,
            metrics_before, metrics_after, timestamp,
            beer_consumed, duct_tape_used, supply_closet_raids,
            redneck_ingenuity_level, engineering_solution,
            beer_level_before, beer_level_after, duct_tape_inventory_used,
            supply_closet_items, confidence_score, impact_score,
            urgency_level, priority_level, pattern_confidence,
            learned_from_patterns, historical_data_points
        FROM tuning_history
    """)
    
    # Drop old table and rename new one
    op.drop_table('tuning_history')
    op.rename_table('tuning_history_new', 'tuning_history')
    
    # Recreate index
    op.create_index(op.f('ix_tuning_history_id'), 'tuning_history', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Revert tuning_history data types back to INTEGER."""
    # Create old table with INTEGER types
    op.create_table('tuning_history_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parameter', sa.String(), nullable=False),
        sa.Column('old_value', sa.String(), nullable=True),
        sa.Column('new_value', sa.String(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('metrics_before', sa.JSON(), nullable=True),
        sa.Column('metrics_after', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('beer_consumed', sa.Integer(), nullable=True),
        sa.Column('duct_tape_used', sa.Boolean(), nullable=True),
        sa.Column('supply_closet_raids', sa.Integer(), nullable=True),
        sa.Column('redneck_ingenuity_level', sa.Float(), nullable=True),
        sa.Column('engineering_solution', sa.String(), nullable=True),
        sa.Column('beer_level_before', sa.String(), nullable=True),
        sa.Column('beer_level_after', sa.String(), nullable=True),
        sa.Column('duct_tape_inventory_used', sa.Integer(), nullable=True),
        sa.Column('supply_closet_items', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('urgency_level', sa.String(), nullable=True),
        sa.Column('priority_level', sa.String(), nullable=True),
        sa.Column('pattern_confidence', sa.Float(), nullable=True),
        sa.Column('learned_from_patterns', sa.Boolean(), nullable=True),
        sa.Column('historical_data_points', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        
    )
    
    # Copy data back (converting UUIDs back to integers - this may cause data loss)
    op.execute("""
        INSERT INTO tuning_history_old 
        SELECT 
            CAST(id AS INTEGER) as id,
            CAST(user_id AS INTEGER) as user_id,
            parameter, old_value, new_value, success, error,
            metrics_before, metrics_after, timestamp,
            beer_consumed, duct_tape_used, supply_closet_raids,
            redneck_ingenuity_level, engineering_solution,
            beer_level_before, beer_level_after, duct_tape_inventory_used,
            supply_closet_items, confidence_score, impact_score,
            urgency_level, priority_level, pattern_confidence,
            learned_from_patterns, historical_data_points
        FROM tuning_history
    """)
    
    # Drop new table and rename old one back
    op.drop_table('tuning_history')
    op.rename_table('tuning_history_old', 'tuning_history')
    
    # Recreate index
    op.create_index(op.f('ix_tuning_history_id'), 'tuning_history', ['id'], unique=False)