"""
Initial migration for System Rebellion (squashed).
"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.sqlite as sqlite

# Alembic revision identifiers
revision = '2025_05_19_2110'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('username', sa.VARCHAR(length=50), nullable=False),
        sa.Column('email', sa.VARCHAR(length=100), nullable=False),
        sa.Column('hashed_password', sa.VARCHAR(length=255), nullable=False),
        sa.Column('needs_onboarding', sa.BOOLEAN(), nullable=True),
        sa.Column('first_name', sa.VARCHAR(length=50), nullable=True),
        sa.Column('last_name', sa.VARCHAR(length=50), nullable=True),
        sa.Column('bio', sa.TEXT(), nullable=True),
        sa.Column('profile_picture', sa.VARCHAR(length=255), nullable=True),
        sa.Column('operating_system', sa.VARCHAR(length=50), nullable=True),
        sa.Column('os_version', sa.VARCHAR(length=50), nullable=True),
        sa.Column('linux_distro', sa.VARCHAR(length=50), nullable=True),
        sa.Column('linux_distro_version', sa.VARCHAR(length=50), nullable=True),
        sa.Column('cpu_cores', sa.INTEGER(), nullable=True),
        sa.Column('total_memory', sa.INTEGER(), nullable=True),
        sa.Column('avatar', sa.VARCHAR(length=50), nullable=True),
        sa.Column('preferences', sqlite.JSON(), nullable=True),
        sa.Column('is_active', sa.BOOLEAN(), nullable=True),
        sa.Column('is_superuser', sa.BOOLEAN(), nullable=True),
        sa.Column('is_verified', sa.BOOLEAN(), nullable=True),
        sa.Column('last_login', sa.DATETIME(), nullable=True),
        sa.Column('failed_login_attempts', sa.INTEGER(), nullable=True),
        sa.Column('lockout_until', sa.DATETIME(), nullable=True),
        sa.Column('created_at', sa.DATETIME(), nullable=True),
        sa.Column('updated_at', sa.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.create_table('tuning_history',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('user_id', sa.INTEGER(), nullable=False),
        sa.Column('parameter', sa.VARCHAR(), nullable=False),
        sa.Column('old_value', sa.VARCHAR(), nullable=True),
        sa.Column('new_value', sa.VARCHAR(), nullable=False),
        sa.Column('success', sa.BOOLEAN(), nullable=True),
        sa.Column('error', sa.VARCHAR(), nullable=True),
        sa.Column('metrics_before', sqlite.JSON(), nullable=True),
        sa.Column('metrics_after', sqlite.JSON(), nullable=True),
        sa.Column('timestamp', sa.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tuning_history_id', 'tuning_history', ['id'], unique=False)
    op.create_table('system_configurations',
        sa.Column('id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('user_id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('config_type', sa.VARCHAR(length=11), nullable=False),
        sa.Column('settings', sqlite.JSON(), nullable=False),
        sa.Column('is_active', sa.BOOLEAN(), nullable=True),
        sa.Column('created_at', sa.DATETIME(), nullable=True),
        sa.Column('updated_at', sa.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_profiles',
        sa.Column('id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('user_id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('location', sa.VARCHAR(length=100), nullable=True),
        sa.Column('website', sa.VARCHAR(length=200), nullable=True),
        sa.Column('github_username', sa.VARCHAR(length=50), nullable=True),
        sa.Column('linkedin_profile', sa.VARCHAR(length=200), nullable=True),
        sa.Column('theme_preference', sa.VARCHAR(length=20), nullable=True),
        sa.Column('notification_settings', sa.VARCHAR(length=100), nullable=True),
        sa.Column('optimization_level', sa.VARCHAR(length=50), nullable=True),
        sa.Column('created_at', sa.DATETIME(), nullable=True),
        sa.Column('updated_at', sa.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('system_metrics',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('timestamp', sa.DATETIME(), nullable=True),
        sa.Column('cpu_usage', sa.FLOAT(), nullable=True),
        sa.Column('memory_usage', sa.FLOAT(), nullable=True),
        sa.Column('disk_usage', sa.FLOAT(), nullable=True),
        sa.Column('network_usage', sqlite.JSON(), nullable=True),
        sa.Column('process_count', sa.INTEGER(), nullable=True),
        sa.Column('additional_metrics', sqlite.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_system_metrics_id', 'system_metrics', ['id'], unique=False)
    op.create_table('optimization_profiles',
        sa.Column('id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('user_id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('settings', sqlite.JSON(), nullable=False),
        sa.Column('is_active', sa.BOOLEAN(), nullable=True),
        sa.Column('created_at', sa.DATETIME(), nullable=True),
        sa.Column('updated_at', sa.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('system_alerts',
        sa.Column('id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('user_id', sa.VARCHAR(length=36), nullable=False),
        sa.Column('title', sa.VARCHAR(length=100), nullable=False),
        sa.Column('message', sa.TEXT(), nullable=False),
        sa.Column('severity', sa.VARCHAR(length=8), nullable=True),
        sa.Column('timestamp', sa.DATETIME(), nullable=True),
        sa.Column('is_read', sa.BOOLEAN(), nullable=True),
        sa.Column('additional_data', sqlite.JSON(), nullable=True),
        sa.Column('created_at', sa.DATETIME(), nullable=True),
        sa.Column('updated_at', sa.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('system_alerts')
    op.drop_table('optimization_profiles')
    op.drop_index('ix_system_metrics_id', table_name='system_metrics')
    op.drop_table('system_metrics')
    op.drop_table('user_profiles')
    op.drop_table('system_configurations')
    op.drop_index('ix_tuning_history_id', table_name='tuning_history')
    op.drop_table('tuning_history')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
