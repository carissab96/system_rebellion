from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine
from contextlib import asynccontextmanager
from app.core.base import Base
import os
from dotenv import load_dotenv

# Load environment variables FIRST
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_project_dir = os.path.dirname(_backend_dir)
env_file = None
for candidate in [
    os.path.join(_project_dir, '.env'),
    os.path.join(_backend_dir, '.env'),
    os.path.join(_project_dir, '.env.development'),
    os.path.join(_backend_dir, '.env.development'),
]:
    if os.path.exists(candidate):
        env_file = candidate
        break
if env_file:
    load_dotenv(env_file, override=True)
    print(f"✅ [database.py] Loaded environment from: {env_file}")

# Database URLs - PostgreSQL
ASYNC_DATABASE_URL = os.getenv("DB_URL") or os.getenv("DATABASE_URL", "postgresql+asyncpg://carissab@localhost:5432/system_rebellion")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", "postgresql://carissab@localhost:5432/system_rebellion")

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

# Dedicated auth engine with reserved connections for critical auth operations
auth_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=5,  # Small dedicated pool for auth only
    max_overflow=5,  # Allow up to 10 total auth connections
    pool_timeout=2,  # Fast timeout for auth
    pool_recycle=3600
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

# Dedicated auth session maker
AuthSessionLocal = sessionmaker(
    auth_engine,
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

# Async database getter (generator pattern - use for FastAPI dependencies)
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def get_managed_session():
    """
    Get a properly managed database session for use in background tasks.
    
    Unlike get_async_db() which is an async generator, this context manager
    ensures proper session lifecycle even when used in asyncio.create_task()
    or fire-and-forget contexts.
    
    Usage:
        async with get_managed_session() as session:
            session.add(...)
            await session.commit()
    
    This prevents the IllegalStateChangeError that occurs when async generators
    are garbage collected before completing in background tasks.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# Dedicated auth database getter with priority connection pool
async def get_auth_db():
    """Priority database connection for authentication - bypasses agent contention"""
    async with AuthSessionLocal() as session:
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
        or "postgresql+asyncpg://carissab:Garfield7734@localhost:5432/system_rebellion"
    )
    return url
    
# For backwards compatibility, make get_db the default
# This allows existing code to work without changes
get_db_dependency = get_db
