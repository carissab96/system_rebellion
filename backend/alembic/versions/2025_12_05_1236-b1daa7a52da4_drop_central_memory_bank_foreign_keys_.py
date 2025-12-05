"""drop_central_memory_bank_foreign_keys constraints

Revision ID: b1daa7a52da4
Revises: 3734e17210c3
Create Date: 2025-12-05 12:36:23.369705
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1daa7a52da4'
down_revision: Union[str, None] = '3734e17210c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Drop foreign key constraints from agent memory banks to central_memory_bank.
    
    These FKs cause ordering issues during dual-writes - we want to be able to
    write to either table first without constraint violations.
    
    The central_memory_id column remains for reference, just without enforcement.
    """
    # Drop FK from sir_hawkington_memory_bank
    op.execute("""
        ALTER TABLE sir_hawkington_memory_bank 
        DROP CONSTRAINT IF EXISTS fk_sir_hawkington_memory_bank_central_memory_id_central_906c
    """)
    
    # Drop FK from meth_snail_memory_bank
    op.execute("""
        ALTER TABLE meth_snail_memory_bank 
        DROP CONSTRAINT IF EXISTS fk_meth_snail_memory_bank_central_memory_id_central_memor_5a3e
    """)
    
    # Drop FK from the_stick_memory_bank
    op.execute("""
        ALTER TABLE the_stick_memory_bank 
        DROP CONSTRAINT IF EXISTS fk_the_stick_memory_bank_central_memory_id_central_memory_b4d1
    """)
    
    # Drop FK from hamsters_memory_bank
    op.execute("""
        ALTER TABLE hamsters_memory_bank 
        DROP CONSTRAINT IF EXISTS fk_hamsters_memory_bank_central_memory_id_central_memory__0f8a
    """)
    
    # Drop FK from quantum_shadow_people_memory_bank
    op.execute("""
        ALTER TABLE quantum_shadow_people_memory_bank 
        DROP CONSTRAINT IF EXISTS fk_quantum_shadow_people_memory_bank_central_memory_id_ce_c7b2
    """)
    
    # Drop FK from vic20_memory_bank
    op.execute("""
        ALTER TABLE vic20_memory_bank 
        DROP CONSTRAINT IF EXISTS fk_vic20_memory_bank_central_memory_id_central_memory_ban_8f3d
    """)


def downgrade() -> None:
    """
    Re-add foreign key constraints (not recommended - causes write ordering issues).
    """
    # Re-add FK to sir_hawkington_memory_bank
    op.execute("""
        ALTER TABLE sir_hawkington_memory_bank 
        ADD CONSTRAINT fk_sir_hawkington_memory_bank_central_memory_id_central_906c
        FOREIGN KEY (central_memory_id) REFERENCES central_memory_bank(memory_id)
    """)
    
    # Re-add FK to meth_snail_memory_bank
    op.execute("""
        ALTER TABLE meth_snail_memory_bank 
        ADD CONSTRAINT fk_meth_snail_memory_bank_central_memory_id_central_memor_5a3e
        FOREIGN KEY (central_memory_id) REFERENCES central_memory_bank(memory_id)
    """)
    
    # Re-add FK to the_stick_memory_bank
    op.execute("""
        ALTER TABLE the_stick_memory_bank 
        ADD CONSTRAINT fk_the_stick_memory_bank_central_memory_id_central_memory_b4d1
        FOREIGN KEY (central_memory_id) REFERENCES central_memory_bank(memory_id)
    """)
    
    # Re-add FK to hamsters_memory_bank
    op.execute("""
        ALTER TABLE hamsters_memory_bank 
        ADD CONSTRAINT fk_hamsters_memory_bank_central_memory_id_central_memory__0f8a
        FOREIGN KEY (central_memory_id) REFERENCES central_memory_bank(memory_id)
    """)
    
    # Re-add FK to quantum_shadow_people_memory_bank
    op.execute("""
        ALTER TABLE quantum_shadow_people_memory_bank 
        ADD CONSTRAINT fk_quantum_shadow_people_memory_bank_central_memory_id_ce_c7b2
        FOREIGN KEY (central_memory_id) REFERENCES central_memory_bank(memory_id)
    """)
    
    # Re-add FK to vic20_memory_bank
    op.execute("""
        ALTER TABLE vic20_memory_bank 
        ADD CONSTRAINT fk_vic20_memory_bank_central_memory_id_central_memory_ban_8f3d
        FOREIGN KEY (central_memory_id) REFERENCES central_memory_bank(memory_id)
    """)
