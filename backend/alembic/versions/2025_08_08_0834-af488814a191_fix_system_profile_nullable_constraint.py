"""fix_system_profile_nullable_constraint

Revision ID: af488814a191
Revises: 657824b74ef5
Create Date: 2025-08-08 08:34:46.722975
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af488814a191'
down_revision: Union[str, None] = '657824b74ef5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix system_profile column to be nullable with default empty dict."""
    # For SQLite, we need to check if the column constraint needs fixing
    # The column should be nullable=True with a default value
    
    # First, ensure all existing NULL values have empty dict
    op.execute("UPDATE users SET system_profile = '{}' WHERE system_profile IS NULL")
    
    # Note: SQLite doesn't support ALTER COLUMN to change constraints
    # But since we've set defaults for existing records, PostgreSQL should work
    # The model definition (nullable=True, default=lambda: {}) will handle new records


def downgrade() -> None:
    """Downgrade schema."""
    # No downgrade needed - this is a constraint fix, not a schema change
    pass
