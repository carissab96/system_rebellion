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
    # NO-OP: All columns this migration was trying to add already exist
    # This migration was causing PostgreSQL duplicate column errors during deployment
    
    # The following columns already exist in the users table (added by previous migrations):
    # - onboarding_data (added in migration 2025_08_04_0738)
    # - onboarding_started_at (added in migration 2025_08_04_0738)  
    # - onboarding_last_step_at (added in migration 2025_08_04_0738)
    # - onboarding_abandoned_count (added in migration 2025_08_04_0738)
    
    pass

def downgrade():
    # NO-OP: This migration doesn't add any columns, so no downgrade needed
    # Columns exist from previous migration and should not be dropped
    pass