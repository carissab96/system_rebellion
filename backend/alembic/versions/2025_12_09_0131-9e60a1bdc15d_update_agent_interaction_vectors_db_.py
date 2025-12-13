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
    # Get the current table info
    inspector = sa.inspect(op.get_bind())
    columns = [col['name'] for col in inspector.get_columns('agent_interaction_vectors')]
    indexes = [idx['name'] for idx in inspector.get_indexes('agent_interaction_vectors')]
    
    # Only rename columns if they exist and new names don't
    if 'from_agent' in columns and 'primary_agent' not in columns:
        op.alter_column('agent_interaction_vectors', 'from_agent', new_column_name='primary_agent')
    if 'to_agent' in columns and 'secondary_agent' not in columns:
        op.alter_column('agent_interaction_vectors', 'to_agent', new_column_name='secondary_agent')
    
    # Add new columns if they don't exist
    if 'user_id' not in columns:
        op.add_column('agent_interaction_vectors', sa.Column('user_id', sa.String(255), nullable=False, server_default='system'))
    if 'outcome' not in columns:
        op.add_column('agent_interaction_vectors', sa.Column('outcome', sa.String(255), nullable=True))
    if 'success_score' not in columns:
        op.add_column('agent_interaction_vectors', sa.Column('success_score', sa.Float(), nullable=True))
    if 'sql_interaction_id' not in columns:
        op.add_column('agent_interaction_vectors', sa.Column('sql_interaction_id', sa.String(255), nullable=True))
    
    # Drop old columns if they exist
    if 'priority' in columns:
        op.drop_column('agent_interaction_vectors', 'priority')
    if 'embedding_model' in columns:
        op.drop_column('agent_interaction_vectors', 'embedding_model')
    
    # Create indexes only if they don't exist
    if 'idx_agent_interaction_vectors_primary' not in indexes:
        op.execute('CREATE INDEX idx_agent_interaction_vectors_primary ON agent_interaction_vectors(primary_agent, occurred_at DESC)')
    if 'idx_agent_interaction_vectors_secondary' not in indexes:
        op.execute('CREATE INDEX idx_agent_interaction_vectors_secondary ON agent_interaction_vectors(secondary_agent, occurred_at DESC)')
    if 'idx_agent_interaction_vectors_pair' not in indexes:
        op.execute('CREATE INDEX idx_agent_interaction_vectors_pair ON agent_interaction_vectors(primary_agent, secondary_agent, occurred_at DESC)')


def downgrade() -> None:
    """Revert to original schema."""
    inspector = sa.inspect(op.get_bind())
    columns = [col['name'] for col in inspector.get_columns('agent_interaction_vectors')]
    indexes = [idx['name'] for idx in inspector.get_indexes('agent_interaction_vectors')]
    
    # Drop new indexes if they exist
    for idx in ['idx_agent_interaction_vectors_primary', 'idx_agent_interaction_vectors_secondary', 
               'idx_agent_interaction_vectors_pair', 'idx_agent_interaction_vectors_user']:
        if idx in indexes:
            op.drop_index(idx, table_name='agent_interaction_vectors')
    
    # Add back old columns if they don't exist
    if 'priority' not in columns:
        op.add_column('agent_interaction_vectors', sa.Column('priority', sa.Integer(), nullable=False, server_default='2'))
    if 'embedding_model' not in columns:
        op.add_column('agent_interaction_vectors', sa.Column('embedding_model', sa.String(100), nullable=False, server_default='all-MiniLM-L6-v2'))
    
    # Drop new columns if they exist
    for col in ['user_id', 'outcome', 'success_score', 'sql_interaction_id']:
        if col in columns:
            op.drop_column('agent_interaction_vectors', col)
    
    # Rename columns back if they exist
    if 'primary_agent' in columns and 'from_agent' not in columns:
        op.alter_column('agent_interaction_vectors', 'primary_agent', new_column_name='from_agent')
    if 'secondary_agent' in columns and 'to_agent' not in columns:
        op.alter_column('agent_interaction_vectors', 'secondary_agent', new_column_name='to_agent')
    
    # Recreate old indexes if they don't exist
    if 'idx_agent_interaction_vectors_from' not in indexes:
        op.create_index('idx_agent_interaction_vectors_from', 'agent_interaction_vectors', ['from_agent'])
    if 'idx_agent_interaction_vectors_to' not in indexes:
        op.create_index('idx_agent_interaction_vectors_to', 'agent_interaction_vectors', ['to_agent'])
    if 'idx_agent_interaction_vectors_pair' not in indexes:
        op.create_index('idx_agent_interaction_vectors_pair', 'agent_interaction_vectors', ['from_agent', 'to_agent'])
