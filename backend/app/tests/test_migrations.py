from alembic.config import Config
from alembic import command
import os

def run_migrations(engine):
    """Run Alembic migrations against the given engine."""
    # Get the absolute path to the alembic directory
    alembic_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'alembic')
    
    # Create a temporary alembic configuration
    config = Config()
    config.set_main_option("script_location", alembic_dir)
    
    # Set the database URL
    config.set_main_option("sqlalchemy.url", engine.url.render_as_string(hide_password=False))
    
    # Run the upgrade command
    command.upgrade(config, "head")
