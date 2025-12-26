"""increase agent learning text column sizes

Revision ID: 9f7a27569c0a
Revises: 84bbeb827a40
Create Date: 2025-12-26 14:22:01.042211
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f7a27569c0a'
down_revision: Union[str, None] = '84bbeb827a40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
