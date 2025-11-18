"""
Test Triage Bridge (Task 3.4)
==============================

Tests that the triage bridge reliably routes decisions to correct agents.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.ai_agents.distributed.bridges.triage_bridge import (
    TriageBridge,
    TriageRoutingStats,
    create_triage_bridge
)


class TestTriageBridge:
    """Test triage bridge routing and statistics"""
    
    @pytest.mark.asyncio
    async def test_triage_bridge_initialization(self):
        """Test that triage bridge initializes correctly"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        assert bridge.redis_client is mock_redis
        assert bridge.is_running is False
        assert bridge.stats.total_decisions == 0
    
    @pytest.mark.asyncio
    async def test_triage_bridge_start_stop(self):
        """Test starting and stopping the bridge"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Mock message bus
        bridge.message_bus.start = AsyncMock()
        bridge.message_bus.stop = AsyncMock()
        bridge.message_bus.register_handler = MagicMock()
        
        # Start
        await bridge.start()
        assert bridge.is_running is True
        assert bridge._last_heartbeat is not None
        bridge.message_bus.start.assert_called_once()
        
        # Stop
        await bridge.stop()
        assert bridge.is_running is False
        bridge.message_bus.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_route_to_stick_and_vic20(self):
        """Test routing to The Stick and VIC-20"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Test routing
        message_data = {
            'severity': 'high',
            'routing': 'vic20_coordination',
            'target_agents': ['the_stick', 'vic_20_sage'],
            'metrics_summary': {}
        }
        
        success = await bridge._route_to_agents(
            ['the_stick', 'vic_20_sage'],
            message_data
        )
        
        assert success is True
        # Should have published to both agents
        assert mock_redis.publish.call_count == 2
    
    @pytest.mark.asyncio
    async def test_routing_statistics_tracking(self):
        """Test that routing statistics are tracked correctly"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        bridge.message_bus.start = AsyncMock()
        bridge.message_bus.register_handler = MagicMock()
        
        await bridge.start()
        
        # Simulate handling multiple triage decisions
        decisions = [
            {'severity': 'high', 'routing': 'vic20_coordination', 'target_agents': ['vic_20_sage']},
            {'severity': 'critical', 'routing': 'vic20_emergency', 'target_agents': ['vic_20_sage']},
            {'severity': 'normal', 'routing': 'stick_direct', 'target_agents': ['the_stick']},
            {'severity': 'high', 'routing': 'vic20_coordination', 'target_agents': ['vic_20_sage']},
        ]
        
        for decision in decisions:
            await bridge._handle_triage_decision(decision)
        
        # Check statistics
        stats = bridge.get_stats()
        assert stats['total_decisions'] == 4
        assert stats['decisions_by_severity']['high'] == 2
        assert stats['decisions_by_severity']['critical'] == 1
        assert stats['decisions_by_severity']['normal'] == 1
        assert stats['decisions_by_routing']['vic20_coordination'] == 2
        assert stats['decisions_by_routing']['vic20_emergency'] == 1
        assert stats['decisions_by_routing']['stick_direct'] == 1
    
    @pytest.mark.asyncio
    async def test_routing_by_severity(self):
        """Test routing decisions of different severities"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Test NORMAL severity
        await bridge._handle_triage_decision({
            'severity': 'normal',
            'routing': 'stick_direct',
            'target_agents': ['the_stick']
        })
        
        assert bridge.stats.decisions_by_severity['normal'] == 1
        
        # Test EMERGENCY severity
        await bridge._handle_triage_decision({
            'severity': 'emergency',
            'routing': 'vic20_emergency',
            'target_agents': ['vic_20_sage', 'all']
        })
        
        assert bridge.stats.decisions_by_severity['emergency'] == 1
    
    @pytest.mark.asyncio
    async def test_routing_by_type(self):
        """Test routing decisions by routing type"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Test STICK_DIRECT routing
        await bridge._handle_triage_decision({
            'severity': 'normal',
            'routing': 'stick_direct',
            'target_agents': ['the_stick']
        })
        
        assert bridge.stats.decisions_by_routing['stick_direct'] == 1
        
        # Test VIC20_COORDINATION routing
        await bridge._handle_triage_decision({
            'severity': 'medium',
            'routing': 'vic20_coordination',
            'target_agents': ['vic_20_sage']
        })
        
        assert bridge.stats.decisions_by_routing['vic20_coordination'] == 1
        
        # Test VIC20_EMERGENCY routing
        await bridge._handle_triage_decision({
            'severity': 'emergency',
            'routing': 'vic20_emergency',
            'target_agents': ['vic_20_sage', 'all']
        })
        
        assert bridge.stats.decisions_by_routing['vic20_emergency'] == 1
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self):
        """Test bridge health monitoring"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        bridge.message_bus.start = AsyncMock()
        bridge.message_bus.register_handler = MagicMock()
        
        await bridge.start()
        
        # Handle a decision to update heartbeat
        await bridge._handle_triage_decision({
            'severity': 'normal',
            'routing': 'stick_direct',
            'target_agents': ['the_stick']
        })
        
        # Check health
        health = bridge.get_health()
        assert health['is_running'] is True
        assert health['is_healthy'] is True
        assert health['last_heartbeat'] is not None
        assert health['seconds_since_heartbeat'] is not None
        assert health['seconds_since_heartbeat'] < 5  # Should be very recent
    
    @pytest.mark.asyncio
    async def test_flow_visualization_data(self):
        """Test generation of flow visualization data"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Simulate some decisions
        await bridge._handle_triage_decision({
            'severity': 'high',
            'routing': 'vic20_coordination',
            'target_agents': ['vic_20_sage']
        })
        await bridge._handle_triage_decision({
            'severity': 'critical',
            'routing': 'vic20_emergency',
            'target_agents': ['vic_20_sage', 'all']
        })
        
        # Get visualization data
        viz_data = bridge.get_flow_visualization_data()
        
        assert 'overview' in viz_data
        assert 'severity_distribution' in viz_data
        assert 'routing_distribution' in viz_data
        assert 'delivery_stats' in viz_data
        assert 'health' in viz_data
        
        assert viz_data['overview']['total_decisions'] == 2
        assert viz_data['severity_distribution']['high'] == 1
        assert viz_data['severity_distribution']['critical'] == 1
    
    @pytest.mark.asyncio
    async def test_delivery_time_tracking(self):
        """Test that delivery times are tracked"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Handle a decision
        await bridge._handle_triage_decision({
            'severity': 'normal',
            'routing': 'stick_direct',
            'target_agents': ['the_stick']
        })
        
        # Check that delivery time was recorded
        assert len(bridge._delivery_times) > 0
        assert bridge.stats.average_delivery_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_create_triage_bridge_convenience_function(self):
        """Test the convenience function for creating a bridge"""
        
        mock_redis = AsyncMock()
        
        with patch.object(TriageBridge, 'start', new_callable=AsyncMock) as mock_start:
            bridge = await create_triage_bridge(mock_redis)
            
            assert isinstance(bridge, TriageBridge)
            mock_start.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
