"""Create users and user_profiles tables]

Revision ID: d578c3f6b64f
Revises: 9a7a4a83b4af
Create Date: 2025-03-19 10:38:39.594830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd578c3f6b64f'
down_revision: Union[str, None] = '9a7a4a83b4af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(length=50), unique=True, nullable=False),
        sa.Column('email', sa.String(length=100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=True),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('bio', sa.Text, nullable=True),
        sa.Column('profile_picture', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_superuser', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('github_username', sa.String(length=50), nullable=True),
        sa.Column('linkedin_profile', sa.String(length=200), nullable=True),
        sa.Column('theme_preference', sa.String(length=20), default='system'),
        sa.Column('notification_settings', sa.String(length=100), default='all')
    )

def downgrade() -> None:
    """Downgrade schema."""
    # Drop user_profiles table first due to foreign key constraint
    op.drop_table('user_profiles')
    op.drop_table('users')