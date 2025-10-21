"""Add is onboarded field to users table

Revision ID: 409bd22154f8
Revises: d573ad249444
Create Date: 2025-07-21 01:55:54.374354
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '409bd22154f8'
down_revision: Union[str, None] = 'd573ad249444'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_onboarded field to users table."""
    # Column already exists in original migration - no action needed
    pass

def downgrade() -> None:
    """Remove is_onboarded field from users table."""
    # Column managed by original migration - no action needed
    pass