"""
Test Agent Manager with Distributed Agents
==========================================

Verify that the agent manager can initialize and shutdown
distributed agents correctly.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai_agents.agent_manager import AIAgentManager


@pytest.fixture
def mock_memory_service():
    """Mock memory service"""
    service = AsyncMock()
    service.ensure_ready = AsyncMock()
    return service


@pytest.fixture
def mock_db_getter():
    """Mock database getter"""
    return AsyncMock()


@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    redis = AsyncMock()
    redis.ping = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.publish = AsyncMock(return_value=1)
    redis.aclose = AsyncMock()
    return redis


class MockDistributedAgent:
    """Mock agent with distributed features"""
    
    def __init__(self):
        self.is_active = True
        self.initialized_distributed = False
        self.shutdown_distributed_called = False
    
    async def process_metrics(self, metrics, user_context=None):
        return {"status": "ok"}
    
    async def health_check(self):
        return {"status": "healthy"}
    
    async def initialize_distributed(self, redis_client):
        """Mock distributed initialization"""
        self.initialized_distributed = True
        self.redis_client = redis_client
    
    async def shutdown_distributed(self):
        """Mock distributed shutdown"""
        self.shutdown_distributed_called = True


class MockRegularAgent:
    """Mock agent without distributed features"""
    
    def __init__(self):
        self.is_active = True
    
    async def process_metrics(self, metrics, user_context=None):
        return {"status": "ok"}
    
    async def health_check(self):
        return {"status": "healthy"}


class TestAgentManagerDistributed:
    """Test agent manager with distributed agents"""
    
    @pytest.mark.asyncio
    async def test_initialize_distributed_features(
        self, mock_memory_service, mock_db_getter, mock_redis_client
    ):
        """Test that agent manager initializes distributed features"""
        
        # Create agent manager
        manager = AIAgentManager(
            memory_service=mock_memory_service,
            db_getter=mock_db_getter,
            redis_url="redis://localhost:6379"
        )
        
        # Mock agents - one distributed, one regular
        distributed_agent = MockDistributedAgent()
        regular_agent = MockRegularAgent()
        
        manager.agents = {
            "distributed_agent": distributed_agent,
            "regular_agent": regular_agent
        }
        
        # Mock Redis client creation
        with patch('redis.asyncio.from_url', return_value=mock_redis_client):
            # Initialize distributed features
            await manager._initialize_distributed_features()
        
        # Verify distributed agent was initialized
        assert distributed_agent.initialized_distributed is True
        assert hasattr(distributed_agent, 'redis_client')
        
        # Verify regular agent was not affected
        assert not hasattr(regular_agent, 'initialized_distributed')
    
    @pytest.mark.asyncio
    async def test_shutdown_distributed_features(
        self, mock_memory_service, mock_db_getter
    ):
        """Test that agent manager shuts down distributed features"""
        
        # Create agent manager
        manager = AIAgentManager(
            memory_service=mock_memory_service,
            db_getter=mock_db_getter,
            redis_url="redis://localhost:6379"
        )
        
        # Mock agents
        distributed_agent = MockDistributedAgent()
        distributed_agent.initialized_distributed = True
        regular_agent = MockRegularAgent()
        
        manager.agents = {
            "distributed_agent": distributed_agent,
            "regular_agent": regular_agent
        }
        
        # Shutdown distributed features
        await manager._shutdown_distributed_features()
        
        # Verify distributed agent was shut down
        assert distributed_agent.shutdown_distributed_called is True
    
    @pytest.mark.asyncio
    async def test_no_redis_url_skips_distributed(
        self, mock_memory_service, mock_db_getter
    ):
        """Test that missing Redis URL skips distributed initialization"""
        
        # Create agent manager without Redis URL
        manager = AIAgentManager(
            memory_service=mock_memory_service,
            db_getter=mock_db_getter,
            redis_url=None
        )
        
        # Mock agent
        distributed_agent = MockDistributedAgent()
        manager.agents = {"distributed_agent": distributed_agent}
        
        # Initialize distributed features (should skip)
        await manager._initialize_distributed_features()
        
        # Verify agent was NOT initialized with distributed features
        assert distributed_agent.initialized_distributed is False
    
    @pytest.mark.asyncio
    async def test_redis_connection_failure_graceful(
        self, mock_memory_service, mock_db_getter
    ):
        """Test that Redis connection failure doesn't crash initialization"""
        
        # Create agent manager
        manager = AIAgentManager(
            memory_service=mock_memory_service,
            db_getter=mock_db_getter,
            redis_url="redis://localhost:6379"
        )
        
        # Mock agent
        distributed_agent = MockDistributedAgent()
        manager.agents = {"distributed_agent": distributed_agent}
        
        # Mock Redis to fail connection
        mock_redis_fail = AsyncMock()
        mock_redis_fail.ping = AsyncMock(side_effect=Exception("Connection failed"))
        
        with patch('redis.asyncio.from_url', return_value=mock_redis_fail):
            # Should not raise exception
            await manager._initialize_distributed_features()
        
        # Verify agent was NOT initialized (graceful degradation)
        assert distributed_agent.initialized_distributed is False
    
    @pytest.mark.asyncio
    async def test_agent_distributed_init_failure_continues(
        self, mock_memory_service, mock_db_getter, mock_redis_client
    ):
        """Test that one agent's failure doesn't stop others"""
        
        # Create agent manager
        manager = AIAgentManager(
            memory_service=mock_memory_service,
            db_getter=mock_db_getter,
            redis_url="redis://localhost:6379"
        )
        
        # Create agents - one that will fail, one that will succeed
        class FailingAgent(MockDistributedAgent):
            async def initialize_distributed(self, redis_client):
                raise Exception("Initialization failed!")
        
        failing_agent = FailingAgent()
        success_agent = MockDistributedAgent()
        
        manager.agents = {
            "failing_agent": failing_agent,
            "success_agent": success_agent
        }
        
        with patch('redis.asyncio.from_url', return_value=mock_redis_client):
            # Should not raise exception
            await manager._initialize_distributed_features()
        
        # Verify successful agent was initialized
        assert success_agent.initialized_distributed is True
        
        # Verify failing agent was not initialized
        assert failing_agent.initialized_distributed is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
