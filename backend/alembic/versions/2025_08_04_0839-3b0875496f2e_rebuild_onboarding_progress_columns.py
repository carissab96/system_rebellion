"""rebuild_onboarding_progress_columns

Revision ID: 3b0875496f2e
Revises: 82f8ee1a2066
Create Date: 2025-08-04 08:39:00.863637
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b0875496f2e'
down_revision: Union[str, None] = '82f8ee1a2066'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Keep existing onboarding_progress INTEGER (probably tracks current step)
    # Add new columns for detailed tracking
    op.add_column('users', sa.Column('onboarding_data', sa.Text(), nullable=True))  # JSON data
    op.add_column('users', sa.Column('onboarding_started_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('onboarding_last_step_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('onboarding_abandoned_count', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('users', 'onboarding_abandoned_count')
    op.drop_column('users', 'onboarding_last_step_at')
    op.drop_column('users', 'onboarding_started_at')
    op.drop_column('users', 'onboarding_data')
    # Don't touch the existing onboarding_progress INTEGER