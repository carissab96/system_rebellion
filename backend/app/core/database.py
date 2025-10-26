from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine
from app.core.base import Base
import os
from dotenv import load_dotenv

# Load environment variables FIRST
env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env.development')
if os.path.exists(env_file):
    load_dotenv(env_file, override=True)
    print(f"✅ [database.py] Loaded environment from: {env_file}")

# Database URLs - PostgreSQL
ASYNC_DATABASE_URL = os.getenv("DB_URL") or os.getenv("DATABASE_URL", "postgresql+asyncpg://carissa@localhost:5432/system_rebellion")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", "postgresql://carissa@localhost:5432/system_rebellion")

print(f"🔗 [database.py] Using database: {ASYNC_DATABASE_URL[:50]}...")

# Create engines with optimized connection pooling for PostgreSQL
async_engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=False,  # Disable verbose logging for performance
    future=True,
    pool_pre_ping=True,  # Ensure connections are valid
    pool_size=20,  # Increased from default 5
    max_overflow=40,  # Allow up to 60 total connections
    pool_timeout=5,  # Fail fast if pool exhausted
    pool_recycle=3600  # Recycle connections after 1 hour
)
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,  # Disable verbose logging for performance
    future=True,
    pool_pre_ping=True,  # Ensure connections are valid
    pool_size=20,
    max_overflow=40,
    pool_timeout=5,
    pool_recycle=3600
)
# Async session
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Sync session - now properly bound to the sync engine
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False, 
    autoflush=False
)
def log_registered_models():
    """
    Sir Hawkington's Model Inspection Protocol
    The Meth Snail's paranoid sketched-out ass watches ALL!
    """
    print("REGISTERED MODELS")
    print("\n")
    for table_name in Base.metadata.tables.keys():
        print(f"The snail Found Model: {table_name}")
    print("\n")
#Model Creation Funciton
async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log_registered_models()
    print("Models initialized successfully.")

# Async database getter
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
async def get_async_session():
    async with async_engine.connect() as conn:
        yield conn

# Sync database getter
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_url() -> str:
    url = (
        os.getenv("DB_URL")
        or os.getenv("DATABASE_URL")
        or "postgresql+asyncpg://rebellion_user:ChangeThisPassword123!@localhost:5432/system_rebellion"
    )
    return url
    
# For backwards compatibility, make get_db the default
# This allows existing code to work without changes
get_db_dependency = get_db
