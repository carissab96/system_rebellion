"""add foreign key to user id

Revision ID: 275af0769985
Revises: afae548fcd28
Create Date: 2025-10-11 20:21:57.553850
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '275af0769985'
down_revision: Union[str, None] = 'afae548fcd28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# backend/alembic/versions/XXXXX_add_foreign_keys_to_agent_memory_tables.py

def upgrade() -> None:
    """Add foreign key constraints to agent memory tables using batch mode for SQLite"""
    
    # Sir Hawkington - batch mode
    with op.batch_alter_table('sir_hawkington_memory_bank', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_sir_hawkington_user_id',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )
    
    # The Stick - batch mode
    with op.batch_alter_table('the_stick_memory_bank', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_the_stick_user_id',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )
    
    # Meth Snail - batch mode
    with op.batch_alter_table('meth_snail_memory_bank', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_meth_snail_user_id',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )
    
    # Hamsters - batch mode
    with op.batch_alter_table('hamsters_memory_bank', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_hamsters_user_id',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )
    
    # Quantum Shadow People - batch mode
    with op.batch_alter_table('quantum_shadow_people_memory_bank', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_qsp_user_id',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )
    
    # VIC-20 - batch mode
    with op.batch_alter_table('vic20_memory_bank', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_vic20_user_id',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    """Remove foreign key constraints using batch mode for SQLite"""
    
    with op.batch_alter_table('vic20_memory_bank', schema=None) as batch_op:
        batch_op.drop_constraint('fk_vic20_user_id', type_='foreignkey')
    
    with op.batch_alter_table('quantum_shadow_people_memory_bank', schema=None) as batch_op:
        batch_op.drop_constraint('fk_qsp_user_id', type_='foreignkey')
    
    with op.batch_alter_table('hamsters_memory_bank', schema=None) as batch_op:
        batch_op.drop_constraint('fk_hamsters_user_id', type_='foreignkey')
    
    with op.batch_alter_table('meth_snail_memory_bank', schema=None) as batch_op:
        batch_op.drop_constraint('fk_meth_snail_user_id', type_='foreignkey')
    
    with op.batch_alter_table('the_stick_memory_bank', schema=None) as batch_op:
        batch_op.drop_constraint('fk_the_stick_user_id', type_='foreignkey')
    
    with op.batch_alter_table('sir_hawkington_memory_bank', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sir_hawkington_user_id', type_='foreignkey')