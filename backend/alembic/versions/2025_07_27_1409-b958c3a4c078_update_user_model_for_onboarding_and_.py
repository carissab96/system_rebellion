"""Update user model for onboarding and system profile

Revision ID: b958c3a4c078
Revises: f717dcc399f9
Create Date: 2025-07-27 14:09:52.467396
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import json

# revision identifiers, used by Alembic.
revision: str = 'b958c3a4c078'
down_revision: Union[str, None] = 'f717dcc399f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add columns one by one for SQLite compatibility
    # Note: SQLite doesn't support adding multiple columns in one ALTER statement
    
    # Add onboarding_completed
    try:
        op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=True))
    except:
        pass  # Column might already exist
    
    # Add onboarding_progress
    try:
        op.add_column('users', sa.Column('onboarding_progress', sa.Integer(), nullable=True))
    except:
        pass
    
    # Add system_profile as TEXT (JSON string) for SQLite
    try:
        op.add_column('users', sa.Column('system_profile', sa.Text(), nullable=True))
    except:
        pass
    
    # Add agent_preferences as TEXT (JSON string) for SQLite
    try:
        op.add_column('users', sa.Column('agent_preferences', sa.Text(), nullable=True))
    except:
        pass
    
    # Add monitoring_thresholds as TEXT (JSON string) for SQLite
    try:
        op.add_column('users', sa.Column('monitoring_thresholds', sa.Text(), nullable=True))
    except:
        pass
    
    # Add permissions_status as TEXT (JSON string) for SQLite
    try:
        op.add_column('users', sa.Column('permissions_status', sa.Text(), nullable=True))
    except:
        pass
    
    # Add installation_method
    try:
        op.add_column('users', sa.Column('installation_method', sa.String(50), nullable=True))
    except:
        pass
    
    # Set default values for existing users
    # For SQLite, we need to use JSON strings
    default_system_profile = json.dumps({
        "os_type": None,
        "os_version": None,
        "total_ram_gb": None,
        "storage_type": None,
        "total_storage_gb": None,
        "cpu_cores": None,
        "is_virtual": False,
        "network_type": "standard",
        "admin_access": "full",
        "mdm_controlled": False,
        "custom_restrictions": []
    })
    
    default_agent_preferences = json.dumps({
        "sir_hawkington": {"enabled": True, "aggression_level": 5},
        "the_stick": {"enabled": True, "anxiety_threshold": 7},
        "hamsters": {"enabled": True, "beer_allocation": "moderate"},
        "meth_snail": {"enabled": True, "speed_mode": "chaotic"},
        "quantum_shadow_people": {"enabled": True, "phase_frequency": "standard"},
        "vic_20": {"enabled": True, "wisdom_mode": "cryptic"}
    })
    
    default_monitoring_thresholds = json.dumps({
        "cpu_alert": 80,
        "memory_alert": 85,
        "disk_alert": 90,
        "network_alert": 75,
        "custom_alerts": []
    })
    
    default_permissions_status = json.dumps({
        "install_complete": False,
        "admin_access": False,
        "monitoring_enabled": False,
        "network_access": True,
        "storage_access": True
    })
    
    # Update existing records with defaults
    op.execute(f"""
        UPDATE users 
        SET system_profile = '{default_system_profile}'
        WHERE system_profile IS NULL
    """)
    
    op.execute(f"""
        UPDATE users 
        SET agent_preferences = '{default_agent_preferences}'
        WHERE agent_preferences IS NULL
    """)
    
    op.execute(f"""
        UPDATE users 
        SET monitoring_thresholds = '{default_monitoring_thresholds}'
        WHERE monitoring_thresholds IS NULL
    """)
    
    op.execute(f"""
        UPDATE users 
        SET permissions_status = '{default_permissions_status}'
        WHERE permissions_status IS NULL
    """)
    
    op.execute("""
        UPDATE users 
        SET onboarding_completed = 0 
        WHERE onboarding_completed IS NULL
    """)
    
    op.execute("""
        UPDATE users 
        SET onboarding_progress = 0 
        WHERE onboarding_progress IS NULL
    """)

def downgrade():
    # Remove columns
    op.drop_column('users', 'installation_method')
    op.drop_column('users', 'permissions_status')
    op.drop_column('users', 'monitoring_thresholds')
    op.drop_column('users', 'agent_preferences')
    op.drop_column('users', 'system_profile')
    op.drop_column('users', 'onboarding_progress')
    op.drop_column('users', 'onboarding_completed')