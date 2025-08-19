"""add canonical memory tables

Revision ID: db5aaa2d6c36
Revises: 34e341e63e9a
Create Date: 2025-08-18 08:51:13.735917
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db5aaa2d6c36'
down_revision: Union[str, None] = '34e341e63e9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'agent_memories',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('agent_name', sa.String(), nullable=False, index=True),
        sa.Column('memory_type', sa.String(), nullable=False, index=True),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('importance', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_mem_user_agent_type_time',
                    'agent_memories',
                    ['user_id', 'agent_name', 'memory_type', 'timestamp'])

    op.create_table(
        'agent_global_patterns',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('pattern_key', sa.String(), nullable=False, index=True),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )
    op.create_index('ix_global_pattern_key', 'agent_global_patterns', ['pattern_key'])

def downgrade():
    op.drop_index('ix_global_pattern_key', table_name='agent_global_patterns')
    op.drop_table('agent_global_patterns')
    op.drop_index('ix_mem_user_agent_type_time', table_name='agent_memories')
    op.drop_table('agent_memories')