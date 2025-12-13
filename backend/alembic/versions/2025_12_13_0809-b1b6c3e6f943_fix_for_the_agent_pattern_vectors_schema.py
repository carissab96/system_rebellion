"""fix for the agent_pattern_vectors schema

Revision ID: b1b6c3e6f943
Revises: 9e60a1bdc15d
Create Date: 2025-12-13 08:09:11.291708
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1b6c3e6f943'
down_revision: Union[str, None] = '9e60a1bdc15d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
