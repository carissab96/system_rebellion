from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine
import os

# Base declarative model
Base = declarative_base()

# Database URLs
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./system_rebellion.db"
SYNC_DATABASE_URL = "sqlite:///./system_rebellion.db"

# Create engines
async_engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=True,  # Logging for debugging
    future=True
)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=True,  # Logging for debugging
    future=True
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

# Async database getter
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

# Sync database getter
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# For backwards compatibility, make get_db the default
# This allows existing code to work without changes
get_db_dependency = get_db

