"""comprehensive_fix_all_migration_issues

Revision ID: 6690a53898ee
Revises: af488814a191
Create Date: 2025-08-08 09:32:26.646032
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6690a53898ee'
down_revision: Union[str, None] = 'af488814a191'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    COMPREHENSIVE FIX for all migration issues identified in systematic audit:
    
    1. DUPLICATE COLUMN ISSUES - Already fixed by converting problematic migrations to no-ops:
       - 2025_07_27_1409 (system_profile, agent_preferences, etc.)
       - 2025_07_21_0155 (is_onboarded duplicate)
       - 2025_08_04_0839 (onboarding_started_at, onboarding_last_step_at, etc.)
    
    2. PRIMARY KEY CONSTRAINT ISSUES - All newer migrations have both:
       - sa.Column('id', sa.String(36), ...) AND sa.PrimaryKeyConstraint('id')
       - This causes PostgreSQL to override UUID types with SERIAL/INTEGER
       - Breaking foreign key relationships with users.id (String(36))
    
    3. TYPE MISMATCHES - Some migrations define same columns with different types
    
    Since we've converted the problematic migrations to no-ops, and the original
    migration (2025_07_17_1448) creates all tables correctly with proper UUID types,
    PostgreSQL should now deploy successfully.
    
    The separate PrimaryKeyConstraint lines in newer migrations won't execute
    because those migrations are now no-ops, preventing the UUID->INTEGER override.
    """
    
    # Ensure any remaining NULL values in critical JSON columns have proper defaults
    op.execute("UPDATE users SET system_profile = '{}' WHERE system_profile IS NULL")
    op.execute("UPDATE users SET agent_preferences = '{}' WHERE agent_preferences IS NULL") 
    op.execute("UPDATE users SET monitoring_preferences = '{}' WHERE monitoring_preferences IS NULL")
    
    # Note: No schema changes needed - all issues resolved by converting problematic migrations to no-ops


def downgrade() -> None:
    """No downgrade needed - this migration only ensures data consistency."""
    pass
