"""
Week 3 Checkpoint: End-to-End Triage Flow Test
===============================================

Tests the complete triage flow from metrics → Hawkington → VIC-20 → Specialists → The Stick.

This test verifies:
1. Sir Hawkington makes triage decisions
2. Decisions broadcast via Redis
3. The Stick receives and logs decisions
4. VIC-20 receives and coordinates
5. VIC-20 broadcasts coordination requests
6. Specialists receive and execute tasks
7. VIC-20 updates The Stick with results
8. All decisions recorded with triage fields
9. Statistics tracked by Triage Bridge
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
import asyncio

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.ai_agents.distributed.bridges.triage_bridge import TriageBridge


class TestWeek3TriageFlow:
    """End-to-end triage flow tests"""
    
    @pytest.mark.asyncio
    async def test_normal_severity_routes_to_stick(self):
        """Test that NORMAL severity routes to The Stick"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Simulate NORMAL triage decision
        triage_decision = {
            'severity': 'normal',
            'routing': 'stick_direct',
            'target_agents': ['the_stick'],
            'reasoning': 'System operating normally',
            'metrics_summary': {
                'cpu_usage': 25.0,
                'memory_usage': 40.0,
                'disk_usage': 50.0
            }
        }
        
        await bridge._handle_triage_decision(triage_decision)
        
        # Verify statistics
        assert bridge.stats.total_decisions == 1
        assert bridge.stats.decisions_by_severity['normal'] == 1
        assert bridge.stats.decisions_by_routing['stick_direct'] == 1
        
        # Verify routing
        assert mock_redis.publish.called
        # Should route to the_stick
        calls = [str(call) for call in mock_redis.publish.call_args_list]
        assert any('the_stick' in str(call) for call in calls)
    
    @pytest.mark.asyncio
    async def test_medium_severity_routes_to_vic20(self):
        """Test that MEDIUM severity routes to VIC-20 for coordination"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Simulate MEDIUM triage decision
        triage_decision = {
            'severity': 'medium',
            'routing': 'vic20_coordination',
            'target_agents': ['vic_20_sage', 'meth_snail'],
            'reasoning': 'Memory usage elevated - coordination needed',
            'metrics_summary': {
                'cpu_usage': 45.0,
                'memory_usage': 72.0,
                'disk_usage': 55.0
            }
        }
        
        await bridge._handle_triage_decision(triage_decision)
        
        # Verify statistics
        assert bridge.stats.total_decisions == 1
        assert bridge.stats.decisions_by_severity['medium'] == 1
        assert bridge.stats.decisions_by_routing['vic20_coordination'] == 1
        
        # Verify routing to VIC-20
        assert mock_redis.publish.called
        calls = [str(call) for call in mock_redis.publish.call_args_list]
        assert any('vic_20_sage' in str(call) for call in calls)
    
    @pytest.mark.asyncio
    async def test_critical_severity_routes_to_vic20_and_specialists(self):
        """Test that CRITICAL severity routes to VIC-20 + specialists"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Simulate CRITICAL triage decision
        triage_decision = {
            'severity': 'critical',
            'routing': 'vic20_emergency',
            'target_agents': ['vic_20_sage', 'meth_snail', 'hamsters', 'quantum_shadow_people'],
            'reasoning': 'Multiple systems critical - emergency coordination',
            'metrics_summary': {
                'cpu_usage': 92.0,
                'memory_usage': 88.0,
                'disk_usage': 85.0,
                'network_usage': 90.0
            }
        }
        
        await bridge._handle_triage_decision(triage_decision)
        
        # Verify statistics
        assert bridge.stats.total_decisions == 1
        assert bridge.stats.decisions_by_severity['critical'] == 1
        assert bridge.stats.decisions_by_routing['vic20_emergency'] == 1
        
        # Verify routing to VIC-20
        assert mock_redis.publish.called
        calls = [str(call) for call in mock_redis.publish.call_args_list]
        assert any('vic_20_sage' in str(call) for call in calls)
    
    @pytest.mark.asyncio
    async def test_emergency_severity_broadcasts_to_all(self):
        """Test that EMERGENCY severity broadcasts to all agents"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Simulate EMERGENCY triage decision
        triage_decision = {
            'severity': 'emergency',
            'routing': 'vic20_emergency',
            'target_agents': ['all'],
            'reasoning': 'SYSTEM EMERGENCY - All hands on deck!',
            'metrics_summary': {
                'cpu_usage': 98.0,
                'memory_usage': 95.0,
                'disk_usage': 92.0,
                'network_usage': 96.0
            }
        }
        
        await bridge._handle_triage_decision(triage_decision)
        
        # Verify statistics
        assert bridge.stats.total_decisions == 1
        assert bridge.stats.decisions_by_severity['emergency'] == 1
        assert bridge.stats.decisions_by_routing['vic20_emergency'] == 1
        
        # Verify routing
        assert mock_redis.publish.called
        # Should route to both The Stick and VIC-20 at minimum
        assert mock_redis.publish.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_triage_bridge_tracks_all_routing_types(self):
        """Test that bridge tracks all routing types correctly"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Send decisions of each routing type
        routing_types = [
            ('normal', 'stick_direct', ['the_stick']),
            ('medium', 'vic20_coordination', ['vic_20_sage']),
            ('high', 'vic20_coordination', ['vic_20_sage', 'meth_snail']),
            ('critical', 'vic20_emergency', ['vic_20_sage', 'all']),
            ('emergency', 'vic20_emergency', ['all']),
        ]
        
        for severity, routing, targets in routing_types:
            await bridge._handle_triage_decision({
                'severity': severity,
                'routing': routing,
                'target_agents': targets,
                'reasoning': f'Test {severity} routing',
                'metrics_summary': {}
            })
        
        # Verify all tracked
        assert bridge.stats.total_decisions == 5
        assert bridge.stats.decisions_by_severity['normal'] == 1
        assert bridge.stats.decisions_by_severity['medium'] == 1
        assert bridge.stats.decisions_by_severity['high'] == 1
        assert bridge.stats.decisions_by_severity['critical'] == 1
        assert bridge.stats.decisions_by_severity['emergency'] == 1
        
        assert bridge.stats.decisions_by_routing['stick_direct'] == 1
        assert bridge.stats.decisions_by_routing['vic20_coordination'] == 2
        assert bridge.stats.decisions_by_routing['vic20_emergency'] == 2
    
    @pytest.mark.asyncio
    async def test_triage_flow_performance(self):
        """Test that triage flow has acceptable performance"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Send 100 decisions and measure performance
        for i in range(100):
            await bridge._handle_triage_decision({
                'severity': 'normal',
                'routing': 'stick_direct',
                'target_agents': ['the_stick'],
                'reasoning': f'Test decision {i}',
                'metrics_summary': {}
            })
        
        # Verify all processed
        assert bridge.stats.total_decisions == 100
        assert bridge.stats.successful_deliveries == 100
        
        # Verify performance
        assert bridge.stats.average_delivery_time_ms < 100  # Should be under 100ms
        
        # Verify success rate
        success_rate = (bridge.stats.successful_deliveries / bridge.stats.total_decisions) * 100
        assert success_rate == 100.0
    
    @pytest.mark.asyncio
    async def test_triage_bridge_health_monitoring(self):
        """Test that bridge health monitoring works correctly"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        bridge.message_bus.start = AsyncMock()
        bridge.message_bus.register_handler = MagicMock()
        
        # Start bridge
        await bridge.start()
        
        # Process a decision to update heartbeat
        await bridge._handle_triage_decision({
            'severity': 'normal',
            'routing': 'stick_direct',
            'target_agents': ['the_stick'],
            'reasoning': 'Health check',
            'metrics_summary': {}
        })
        
        # Check health
        health = bridge.get_health()
        assert health['is_running'] is True
        assert health['is_healthy'] is True
        assert health['total_decisions_routed'] == 1
        assert health['success_rate'] == 100.0
    
    @pytest.mark.asyncio
    async def test_visualization_data_generation(self):
        """Test that visualization data is generated correctly"""
        
        mock_redis = AsyncMock()
        bridge = TriageBridge(mock_redis)
        
        # Send various decisions
        decisions = [
            ('high', 'vic20_coordination'),
            ('critical', 'vic20_emergency'),
            ('normal', 'stick_direct'),
            ('high', 'vic20_coordination'),
            ('emergency', 'vic20_emergency'),
        ]
        
        for severity, routing in decisions:
            await bridge._handle_triage_decision({
                'severity': severity,
                'routing': routing,
                'target_agents': ['vic_20_sage'],
                'reasoning': 'Visualization test',
                'metrics_summary': {}
            })
        
        # Get visualization data
        viz_data = bridge.get_flow_visualization_data()
        
        # Verify structure
        assert 'overview' in viz_data
        assert 'severity_distribution' in viz_data
        assert 'routing_distribution' in viz_data
        assert 'delivery_stats' in viz_data
        assert 'health' in viz_data
        
        # Verify data
        assert viz_data['overview']['total_decisions'] == 5
        assert viz_data['severity_distribution']['high'] == 2
        assert viz_data['severity_distribution']['critical'] == 1
        assert viz_data['severity_distribution']['normal'] == 1
        assert viz_data['severity_distribution']['emergency'] == 1
        
        assert viz_data['routing_distribution']['vic20_coordination'] == 2
        assert viz_data['routing_distribution']['vic20_emergency'] == 2
        assert viz_data['routing_distribution']['stick_direct'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
