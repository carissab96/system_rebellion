"""
Unit Tests for DistributedAgentMixin
====================================

Tests the consciousness injection mechanism without breaking existing functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

# Import the mixin
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai_agents.distributed.mixins import DistributedAgentMixin
from app.ai_agents.distributed.resource_monitor import ResourceType
from app.ai_agents.distributed.message_protocol import MessageType, Priority


class MockExistingAgent:
    """Mock existing agent to test mixin doesn't break functionality"""
    
    def __init__(self):
        self.agent_name = "test_agent"
        self.existing_functionality_works = True
        self.process_count = 0
    
    async def existing_method(self):
        """Simulate existing agent method"""
        self.process_count += 1
        return {"status": "existing_works"}


class TestAgentWithMixin(DistributedAgentMixin, MockExistingAgent):
    """Test agent combining mixin with existing agent"""
    
    def __init__(self):
        super().__init__()
        self.personality_traits = {
            "test_trait": True,
            "consciousness_level": "awakening"
        }
        self.resource_thresholds = {
            ResourceType.CPU: 75.0,
            ResourceType.MEMORY: 80.0
        }


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis = AsyncMock()
    redis.ping = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.publish = AsyncMock(return_value=1)
    redis.aclose = AsyncMock()
    return redis


@pytest.fixture
def test_agent():
    """Create test agent with mixin"""
    return TestAgentWithMixin()


