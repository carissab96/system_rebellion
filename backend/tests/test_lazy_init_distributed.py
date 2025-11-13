"""
Test Lazy Initialization with Distributed Agents
================================================

Verify that lazy initialization works correctly with distributed agents.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.lazy_init import initialize_agents_and_websockets, is_initialized


class MockDistributedAgent:
    """Mock distributed agent"""
    
    def __init__(self, name):
        self.name = name
        self.is_active = True
        self.initialized_distributed = False
    
    async def initialize_distributed(self, redis_client):
        self.initialized_distributed = True
    
    async def process_metrics(self, metrics, user_context=None):
        return {"status": "ok"}
    
    async def health_check(self):
        return {"status": "healthy"}


class MockAgentManager:
    """Mock agent manager"""
    
    def __init__(self):
        self.initialized = True
        self.agents = {
            "sir_hawkington": MockDistributedAgent("sir_hawkington"),
            "meth_snail": MockDistributedAgent("meth_snail"),
            "hamsters": MockDistributedAgent("hamsters")
        }


class TestLazyInitDistributed:
    """Test lazy initialization with distributed agents"""
    
    @pytest.mark.asyncio
    async def test_lazy_init_counts_distributed_agents(self):
        """Test that lazy init counts and logs distributed agents"""
        
        # Reset initialization state
        import app.core.lazy_init as lazy_init_module
        lazy_init_module._initialized = False
        lazy_init_module._initialization_task = None
        
        # Mock app state
        app_state = Mock()
        app_state.background_tasks = []
        
        # Mock all the imports and functions (they're imported inside the function)
        with patch('app.api.websockets.get_websocket_manager') as mock_ws_manager, \
             patch('app.ai_agents.agent_manager.get_agent_manager') as mock_get_agent_manager, \
             patch('app.core.background_tasks.start_all_background_tasks') as mock_bg_tasks, \
             patch('app.core.learning_helpers.run_metadata_scheduler') as mock_metadata, \
             patch('app.core.database.AsyncSessionLocal') as mock_session:
            
            # Setup mocks
            mock_ws = AsyncMock()
            mock_ws.start = AsyncMock()
            mock_ws_manager.return_value = mock_ws
            
            mock_agent_manager = MockAgentManager()
            mock_get_agent_manager.return_value = mock_agent_manager
            
            mock_bg_tasks.return_value = []
            
            # Run lazy initialization
            result = await initialize_agents_and_websockets(app_state)
            
            # Verify initialization happened
            assert result is True
            assert is_initialized() is True
            
            # Verify agent manager was called
            mock_get_agent_manager.assert_called_once()
            
            # Verify WebSocket manager was started
            mock_ws.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_lazy_init_idempotent(self):
        """Test that lazy init can be called multiple times safely"""
        
        # Reset initialization state
        import app.core.lazy_init as lazy_init_module
        lazy_init_module._initialized = False
        lazy_init_module._initialization_task = None
        
        # Mock app state
        app_state = Mock()
        app_state.background_tasks = []
        
        # Mock all the imports and functions (they're imported inside the function)
        with patch('app.api.websockets.get_websocket_manager') as mock_ws_manager, \
             patch('app.ai_agents.agent_manager.get_agent_manager') as mock_get_agent_manager, \
             patch('app.core.background_tasks.start_all_background_tasks') as mock_bg_tasks, \
             patch('app.core.learning_helpers.run_metadata_scheduler') as mock_metadata, \
             patch('app.core.database.AsyncSessionLocal') as mock_session:
            
            # Setup mocks
            mock_ws = AsyncMock()
            mock_ws.start = AsyncMock()
            mock_ws_manager.return_value = mock_ws
            
            mock_agent_manager = MockAgentManager()
            mock_get_agent_manager.return_value = mock_agent_manager
            
            mock_bg_tasks.return_value = []
            
            # First call should initialize
            result1 = await initialize_agents_and_websockets(app_state)
            assert result1 is True
            
            # Second call should skip
            result2 = await initialize_agents_and_websockets(app_state)
            assert result2 is False
            
            # Agent manager should only be called once
            assert mock_get_agent_manager.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
