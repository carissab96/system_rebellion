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
    op.alter_column('agent_learning_records', 'root_cause',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=500),
                    existing_nullable=True)
    
    op.alter_column('agent_learning_records', 'what_worked',
                    existing_type=sa.String(),
                    type_=sa.String(length=500),
                    existing_nullable=True)
    
    op.alter_column('agent_learning_records', 'what_failed',
                    existing_type=sa.String(),
                    type_=sa.String(length=500),
                    existing_nullable=True)


def downgrade() -> None:
    """Revert text column sizes back to original."""
    op.alter_column('agent_learning_records', 'root_cause',
                    existing_type=sa.String(length=500),
                    type_=sa.String(length=50),
                    existing_nullable=True)
    
    op.alter_column('agent_learning_records', 'what_worked',
                    existing_type=sa.String(length=500),
                    type_=sa.String(),
                    existing_nullable=True)
    
    op.alter_column('agent_learning_records', 'what_failed',
                    existing_type=sa.String(length=500),
                    type_=sa.String(),
                    existing_nullable=True)
