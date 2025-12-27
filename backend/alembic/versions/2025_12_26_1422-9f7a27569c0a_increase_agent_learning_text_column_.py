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
    """Increase text column sizes for agent learning records."""
    # Use raw SQL for faster execution
    op.execute('ALTER TABLE agent_learning_records ALTER COLUMN root_cause TYPE VARCHAR(500)')
    op.execute('ALTER TABLE agent_learning_records ALTER COLUMN what_worked TYPE VARCHAR(500)')
    op.execute('ALTER TABLE agent_learning_records ALTER COLUMN what_failed TYPE VARCHAR(500)')


def downgrade() -> None:
    """Revert text column sizes back to original."""
    # Use raw SQL for faster execution
    op.execute('ALTER TABLE agent_learning_records ALTER COLUMN root_cause TYPE VARCHAR(50)')
    op.execute('ALTER TABLE agent_learning_records ALTER COLUMN what_worked TYPE TEXT')
    op.execute('ALTER TABLE agent_learning_records ALTER COLUMN what_failed TYPE TEXT')
