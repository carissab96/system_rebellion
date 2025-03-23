"""initial migration

Revision ID: 74504bba0ad0
Revises: 
Create Date: 2025-03-21 13:41:37.152626
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74504bba0ad0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Resurrect the tables from quantum oblivion"""
    # Users Table
    op.create_table('users',
    sa.Column('id', sa.String(36), primary_key=True),
    sa.Column('username', sa.String(50), nullable=False, unique=True),
    sa.Column('email', sa.String(100), nullable=False, unique=True),
    sa.Column('hashed_password', sa.String(255), nullable=False),
    sa.Column('first_name', sa.String(50), nullable=True),
    sa.Column('last_name', sa.String(50), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('profile_picture', sa.String(255), nullable=True),
    sa.Column('is_active', sa.Boolean(), default=True),
    sa.Column('is_superuser', sa.Boolean(), default=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

    # User Profiles Table
    op.create_table('user_profiles',
    sa.Column('id', sa.String(36), primary_key=True),
    sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
    sa.Column('location', sa.String(100), nullable=True),
    sa.Column('website', sa.String(200), nullable=True),
    sa.Column('github_username', sa.String(50), nullable=True),
    sa.Column('linkedin_profile', sa.String(200), nullable=True),
    sa.Column('theme_preference', sa.String(20), default='system'),
    sa.Column('notification_settings', sa.String(100), default='all'),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

def downgrade() -> None:
    """Quantum Shadow People Removal Protocol"""
    op.drop_table('user_profiles')
    op.drop_table('users')