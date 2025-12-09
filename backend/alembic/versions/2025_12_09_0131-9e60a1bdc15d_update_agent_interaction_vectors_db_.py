"""update agent_interaction_vectors db schema and table

Revision ID: 9e60a1bdc15d
Revises: b1daa7a52da4
Create Date: 2025-12-09 01:31:19.202496
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e60a1bdc15d'
down_revision: Union[str, None] = 'b1daa7a52da4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
