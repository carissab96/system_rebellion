"""
Base Database Integration for All Agents
Enforces consistent db_getter pattern and DUAL-WRITE architecture
"""

import logging
from typing import Optional, AsyncGenerator, Dict, Any
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)


class BaseDatabaseIntegration(ABC):
    """
    Base class for all agent database integrations.
    Enforces consistent patterns:
    - Use db_getter for session management (NO self.session!)
    - DUAL-WRITE: agent table + central_memory_bank
    - Proper error handling and logging
    """
    
    def __init__(self, db_getter=None):
        """
        Initialize database integration with shared connection pool.
        
        Args:
            db_getter: Async generator function that yields database sessions
                      Example: async for session in db_getter(): ...
        """
        self.db_getter = db_getter
        self._initialized = False
        self.agent_name = self._get_agent_name()
        self.logger = logging.getLogger(f"{self.agent_name}.Database")
    
    @abstractmethod
    def _get_agent_name(self) -> str:
        """Return the agent's name (e.g., 'the_stick', 'vic20_sage')"""
        pass
    
    async def initialize(self):
        """Initialize and verify database connection"""
        if not self.db_getter:
            raise ValueError(f"{self.agent_name}: db_getter is required!")
        
        # Verify db_getter works by testing a connection
        try:
            async for session in self.db_getter():
                # Just verify we can get a session
                break
            self._initialized = True
            self.logger.info(f"✅ {self.agent_name} database integration initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to verify database connection: {e}")
            raise
    
    async def ensure_initialized(self):
        """Ensure database is initialized before operations"""
        if not self._initialized:
            await self.initialize()
    
    def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session using the db_getter pattern.
        
        Usage:
            async for session in self.get_session():
                # Do database operations
                session.add(...)
                await session.commit()
                break  # Important: only use first session
        
        Returns:
            AsyncGenerator that yields database sessions
        """
        if not self.db_getter:
            raise ValueError(f"{self.agent_name}: db_getter not configured!")
        return self.db_getter()
    
    @asynccontextmanager
    async def get_managed_session(self):
        """
        Get a properly managed database session that works in fire-and-forget tasks.
        
        Unlike get_session() which uses an async generator, this context manager
        ensures proper session lifecycle even when used in asyncio.create_task().
        
        Usage:
            async with self.get_managed_session() as session:
                session.add(...)
                await session.commit()
        
        This prevents the IllegalStateChangeError that occurs when async generators
        are garbage collected before completing in background tasks.
        """
        if not self.db_getter:
            raise ValueError(f"{self.agent_name}: db_getter not configured!")
        
        # Import here to avoid circular imports
        from app.core.database import AsyncSessionLocal
        
        session = AsyncSessionLocal()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async for session in self.get_session():
                from sqlalchemy import text
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                return True
        except Exception as e:
            self.logger.error(f"❌ Database health check failed: {e}")
            return False
    
    @abstractmethod
    async def store_decision(self, user_id: str, decision: Any) -> str:
        """
        Store agent decision using DUAL-WRITE pattern.
        
        MUST implement:
        1. Write structured data to agent-specific table
        2. Write summary to central_memory_bank
        3. Return central_memory_id
        
        Args:
            user_id: User identifier
            decision: Agent-specific decision dataclass
            
        Returns:
            central_memory_id
            
        Raises:
            ValueError: If required data is missing
            Exception: If database write fails
        """
        pass
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list):
        """
        Validate that required fields are present and not None.
        
        Args:
            data: Dictionary of field values
            required_fields: List of field names that must be present
            
        Raises:
            ValueError: If any required field is missing or None
        """
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(
                    f"💥 {self.agent_name}: Missing required field '{field}' - "
                    f"cannot store without real data"
                )
    
    async def log_dual_write_success(
        self, 
        operation: str, 
        agent_memory_id: str, 
        central_memory_id: str
    ):
        """Log successful DUAL-WRITE operation"""
        self.logger.info(
            f"✨ DUAL-WRITE SUCCESS: {operation} stored in agent table "
            f"({agent_memory_id}) and CMB ({central_memory_id})"
        )
    
    async def log_dual_write_failure(
        self, 
        operation: str, 
        error: Exception
    ):
        """Log failed DUAL-WRITE operation"""
        self.logger.error(f"💥 DUAL-WRITE FAILED: {operation} - {str(error)}")
