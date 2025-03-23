"""Add last_login, failed_login_attempts, and lockout_until columns

Revision ID: 85560d772dd4
Revises: e844df608b0b
Create Date: 2025-03-22 13:49:36.621207
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '85560d772dd4'
down_revision: Union[str, None] = 'e844df608b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('lockout_until', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'lockout_until')