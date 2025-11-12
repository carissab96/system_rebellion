"""
Tests for SirHawkingtonDistributed
==================================

Verify Sir Hawkington's existing functionality is preserved
while distributed features are added.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai_agents.sir_hawkington.distributed_hawkington import SirHawkingtonDistributed
from app.ai_agents.distributed.resource_monitor import ResourceType


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
def hawkington():
    """Create Sir Hawkington (not yet distributed)"""
    return SirHawkingtonDistributed(db_getter=None)


class TestSirHawkingtonDistributed:
    """Test suite for distributed Sir Hawkington"""
    
    def test_initialization(self, hawkington):
        """Test Sir Hawkington initializes correctly"""
        assert hawkington.agent_name == "sir_hawkington"
        assert not hawkington.is_distributed  # Not distributed yet
        assert hawkington.is_active
        assert hawkington.total_analyses == 0
        assert len(hawkington.monocle_yeet_incidents) == 0
    
    def test_personality_traits(self, hawkington):
        """Test Sir Hawkington's distinguished personality is preserved"""
        assert hawkington.personality_traits["aristocratic"] is True
        assert hawkington.personality_traits["monocle_yeeting_enabled"] is True
        assert hawkington.personality_traits["triage_commander"] is True
        assert hawkington.personality_traits["distinguished"] is True
    
    def test_resource_thresholds(self, hawkington):
        """Test CPU monitoring threshold is configured"""
        assert ResourceType.CPU in hawkington.resource_thresholds
        assert hawkington.resource_thresholds[ResourceType.CPU] == 70.0
    
    def test_original_thresholds_preserved(self, hawkington):
        """Test original Sir Hawkington thresholds are preserved"""
        assert hawkington.concern_threshold == 0.65
        assert hawkington.alert_threshold == 0.85
        assert hawkington.critical_threshold == 0.95
    
    @pytest.mark.asyncio
    async def test_distributed_initialization(self, hawkington, mock_redis):
        """Test distributed features initialize without breaking Sir Hawkington"""
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
            await hawkington.initialize_distributed(mock_redis)
            
            # Verify distributed features initialized
            assert hawkington.is_distributed
            assert hawkington.comm_hub is not None
            assert hawkington.resource_monitor is not None
            
            # Verify CPU threshold was set
            mock_monitor.set_threshold.assert_called_with(ResourceType.CPU, 70.0)
            
            # Verify original Sir Hawkington still works
            assert hawkington.is_active
            assert hawkington.agent_name == "sir_hawkington"
    
    @pytest.mark.asyncio
    async def test_analyze_metrics_without_distributed(self, hawkington):
        """Test analyze_metrics works without distributed features"""
        # Mock database
        hawkington.db = AsyncMock()
        hawkington.db.save_decision = AsyncMock()
        
        metrics_data = {
            'cpu_usage': 45.0,
            'memory_usage': 60.0,
            'disk_usage': 70.0
        }
        
        # Should work without distributed features
        decision = await hawkington.analyze_metrics(metrics_data)
        
        # Verify decision was made
        assert decision is not None
        assert hawkington.total_analyses == 1
    
    @pytest.mark.asyncio
    async def test_analyze_metrics_with_distributed(self, hawkington, mock_redis):
        """Test analyze_metrics records decisions in distributed state"""
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            # Setup mocks
            mock_hub = AsyncMock()
            mock_hub.initialize = AsyncMock()
            mock_hub.get_state = Mock(return_value=Mock(personality_traits={}))
            mock_hub.state_manager = Mock()
            mock_hub.state_manager.save_state = AsyncMock()
            mock_hub.make_decision = AsyncMock(return_value={"decision_id": "test123"})
            mock_hub.broadcast_message = AsyncMock()
            mock_hub_class.return_value = mock_hub
            
            mock_monitor = Mock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock()
            mock_monitor.set_threshold = Mock()
            mock_monitor.register_alert_callback = Mock()
            mock_monitor.is_running = False
            mock_monitor_class.return_value = mock_monitor
            
            # Initialize distributed
            await hawkington.initialize_distributed(mock_redis)
            
            # Mock database
            hawkington.db = AsyncMock()
            hawkington.db.save_decision = AsyncMock()
            
            metrics_data = {
                'cpu_usage': 45.0,
                'memory_usage': 60.0,
                'disk_usage': 70.0
            }
            
            # Analyze metrics
            decision = await hawkington.analyze_metrics(metrics_data)
            
            # Verify decision was made
            assert decision is not None
            assert hawkington.total_analyses == 1
            
            # Verify distributed decision was recorded
            assert mock_hub.make_decision.called
    
    @pytest.mark.asyncio
    async def test_monocle_yeet_distributed(self, hawkington, mock_redis):
        """Test monocle yeet is broadcast to other agents"""
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            # Setup mocks
            mock_hub = AsyncMock()
            mock_hub.initialize = AsyncMock()
            mock_hub.get_state = Mock(return_value=Mock(personality_traits={}))
            mock_hub.state_manager = Mock()
            mock_hub.state_manager.save_state = AsyncMock()
            mock_hub.make_decision = AsyncMock(return_value={"decision_id": "yeet123"})
            mock_hub.broadcast_message = AsyncMock()
            mock_hub_class.return_value = mock_hub
            
            mock_monitor = Mock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock()
            mock_monitor.set_threshold = Mock()
            mock_monitor.register_alert_callback = Mock()
            mock_monitor.is_running = False
            mock_monitor_class.return_value = mock_monitor
            
            # Initialize distributed
            await hawkington.initialize_distributed(mock_redis)
            
            # Trigger monocle yeet
            await hawkington._record_monocle_yeet(
                missing_metrics=['cpu_usage'],
                invalid_metrics=[],
                reason="Missing critical metrics",
                intensity="concerned",
                user_id="test_user"
            )
            
            # Verify monocle yeet was recorded
            assert len(hawkington.monocle_yeet_incidents) == 1
            
            # Verify distributed decision was made
            assert mock_hub.make_decision.called
            
            # Verify broadcast was sent
            assert mock_hub.broadcast_message.called
    
    def test_get_agent_status(self, hawkington):
        """Test get_agent_status includes distributed state"""
        status = hawkington.get_agent_status()
        
        assert status["agent_name"] == "sir_hawkington"
        assert status["agent_type"] == "triage_commander"
        assert status["is_active"] is True
        assert "monocle_state" in status
        assert "total_analyses" in status
        assert "monocle_yeet_count" in status
        assert "thresholds" in status
        assert "distributed" in status
        
        # Distributed should show not enabled
        assert status["distributed"]["distributed_enabled"] is False
    
    @pytest.mark.asyncio
    async def test_get_agent_status_distributed(self, hawkington, mock_redis):
        """Test get_agent_status shows distributed state when enabled"""
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            # Setup mocks
            mock_state = Mock()
            mock_state.agent_name = "sir_hawkington"
            mock_state.health.value = "healthy"
            mock_state.total_decisions = 5
            mock_state.total_messages_sent = 10
            mock_state.total_messages_received = 8
            mock_state.calculate_uptime = Mock(return_value=120.5)
            mock_state.restart_count = 0
            mock_state.personality_traits = {"aristocratic": True}
            mock_state.last_heartbeat = "2025-11-12T02:00:00"
            
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
            
            # Initialize distributed
            await hawkington.initialize_distributed(mock_redis)
            
            status = hawkington.get_agent_status()
            
            # Verify distributed state is included
            assert status["distributed"]["distributed_enabled"] is True
            assert status["distributed"]["health"] == "healthy"
            assert status["distributed"]["total_decisions"] == 5
    
    def test_repr(self, hawkington):
        """Test string representation"""
        repr_str = repr(hawkington)
        
        assert "SirHawkingtonDistributed" in repr_str
        assert "LOCAL" in repr_str  # Not distributed yet
        assert "monocle=" in repr_str
        assert "analyses=" in repr_str
        assert "yeets=" in repr_str
    
    @pytest.mark.asyncio
    async def test_repr_distributed(self, hawkington, mock_redis):
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
            
            await hawkington.initialize_distributed(mock_redis)
            
            repr_str = repr(hawkington)
            assert "DISTRIBUTED" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