class TestDistributedAgentMixin:
    """Test suite for DistributedAgentMixin"""
    
    def test_mixin_initialization(self, test_agent):
        """Test mixin initializes without breaking existing agent"""
        # Existing functionality should work
        assert test_agent.existing_functionality_works
        assert test_agent.agent_name == "test_agent"
        
        # Distributed features should not be initialized yet
        assert not test_agent.is_distributed
        assert test_agent.comm_hub is None
        assert test_agent.resource_monitor is None
    
    @pytest.mark.asyncio
    async def test_existing_methods_still_work(self, test_agent):
        """Test existing agent methods work after mixin"""
        result = await test_agent.existing_method()
        
        assert result["status"] == "existing_works"
        assert test_agent.process_count == 1
    
    def test_personality_traits_set(self, test_agent):
        """Test personality traits are configured"""
        assert test_agent.personality_traits["test_trait"] is True
        assert test_agent.personality_traits["consciousness_level"] == "awakening"
    
    def test_resource_thresholds_set(self, test_agent):
        """Test resource thresholds are configured"""
        assert test_agent.resource_thresholds[ResourceType.CPU] == 75.0
        assert test_agent.resource_thresholds[ResourceType.MEMORY] == 80.0
    
    @pytest.mark.asyncio
    async def test_distributed_initialization(self, test_agent, mock_redis):
        """Test distributed features initialize correctly"""
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            # Setup mocks
            mock_hub = AsyncMock()
            mock_hub.initialize = AsyncMock()
            mock_hub.get_state = Mock(return_value=Mock(personality_traits={}))
            mock_hub.state_manager = Mock()
            mock_hub.state_manager.save_state = AsyncMock()
            mock_hub_class.return_value = mock_hub
            
            mock_monitor = Mock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock()
            mock_monitor.set_threshold = Mock()
            mock_monitor.register_alert_callback = Mock()
            mock_monitor.is_running = False
            mock_monitor_class.return_value = mock_monitor
            
            # Initialize distributed features
            await test_agent.initialize_distributed(mock_redis)
            
            # Verify initialization
            assert test_agent.is_distributed
            assert test_agent.comm_hub is not None
            assert test_agent.resource_monitor is not None
            
            # Verify hub was initialized
            mock_hub.initialize.assert_called_once()
            
            # Verify resource monitor was started
            mock_monitor.start.assert_called_once()
            
            # Verify thresholds were set
            assert mock_monitor.set_threshold.call_count == 2
    
    @pytest.mark.asyncio
    async def test_idempotent_initialization(self, test_agent, mock_redis):
        """Test initialize_distributed can be called multiple times safely"""
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            mock_hub = AsyncMock()
            mock_hub.initialize = AsyncMock()
            mock_hub.get_state = Mock(return_value=Mock(personality_traits={}))
            mock_hub.state_manager = Mock()
            mock_hub.state_manager.save_state = AsyncMock()
            mock_hub_class.return_value = mock_hub
            
            mock_monitor = Mock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock()
            mock_monitor.set_threshold = Mock()
            mock_monitor.register_alert_callback = Mock()
            mock_monitor.is_running = False
            mock_monitor_class.return_value = mock_monitor
            
            # Initialize twice
            await test_agent.initialize_distributed(mock_redis)
            await test_agent.initialize_distributed(mock_redis)
            
            # Should only initialize once
            assert mock_hub.initialize.call_count == 1
    
    @pytest.mark.asyncio
    async def test_distributed_shutdown(self, test_agent, mock_redis):
        """Test distributed features shutdown cleanly"""
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            mock_hub = AsyncMock()
            mock_hub.initialize = AsyncMock()
            mock_hub.shutdown = AsyncMock()
            mock_hub.get_state = Mock(return_value=Mock(personality_traits={}))
            mock_hub.state_manager = Mock()
            mock_hub.state_manager.save_state = AsyncMock()
            mock_hub_class.return_value = mock_hub
            
            mock_monitor = AsyncMock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock()
            mock_monitor.set_threshold = Mock()
            mock_monitor.register_alert_callback = Mock()
            mock_monitor_class.return_value = mock_monitor
            
            # Initialize then shutdown
            await test_agent.initialize_distributed(mock_redis)
            await test_agent.shutdown_distributed()
            
            # Verify shutdown
            assert not test_agent.is_distributed
            mock_hub.shutdown.assert_called_once()
            mock_monitor.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown_when_not_initialized(self, test_agent):
        """Test shutdown is safe when not initialized"""
        # Should not raise error
        await test_agent.shutdown_distributed()
        assert not test_agent.is_distributed
    
    def test_get_distributed_state_not_initialized(self, test_agent):
        """Test get_distributed_state when not initialized"""
        state = test_agent.get_distributed_state()
        
        assert state["distributed_enabled"] is False
        assert "message" in state
    
    @pytest.mark.asyncio
    async def test_get_distributed_state_initialized(self, test_agent, mock_redis):
        """Test get_distributed_state when initialized"""
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            mock_state = Mock()
            mock_state.agent_name = "test_agent"
            mock_state.health.value = "healthy"
            mock_state.total_decisions = 5
            mock_state.total_messages_sent = 10
            mock_state.total_messages_received = 8
            mock_state.calculate_uptime = Mock(return_value=120.5)
            mock_state.restart_count = 0
            mock_state.personality_traits = {"test": True}
            mock_state.last_heartbeat = "2025-11-12T01:00:00"
            
            mock_hub = AsyncMock()
            mock_hub.initialize = AsyncMock()
            mock_hub.get_state = Mock(return_value=mock_state)
            mock_hub.state_manager = Mock()
            mock_hub.state_manager.save_state = AsyncMock()
            mock_hub_class.return_value = mock_hub
            
            mock_monitor = Mock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock()
            mock_monitor.set_threshold = Mock()
            mock_monitor.register_alert_callback = Mock()
            mock_monitor.is_running = True
            mock_monitor_class.return_value = mock_monitor
            
            await test_agent.initialize_distributed(mock_redis)
            state = test_agent.get_distributed_state()
            
            assert state["distributed_enabled"] is True
            assert state["agent_name"] == "test_agent"
            assert state["health"] == "healthy"
            assert state["total_decisions"] == 5
            assert state["uptime_seconds"] == 120.5
    
    def test_repr_not_distributed(self, test_agent):
        """Test string representation when not distributed"""
        repr_str = repr(test_agent)
        assert "LOCAL" in repr_str
    
    @pytest.mark.asyncio
    async def test_repr_distributed(self, test_agent, mock_redis):
        """Test string representation when distributed"""
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            mock_hub = AsyncMock()
            mock_hub.initialize = AsyncMock()
            mock_hub.get_state = Mock(return_value=Mock(personality_traits={}))
            mock_hub.state_manager = Mock()
            mock_hub.state_manager.save_state = AsyncMock()
            mock_hub_class.return_value = mock_hub
            
            mock_monitor = Mock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock()
            mock_monitor.set_threshold = Mock()
            mock_monitor.register_alert_callback = Mock()
            mock_monitor.is_running = False
            mock_monitor_class.return_value = mock_monitor
            
            await test_agent.initialize_distributed(mock_redis)
            repr_str = repr(test_agent)
            assert "DISTRIBUTED" in repr_str


class TestMixinWithMultipleInheritance:
    """Test mixin works correctly with multiple inheritance"""
    
    def test_mro_order(self):
        """Test Method Resolution Order is correct"""
        # Mixin should be first in MRO after the class itself
        mro = TestAgentWithMixin.__mro__
        assert mro[0] == TestAgentWithMixin
        assert mro[1] == DistributedAgentMixin
        assert mro[2] == MockExistingAgent
    
    @pytest.mark.asyncio
    async def test_super_calls_work(self):
        """Test super() calls work correctly through MRO"""
        agent = TestAgentWithMixin()
        
        # Both initializations should have run
        assert hasattr(agent, 'agent_name')  # From MockExistingAgent
        assert hasattr(agent, '_distributed_initialized')  # From Mixin
        assert agent.existing_functionality_works  # From MockExistingAgent
        
        # Existing method should work
        result = await agent.existing_method()
        assert result["status"] == "existing_works"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
