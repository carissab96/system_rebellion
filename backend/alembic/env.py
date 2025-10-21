import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import all your models so alembic can see them
from app.models import user
from app.models import agent_memory_banks
from app.models import agent_events  # NEW: Three-tier event system
from app.models import metrics
from app.models import metrics_aggregates
from app.models import agent_memory


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to use your imported models
from app.core.base import Base
target_metadata = Base.metadata
print(f"DEBUG: Found {len(Base.metadata.tables)} tables in metadata:")
for table_name in sorted(Base.metadata.tables.keys()):
    print(f"  - {table_name}")
# Set DATABASE_URL from environment or use PostgreSQL default
from app.core.database import SYNC_DATABASE_URL
database_url = SYNC_DATABASE_URL
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