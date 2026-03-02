"""add central_memory_id_to_action_outcomes

Revision ID: c0ecfec9e5af
Revises: 58e893ae4e16
Create Date: 2026-02-18 10:06:29.021308
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c0ecfec9e5af'
down_revision: Union[str, None] = '58e893ae4e16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add central_memory_id column to action_outcome_records
    op.add_column('action_outcome_records', 
        sa.Column('central_memory_id', sa.String(length=36), nullable=True)
    )
    
    # Add index for central_memory_id lookups
    op.create_index('ix_action_outcome_records_central_memory_id', 
                    'action_outcome_records', 
                    ['central_memory_id'])


def downgrade():
    # Remove index
    op.drop_index('ix_action_outcome_records_central_memory_id', 
                  table_name='action_outcome_records')
    
    # Remove column
    op.drop_column('action_outcome_records', 'central_memory_id')
