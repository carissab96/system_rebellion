"""drop_central_memory_bank_foreign_keys constraints

Revision ID: b1daa7a52da4
Revises: 3734e17210c3
Create Date: 2025-12-05 12:36:23.369705
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1daa7a52da4'
down_revision: Union[str, None] = '3734e17210c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
