"""add_performance_indexes

Revision ID: 3ea74a8cb1b5
Revises: perf_indexes_001
Create Date: 2025-10-20 12:26:17.829734
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ea74a8cb1b5'
down_revision: Union[str, None] = '5dea6e23a9b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === USER TABLE OPTIMIZATIONS ===
    # Email already has index, but add composite for common auth queries
    op.create_index('idx_users_email_active', 'users', ['email', 'is_active'], unique=False)
    op.create_index('idx_users_last_login', 'users', ['last_login'], unique=False)
    op.create_index('idx_users_created_at', 'users', ['created_at'], unique=False)
    
    # === SYSTEM METRICS OPTIMIZATIONS ===
    op.create_index('idx_system_metrics_user_timestamp', 'system_metrics', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_system_metrics_timestamp', 'system_metrics', ['timestamp'], unique=False)
    
    # === AGENT MEMORY OPTIMIZATIONS ===
    op.create_index('idx_agent_memories_user_timestamp', 'agent_memories', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_agent_memories_agent_user', 'agent_memories', ['agent_name', 'user_id'], unique=False)
    op.create_index('idx_agent_memories_timestamp', 'agent_memories', ['timestamp'], unique=False)
    
    # === CENTRAL MEMORY BANK OPTIMIZATIONS ===
    # Note: central_memory_bank uses 'occurred_at' not 'timestamp'
    op.create_index('idx_central_memory_user_occurred', 'central_memory_bank', ['user_id', 'occurred_at'], unique=False)
    op.create_index('idx_central_memory_occurred', 'central_memory_bank', ['occurred_at'], unique=False)
    
    # === AGENT-SPECIFIC MEMORY BANKS ===
    # Sir Hawkington
    op.create_index('idx_sir_hawkington_user_timestamp', 'sir_hawkington_memory_bank', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_sir_hawkington_timestamp', 'sir_hawkington_memory_bank', ['timestamp'], unique=False)
    
    # The Stick
    op.create_index('idx_the_stick_user_timestamp', 'the_stick_memory_bank', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_the_stick_timestamp', 'the_stick_memory_bank', ['timestamp'], unique=False)
    
    # Meth Snail
    op.create_index('idx_meth_snail_user_timestamp', 'meth_snail_memory_bank', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_meth_snail_timestamp', 'meth_snail_memory_bank', ['timestamp'], unique=False)
    
    # Hamsters
    op.create_index('idx_hamsters_user_timestamp', 'hamsters_memory_bank', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_hamsters_timestamp', 'hamsters_memory_bank', ['timestamp'], unique=False)
    
    # Quantum Shadow People
    op.create_index('idx_quantum_sp_user_timestamp', 'quantum_shadow_people_memory_bank', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_quantum_sp_timestamp', 'quantum_shadow_people_memory_bank', ['timestamp'], unique=False)
    
    # VIC-20
    op.create_index('idx_vic20_user_timestamp', 'vic20_memory_bank', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_vic20_timestamp', 'vic20_memory_bank', ['timestamp'], unique=False)
    
    # === AGENT LEARNING OPTIMIZATIONS ===
    op.create_index('idx_agent_learning_user_timestamp', 'agent_learning_interactions', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_user_learning_user_timestamp', 'user_learning_patterns', ['user_id', 'timestamp'], unique=False)
    
    # === AGENT EVENT LOG OPTIMIZATIONS ===
    op.create_index('idx_agent_event_log_user_timestamp', 'agent_event_log', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_agent_event_log_agent_user', 'agent_event_log', ['agent_name', 'user_id'], unique=False)
    op.create_index('idx_agent_event_log_timestamp', 'agent_event_log', ['timestamp'], unique=False)
    
    # === METRICS AGGREGATION OPTIMIZATIONS ===
    # Note: These tables already have indexes on user_id+hour_start and user_id+date
    # but we're adding explicit ones for consistency
    # metrics_hourly already has idx_user_hour, skip duplicate
    # metrics_daily already has idx_user_date, skip duplicate


def downgrade() -> None:
    # Drop all indexes in reverse order
    # Skipped metrics_hourly and metrics_daily - they already have their own indexes
    
    op.drop_index('idx_agent_event_log_timestamp', table_name='agent_event_log')
    op.drop_index('idx_agent_event_log_agent_user', table_name='agent_event_log')
    op.drop_index('idx_agent_event_log_user_timestamp', table_name='agent_event_log')
    
    op.drop_index('idx_user_learning_user_timestamp', table_name='user_learning_patterns')
    op.drop_index('idx_agent_learning_user_timestamp', table_name='agent_learning_interactions')
    
    op.drop_index('idx_vic20_timestamp', table_name='vic20_memory_bank')
    op.drop_index('idx_vic20_user_timestamp', table_name='vic20_memory_bank')
    
    op.drop_index('idx_quantum_sp_timestamp', table_name='quantum_shadow_people_memory_bank')
    op.drop_index('idx_quantum_sp_user_timestamp', table_name='quantum_shadow_people_memory_bank')
    
    op.drop_index('idx_hamsters_timestamp', table_name='hamsters_memory_bank')
    op.drop_index('idx_hamsters_user_timestamp', table_name='hamsters_memory_bank')
    
    op.drop_index('idx_meth_snail_timestamp', table_name='meth_snail_memory_bank')
    op.drop_index('idx_meth_snail_user_timestamp', table_name='meth_snail_memory_bank')
    
    op.drop_index('idx_the_stick_timestamp', table_name='the_stick_memory_bank')
    op.drop_index('idx_the_stick_user_timestamp', table_name='the_stick_memory_bank')
    
    op.drop_index('idx_sir_hawkington_timestamp', table_name='sir_hawkington_memory_bank')
    op.drop_index('idx_sir_hawkington_user_timestamp', table_name='sir_hawkington_memory_bank')
    
    op.drop_index('idx_central_memory_occurred', table_name='central_memory_bank')
    op.drop_index('idx_central_memory_user_occurred', table_name='central_memory_bank')
    
    op.drop_index('idx_agent_memories_timestamp', table_name='agent_memories')
    op.drop_index('idx_agent_memories_agent_user', table_name='agent_memories')
    op.drop_index('idx_agent_memories_user_timestamp', table_name='agent_memories')
    
    op.drop_index('idx_system_metrics_timestamp', table_name='system_metrics')
    op.drop_index('idx_system_metrics_user_timestamp', table_name='system_metrics')
    
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_last_login', table_name='users')
    op.drop_index('idx_users_email_active', table_name='users')
