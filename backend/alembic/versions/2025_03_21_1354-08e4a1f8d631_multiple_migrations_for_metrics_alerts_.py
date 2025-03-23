"""multiple migrations for metrics,alerts and system configurations

Revision ID: 08e4a1f8d631
Revises: 74504bba0ad0
Create Date: 2025-03-21 13:54:06.605091
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08e4a1f8d631'
down_revision: Union[str, None] = '74504bba0ad0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tables with quantum-level relationships"""
    
    # System Configurations Table
    op.create_table('system_configurations',
    sa.Column('id', sa.String(36), primary_key=True),
    sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
    sa.Column('config_key', sa.String(100), nullable=False),
    sa.Column('config_value', sa.JSON, nullable=True),
    sa.Column('is_active', sa.Boolean(), default=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

    # System Metrics Table
    op.create_table('system_metrics',
    sa.Column('id', sa.String(36), primary_key=True),
    sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('cpu_usage', sa.Float(), nullable=True),
    sa.Column('memory_usage', sa.Float(), nullable=True),
    sa.Column('disk_usage', sa.Float(), nullable=True),
    sa.Column('network_usage', sa.Float(), nullable=True),
    sa.Column('process_count', sa.Integer(), nullable=True),
    sa.Column('configuration_id', sa.String(36), sa.ForeignKey('system_configurations.id'), nullable=True),
    sa.Column('additional_metrics', sa.JSON, nullable=True)
    )

    # System Alerts Table
    op.create_table('system_alerts',
    sa.Column('id', sa.String(36), primary_key=True),
    sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('metric_type', sa.String(50), nullable=True),
    sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='alert_severity'), nullable=False),
    sa.Column('message', sa.String(255), nullable=False),
    sa.Column('metric_id', sa.String(36), sa.ForeignKey('system_metrics.id'), nullable=True),
    sa.Column('configuration_id', sa.String(36), sa.ForeignKey('system_configurations.id'), nullable=True),
    sa.Column('is_resolved', sa.Boolean(), default=False),
    sa.Column('resolved_at', sa.DateTime(), nullable=True),
    sa.Column('additional_data', sa.JSON, nullable=True)
    )

def downgrade() -> None:
    """Quantum Shadow People Removal Protocol"""
    op.drop_table('system_alerts')
    op.drop_table('system_metrics')
    op.drop_table('system_configurations')