"""enhanced onboarding tracking in user table

Revision ID: 5252a4dd6395
Revises: e05a2d49ffff
Create Date: 2025-08-06 23:46:46.848893
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5252a4dd6395'
down_revision: Union[str, None] = 'e05a2d49ffff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Enhanced onboarding tracking
    op.add_column('users', sa.Column('onboarding_step_timestamps', sa.TEXT(), nullable=True))
    op.add_column('users', sa.Column('onboarding_abandonment_reasons', sa.TEXT(), nullable=True))
    op.add_column('users', sa.Column('onboarding_device_info', sa.TEXT(), nullable=True))
    op.add_column('users', sa.Column('onboarding_referral_source', sa.String(100), nullable=True))
    
    # Preview/Trial tracking
    op.add_column('users', sa.Column('preview_agent_selected', sa.String(20), nullable=True))
    op.add_column('users', sa.Column('preview_started_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('preview_expires_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('preview_conversion_emails_sent', sa.TEXT(), nullable=True))
    op.add_column('users', sa.Column('preview_converted_at', sa.DateTime(), nullable=True))
    
    # Email campaign tracking
    op.add_column('users', sa.Column('email_campaign_responses', sa.TEXT(), nullable=True))
    op.add_column('users', sa.Column('last_engagement_at', sa.DateTime(), nullable=True))

def downgrade():
    # Remove email campaign tracking
    op.drop_column('users', 'last_engagement_at')
    op.drop_column('users', 'email_campaign_responses')
    
    # Remove preview/trial tracking
    op.drop_column('users', 'preview_converted_at')
    op.drop_column('users', 'preview_conversion_emails_sent')
    op.drop_column('users', 'preview_expires_at')
    op.drop_column('users', 'preview_started_at')
    op.drop_column('users', 'preview_agent_selected')
    
    # Remove enhanced onboarding tracking
    op.drop_column('users', 'onboarding_referral_source')
    op.drop_column('users', 'onboarding_device_info')
    op.drop_column('users', 'onboarding_abandonment_reasons')
    op.drop_column('users', 'onboarding_step_timestamps')