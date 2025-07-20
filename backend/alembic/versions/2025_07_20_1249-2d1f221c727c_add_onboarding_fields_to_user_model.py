"""Add onboarding fields to user model

Revision ID: 2d1f221c727c
Revises: 5a53b4abfd5b
Create Date: 2025-07-20 12:49:10.803005
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d1f221c727c'
down_revision: Union[str, None] = '5a53b4abfd5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add onboarding configuration fields to users table."""
    # Add new columns to users table - these are SAFE additions that won't affect existing data
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('system_name', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('ram_gb', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('storage_gb', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('primary_use_case', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('monitoring_preferences', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('agent_preferences', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema - Remove onboarding configuration fields from users table."""
    # Remove the columns in reverse order if we need to rollback
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('agent_preferences')
        batch_op.drop_column('monitoring_preferences')
        batch_op.drop_column('primary_use_case')
        batch_op.drop_column('storage_gb')
        batch_op.drop_column('ram_gb')
        batch_op.drop_column('system_name')
