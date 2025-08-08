"""Update user model for onboarding and system profile

Revision ID: b958c3a4c078
Revises: f717dcc399f9
Create Date: 2025-07-27 14:09:52.467396
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import json

# revision identifiers, used by Alembic.
revision: str = 'b958c3a4c078'
down_revision: Union[str, None] = 'f717dcc399f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # This migration now only adds columns that are NOT created in other migrations
    # to prevent duplicate column errors during deployment.
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('system_profile', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('onboarding_completed', sa.Boolean(), nullable=True))
        # batch_op.add_column(sa.Column('onboarding_progress', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('monitoring_thresholds', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('permissions_status', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('installation_method', sa.String(length=50), nullable=True))

    # Set default values for new columns on existing rows
    op.execute("UPDATE users SET system_profile = '{}' WHERE system_profile IS NULL")
    op.execute("UPDATE users SET onboarding_completed = false WHERE onboarding_completed IS NULL")

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('installation_method')
        batch_op.drop_column('permissions_status')
        batch_op.drop_column('monitoring_thresholds')
        # batch_op.drop_column('onboarding_progress')
        batch_op.drop_column('onboarding_completed')
        batch_op.drop_column('system_profile')