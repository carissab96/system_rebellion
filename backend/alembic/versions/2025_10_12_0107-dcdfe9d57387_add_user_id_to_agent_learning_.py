"""add_user_id_to_agent_learning_interactions

Revision ID: dcdfe9d57387
Revises: 275af0769985
Create Date: 2025-10-12 01:07:55.594707
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcdfe9d57387'
down_revision: Union[str, None] = '275af0769985'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user_id to agent_learning_interactions"""
    with op.batch_alter_table('agent_learning_interactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.String(length=255), nullable=True))
        batch_op.create_index('ix_agent_learning_interactions_user_id', ['user_id'])
        batch_op.create_foreign_key(
            'fk_agent_learning_interactions_user_id',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )

def downgrade() -> None:
    with op.batch_alter_table('agent_learning_interactions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_agent_learning_interactions_user_id', type_='foreignkey')
        batch_op.drop_index('ix_agent_learning_interactions_user_id')
        batch_op.drop_column('user_id')
