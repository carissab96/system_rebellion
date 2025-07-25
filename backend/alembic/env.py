import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import all your models so alembic can see them
from app.models import user
from app.models import UserProfile
from app.models.system import SystemConfiguration
from app.models.system import OptimizationProfile
from app.models.alerts import SystemAlert
from app.models.metrics import SystemMetrics
from app.models.tuning_history import TuningHistory
from app.models.agent_coordination_models import CrossAgentCoordination
from app.models.agent_decision_models import HawkingtonDecisionLog, StickDecisionLog,MethSnailDecisionLog, HamstersDecisionLog, AgentPerformanceSummary
from app.models.ai_agent_tracking import AIAgentMetrics, MethSnailShellSpins, SirHawkingtonMonocleYeets, TheStickHyperventilations, QuantumShadowPhasings, VIC20Wisdom
from app.models.hamsters_model import  HamstersIndividualStats, HamstersInfrastructureIntervention, HamstersCommunicationLog, HamstersDuctTapeUsage, HamstersBeerConsumption, HamstersSupplyClosetRaid, HamstersEngineeringStats
from app.models.meth_snail_model import MethSnailOptimizationStats
from app.models.metrics_aggregates import MetricsHourly, MetricsDaily
from app.models.qsp_models import QSPNetworkMetrics, QSPDecisionLog, QSPQuantumStats, QSPNetworkPatterns
from app.models.sir_hawkington_model import HawkingtonMonitoringStats
from app.models.the_stick_model import StickUserPatterns, StickComplianceHistory, StickConfigurationProfiles, StickAnxietyLog, StickHamsterEncounters, StickPaperBagUsage, StickMemoryBank, StickSqueakTranslations, StickEmergencyProtocols
from app.models.vic20_sage_model import VIC20CoordinationLog, VIC20SystemSynthesis, VIC20AgentHarmony, VIC20AncientWisdom, VIC20PartnershipMetrics, VIC20DecisionOrchestration, VIC20AgentInteractionLog
from app.models.triage_decision_models import TriageDecisionLog, TriageStatistics


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
print(f"DEBUG: Found {len(Base.metadata.tables)} tables in metadata:")
for table_name in sorted(Base.metadata.tables.keys()):
    print(f"  - {table_name}")
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