"""add agent_memory_global_patterns table

Revision ID: 34e341e63e9a
Revises: 6690a53898ee
Create Date: 2025-08-16 10:37:51.498351
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34e341e63e9a'
down_revision: Union[str, None] = '6690a53898ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        'agent_memory_global_patterns',
        sa.Column('agent_name', sa.String(), nullable=False),
        sa.Column('pattern_key', sa.String(), nullable=False),
        sa.Column('value', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('agent_name', 'pattern_key')
    )

def downgrade():
    op.drop_table('agent_memory_global_patterns')
