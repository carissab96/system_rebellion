"""add_hamsters_engineering_fields

Revision ID: 212c7bed07af
Revises: 45a4ef80f0b6
Create Date: 2025-07-06 11:27:43.247944
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '212c7bed07af'
down_revision: Union[str, None] = '45a4ef80f0b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Add The Hamsters engineering fields to tuning_history table only."""
    
    # Check if columns already exist to avoid errors
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('tuning_history')]
    
    # Add Hamsters engineering tracking fields (only if they don't exist)
    if 'beer_consumed' not in columns:
        op.add_column('tuning_history', sa.Column('beer_consumed', sa.Integer(), nullable=True, default=0))
    if 'duct_tape_used' not in columns:
        op.add_column('tuning_history', sa.Column('duct_tape_used', sa.Boolean(), nullable=True, default=False))
    if 'supply_closet_raids' not in columns:
        op.add_column('tuning_history', sa.Column('supply_closet_raids', sa.Integer(), nullable=True, default=0))
    if 'redneck_ingenuity_level' not in columns:
        op.add_column('tuning_history', sa.Column('redneck_ingenuity_level', sa.Float(), nullable=True, default=0.0))
    if 'engineering_solution' not in columns:
        op.add_column('tuning_history', sa.Column('engineering_solution', sa.String(), nullable=True))
    if 'beer_level_before' not in columns:
        op.add_column('tuning_history', sa.Column('beer_level_before', sa.String(), nullable=True, default='FULL'))
    if 'beer_level_after' not in columns:
        op.add_column('tuning_history', sa.Column('beer_level_after', sa.String(), nullable=True, default='FULL'))
    if 'duct_tape_inventory_used' not in columns:
        op.add_column('tuning_history', sa.Column('duct_tape_inventory_used', sa.Integer(), nullable=True, default=0))
    if 'supply_closet_items' not in columns:
        op.add_column('tuning_history', sa.Column('supply_closet_items', sa.JSON(), nullable=True))
    
    # Add engineering quality metrics
    if 'confidence_score' not in columns:
        op.add_column('tuning_history', sa.Column('confidence_score', sa.Float(), nullable=True, default=0.0))
    if 'impact_score' not in columns:
        op.add_column('tuning_history', sa.Column('impact_score', sa.Float(), nullable=True, default=0.0))
    if 'urgency_level' not in columns:
        op.add_column('tuning_history', sa.Column('urgency_level', sa.String(), nullable=True, default='LOW'))
    if 'priority_level' not in columns:
        op.add_column('tuning_history', sa.Column('priority_level', sa.String(), nullable=True, default='BEER_BREAK'))
    
    # Add pattern learning data
    if 'pattern_confidence' not in columns:
        op.add_column('tuning_history', sa.Column('pattern_confidence', sa.Float(), nullable=True, default=0.0))
    if 'learned_from_patterns' not in columns:
        op.add_column('tuning_history', sa.Column('learned_from_patterns', sa.Boolean(), nullable=True, default=False))
    if 'historical_data_points' not in columns:
        op.add_column('tuning_history', sa.Column('historical_data_points', sa.Integer(), nullable=True, default=0))
    
    # Set defaults for existing records (safe even if no existing records)
    op.execute("UPDATE tuning_history SET beer_consumed = 0 WHERE beer_consumed IS NULL")
    op.execute("UPDATE tuning_history SET duct_tape_used = 0 WHERE duct_tape_used IS NULL")
    op.execute("UPDATE tuning_history SET supply_closet_raids = 0 WHERE supply_closet_raids IS NULL")
    op.execute("UPDATE tuning_history SET redneck_ingenuity_level = 0.0 WHERE redneck_ingenuity_level IS NULL")
    op.execute("UPDATE tuning_history SET beer_level_before = 'FULL' WHERE beer_level_before IS NULL")
    op.execute("UPDATE tuning_history SET beer_level_after = 'FULL' WHERE beer_level_after IS NULL")
    op.execute("UPDATE tuning_history SET duct_tape_inventory_used = 0 WHERE duct_tape_inventory_used IS NULL")
    op.execute("UPDATE tuning_history SET confidence_score = 0.0 WHERE confidence_score IS NULL")
    op.execute("UPDATE tuning_history SET impact_score = 0.0 WHERE impact_score IS NULL")
    op.execute("UPDATE tuning_history SET urgency_level = 'LOW' WHERE urgency_level IS NULL")
    op.execute("UPDATE tuning_history SET priority_level = 'BEER_BREAK' WHERE priority_level IS NULL")
    op.execute("UPDATE tuning_history SET pattern_confidence = 0.0 WHERE pattern_confidence IS NULL")
    op.execute("UPDATE tuning_history SET learned_from_patterns = 0 WHERE learned_from_patterns IS NULL")
    op.execute("UPDATE tuning_history SET historical_data_points = 0 WHERE historical_data_points IS NULL")

def downgrade() -> None:
    """Remove The Hamsters engineering fields from tuning_history table."""
    
    # Remove columns in reverse order
    try:
        op.drop_column('tuning_history', 'historical_data_points')
        op.drop_column('tuning_history', 'learned_from_patterns')
        op.drop_column('tuning_history', 'pattern_confidence')
        op.drop_column('tuning_history', 'priority_level')
        op.drop_column('tuning_history', 'urgency_level')
        op.drop_column('tuning_history', 'impact_score')
        op.drop_column('tuning_history', 'confidence_score')
        op.drop_column('tuning_history', 'supply_closet_items')
        op.drop_column('tuning_history', 'duct_tape_inventory_used')
        op.drop_column('tuning_history', 'beer_level_after')
        op.drop_column('tuning_history', 'beer_level_before')
        op.drop_column('tuning_history', 'engineering_solution')
        op.drop_column('tuning_history', 'redneck_ingenuity_level')
        op.drop_column('tuning_history', 'supply_closet_raids')
        op.drop_column('tuning_history', 'duct_tape_used')
        op.drop_column('tuning_history', 'beer_consumed')
    except Exception as e:
        # If columns don't exist, that's fine
        pass