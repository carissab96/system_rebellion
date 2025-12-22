"""add agent_learning_records table for terry v2

Revision ID: 84bbeb827a40
Revises: 9e60a1bdc15d
Create Date: 2025-12-22 12:33:11.008619
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84bbeb827a40'
down_revision: Union[str, None] = '9e60a1bdc15d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
