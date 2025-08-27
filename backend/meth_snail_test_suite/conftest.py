# conftest.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from app.ai_agents.meth_snail.decision_engine import MethSnailBrainV2
from app.ai_agents.meth_snail.database_integration import MethSnailDatabaseIntegration
from app.ai_agents.meth_snail.websocket_handler import MethSnailWebSocketHandler
from app.models.agent_memory_banks import CentralMemoryBank

@pytest_asyncio.fixture
async def mock_async_session():
    """Mock async database session for testing"""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    
    # Mock context manager behavior
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    
    return session

@pytest_asyncio.fixture
async def mock_session_factory(mock_session):
    """Mock session factory for database operations"""
    factory = AsyncMock()
    factory.return_value = mock_session
    return factory

@pytest_asyncio.fixture
async def mock_session():
    """Mock async database session for testing"""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    
    # Mock context manager behavior
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    
    return session

@pytest_asyncio.fixture
async def central_memory_bank(mock_session_factory):
    """Central memory bank for cross-agent learning"""
    memory_bank = AsyncMock(spec=CentralMemoryBank)
    
    # Mock the key methods
    memory_bank.store_entry = AsyncMock()
    memory_bank.get_entries_by_agent = AsyncMock(return_value=[])
    memory_bank.get_entries_by_type = AsyncMock(return_value=[])
    memory_bank.get_cross_agent_insights = AsyncMock(return_value=[])
    memory_bank.update_entry = AsyncMock()
    memory_bank.get_performance_metrics = AsyncMock(return_value={
        'avg_response_time': 120.5,
        'success_rate': 0.95,
        'total_decisions': 1250
    })
    
    return memory_bank

@pytest_asyncio.fixture
async def db_integration(mock_session_factory, central_memory_bank):
    """Meth Snail database integration component"""
    db_int = MethSnailDatabaseIntegration(
        session_factory=mock_session_factory,
        central_memory_bank=central_memory_bank
    )
    return db_int

@pytest_asyncio.fixture
async def websocket_manager():
    """Mock WebSocket manager for real-time updates"""
    manager = AsyncMock()
    manager.broadcast = AsyncMock()
    manager.send_to_agent = AsyncMock()
    manager.send_jitter_update = AsyncMock()
    manager.is_connected = MagicMock(return_value=True)
    return manager

@pytest_asyncio.fixture
async def websocket_manager():
    """Meth Snail WebSocket handler"""
    manager = MethSnailWebSocketHandler(
        agent_id="meth_snail"
    )
    return manager

@pytest_asyncio.fixture
async def decision_engine(db_integration, websocket_manager):
    """Fully configured Meth Snail decision engine"""
    engine = MethSnailBrainV2(
        db_integration=db_integration,
        websocket_handler=websocket_manager,
        caffeine_threshold=75,
        jitter_limit=90,
        shell_spin_threshold=3
    )
    
    # Initialize with safe levels
    engine._current_caffeine = 50
    engine._current_jitter = 25
    engine._shell_spin_count = 0
    
    return engine

@pytest_asyncio.fixture
async def sample_metrics():
    """Sample system metrics for testing"""
    return {
        "memory_usage": 68.5,
        "cpu_usage": 45.2,
        "response_time": 125.7,
        "error_rate": 0.015,
        "disk_usage": 72.1,
        "network_latency": 23.4,
        "active_connections": 1250,
        "cache_hit_ratio": 0.87,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@pytest_asyncio.fixture
async def historical_data():
    """Historical performance data for thorough analysis"""
    base_time = datetime.now(timezone.utc) - timedelta(hours=24)
    
    return [
        AgentMemoryEntry(
            id=i,
            agent_id="meth_snail",
            entry_type="performance_metric",
            data={
                "memory_usage": 60 + (i % 30),
                "cpu_usage": 40 + (i % 25),
                "response_time": 100 + (i % 50),
                "timestamp": (base_time + timedelta(minutes=i*10)).isoformat()
            },
            timestamp=base_time + timedelta(minutes=i*10),
            importance_score=0.7 + (i % 3) * 0.1
        )
        for i in range(144)  # 24 hours of 10-minute intervals
    ]