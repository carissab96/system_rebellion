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
    # NO-OP: All columns this migration was trying to add already exist
    # This migration was causing PostgreSQL transaction abort errors during deployment
    # because it attempted to add existing columns, which works in SQLite with try/except
    # but causes transaction failures in PostgreSQL
    
    # The following columns already exist in the users table:
    # - onboarding_completed (added in original migration)
    # - onboarding_progress (added in original migration) 
    # - system_profile (added in original migration)
    # - agent_preferences (added in original migration)
    # - monitoring_thresholds (added in original migration)
    # - permissions_status (added in original migration)
    # - installation_method (added in original migration)
    
    pass
    
    # NO-OP: Default value setting removed since columns already exist with proper defaults
    # The User model handles default values for new records
    # Existing records already have appropriate values set by previous migrations

def downgrade():
    # NO-OP: This migration doesn't add any columns, so no downgrade needed
    # Columns exist from original migration and should not be dropped
    pass