import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import all your models so alembic can see them
# from app.models import user
# from models.qsp_models import QSPNetworkMetrics, QSPDecisionLog, QSPQuantumStats, QSPNetworkPatterns
# from models.sir_hawkington_models import HawkingtonDecisionLog, HawkingtonMonitoringStats
# from models.meth_snail_models import MethSnailDecisionLog, MethSnailOptimizationStats
# from models.hamsters_models import HamstersDecisionLog, HamstersEngineeringStats
# from models.agent_coordination_models import AgentPerformanceSummary, CrossAgentCoordination

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to use your imported models
from app.models.user import Base
target_metadata = Base.metadata

# Set DATABASE_URL from environment if set, else default to sqlite
database_url = os.getenv('DATABASE_URL', 'sqlite:///./system_rebellion.db')
config.set_main_option('sqlalchemy.url', database_url)

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():  # ← FIXED: singular, not plural
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        
        with context.begin_transaction():  # ← FIXED: singular, not plural
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()