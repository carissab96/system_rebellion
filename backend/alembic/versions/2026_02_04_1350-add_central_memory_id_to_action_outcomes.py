"""add central_memory_id to action_outcome_records

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-04 13:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


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
