"""update agent_interaction_vectors db schema and table

Revision ID: 9e60a1bdc15d
Revises: b1daa7a52da4
Create Date: 2025-12-09 01:31:19.202496
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e60a1bdc15d'
down_revision: Union[str, None] = 'b1daa7a52da4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade agent_interaction_vectors to richer schema."""
    # Rename columns
    op.alter_column('agent_interaction_vectors', 'from_agent', new_column_name='primary_agent')
    op.alter_column('agent_interaction_vectors', 'to_agent', new_column_name='secondary_agent')
    
    # Add new columns
    op.add_column('agent_interaction_vectors', sa.Column('user_id', sa.String(255), nullable=False, server_default='system'))
    op.add_column('agent_interaction_vectors', sa.Column('outcome', sa.String(255), nullable=True))
    op.add_column('agent_interaction_vectors', sa.Column('success_score', sa.Float, nullable=True))
    op.add_column('agent_interaction_vectors', sa.Column('sql_interaction_id', sa.String(255), nullable=True))
    
    # Drop old columns
    op.drop_column('agent_interaction_vectors', 'priority')
    op.drop_column('agent_interaction_vectors', 'embedding_model')
    
    # Drop old indexes
    op.drop_index('idx_agent_interaction_vectors_from', table_name='agent_interaction_vectors')
    op.drop_index('idx_agent_interaction_vectors_to', table_name='agent_interaction_vectors')
    op.drop_index('idx_agent_interaction_vectors_pair', table_name='agent_interaction_vectors')
    
    # Create new indexes
    op.create_index('idx_agent_interaction_vectors_primary', 'agent_interaction_vectors', ['primary_agent', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_interaction_vectors_secondary', 'agent_interaction_vectors', ['secondary_agent', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_interaction_vectors_pair', 'agent_interaction_vectors', ['primary_agent', 'secondary_agent', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_interaction_vectors_user', 'agent_interaction_vectors', ['user_id', sa.text('occurred_at DESC')])


def downgrade() -> None:
    """Revert to original schema."""
    # Drop new indexes
    op.drop_index('idx_agent_interaction_vectors_primary', table_name='agent_interaction_vectors')
    op.drop_index('idx_agent_interaction_vectors_secondary', table_name='agent_interaction_vectors')
    op.drop_index('idx_agent_interaction_vectors_pair', table_name='agent_interaction_vectors')
    op.drop_index('idx_agent_interaction_vectors_user', table_name='agent_interaction_vectors')
    
    # Add back old columns
    op.add_column('agent_interaction_vectors', sa.Column('priority', sa.Integer, nullable=False, server_default='2'))
    op.add_column('agent_interaction_vectors', sa.Column('embedding_model', sa.String(100), nullable=False, server_default='all-MiniLM-L6-v2'))
    
    # Drop new columns
    op.drop_column('agent_interaction_vectors', 'sql_interaction_id')
    op.drop_column('agent_interaction_vectors', 'success_score')
    op.drop_column('agent_interaction_vectors', 'outcome')
    op.drop_column('agent_interaction_vectors', 'user_id')
    
    # Rename columns back
    op.alter_column('agent_interaction_vectors', 'primary_agent', new_column_name='from_agent')
    op.alter_column('agent_interaction_vectors', 'secondary_agent', new_column_name='to_agent')
    
    # Recreate old indexes
    op.create_index('idx_agent_interaction_vectors_from', 'agent_interaction_vectors', ['from_agent', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_interaction_vectors_to', 'agent_interaction_vectors', ['to_agent', sa.text('occurred_at DESC')])
    op.create_index('idx_agent_interaction_vectors_pair', 'agent_interaction_vectors', ['from_agent', 'to_agent', sa.text('occurred_at DESC')])
