"""add_onboarding_progress_tracking

Revision ID: 82f8ee1a2066
Revises: b958c3a4c078
Create Date: 2025-08-04 07:38:21.927325
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82f8ee1a2066'
down_revision: Union[str, None] = 'b958c3a4c078'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add onboarding progress tracking columns
    # SQLite will store JSON as TEXT automatically
    op.add_column('users', sa.Column('onboarding_progress', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('onboarding_started_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('onboarding_last_step_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('onboarding_abandoned_count', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    # Remove onboarding progress tracking columns
    op.drop_column('users', 'onboarding_abandoned_count')
    op.drop_column('users', 'onboarding_last_step_at')
    op.drop_column('users', 'onboarding_started_at')
    op.drop_column('users', 'onboarding_progress')