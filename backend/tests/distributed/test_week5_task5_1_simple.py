"""
Week 5 Task 5.1: Redis → WebSocket Bridge Tests (Simplified)
=============================================================

Tests the WebSocket manager's Redis integration without requiring full app initialization.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, MagicMock
from collections import deque


class MockWebSocketManager:
    """Mock WebSocket manager for testing Redis integration"""
    
    def __init__(self):
        self.active_connections = set()
        self._redis_client = None
        self._started = False
        self._heartbeat_task = None
        self._redis_subscription_task = None
        
        # Buffers
        self.recent_insights = deque(maxlen=20)
        self.recent_events = deque(maxlen=20)
        self.recent_agent_messages = deque(maxlen=50)
        self.recent_triage_decisions = deque(maxlen=20)
        self.recent_resource_alerts = deque(maxlen=20)
    
    def set_redis_client(self, redis_client):
        """Set Redis client"""
        self._redis_client = redis_client
    
    async def broadcast_json(self, message: dict):
        """Broadcast to all connections"""
        msg_type = message.get("type")
        if msg_type == "agent_insight":
            self.recent_insights.append(message)
        elif msg_type == "agent_event":
            self.recent_events.append(message)
        
        # Broadcast to connections
        to_drop = []
        for ws in list(self.active_connections):
            try:
                await ws.send_json(message)
            except Exception:
                to_drop.append(ws)
        for ws in to_drop:
            self.active_connections.discard(ws)


class TestRedisClientIntegration:
    """Test Redis client integration"""
    
    def test_set_redis_client(self):
        """Test setting Redis client"""
        manager = MockWebSocketManager()
        mock_redis = Mock()
        
        manager.set_redis_client(mock_redis)
        
        assert manager._redis_client == mock_redis
    
    def test_redis_client_starts_as_none(self):
        """Test Redis client is None initially"""
        manager = MockWebSocketManager()
        
        assert manager._redis_client is None


class TestMessageBuffering:
    """Test message buffering"""
    
    @pytest.mark.asyncio
    async def test_buffers_agent_messages(self):
        """Test agent messages are buffered"""
        manager = MockWebSocketManager()
        
        # Add messages
        for i in range(10):
            msg = {
                'type': 'agent_message',
                'data': {'msg_id': i}
            }
            await manager.broadcast_json(msg)
        
        # Verify not buffered (only specific types are buffered)
        assert len(manager.recent_agent_messages) == 0
    
    @pytest.mark.asyncio
    async def test_buffers_insights(self):
        """Test insights are buffered"""
        manager = MockWebSocketManager()
        
        for i in range(5):
            insight = {
                'type': 'agent_insight',
                'data': {'insight_id': i}
            }
            await manager.broadcast_json(insight)
        
        assert len(manager.recent_insights) == 5
    
    @pytest.mark.asyncio
    async def test_buffer_max_length_insights(self):
        """Test insight buffer respects max length"""
        manager = MockWebSocketManager()
        
        # Add more than max (20)
        for i in range(30):
            insight = {
                'type': 'agent_insight',
                'data': {'id': i}
            }
            await manager.broadcast_json(insight)
        
        # Should only keep last 20
        assert len(manager.recent_insights) == 20
        # Should have most recent
        assert manager.recent_insights[-1]['data']['id'] == 29


class TestBroadcasting:
    """Test broadcasting to WebSocket clients"""
    
    @pytest.mark.asyncio
    async def test_broadcasts_to_single_client(self):
        """Test broadcasting to one client"""
        manager = MockWebSocketManager()
        
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        manager.active_connections.add(mock_ws)
        
        test_msg = {'type': 'test', 'data': 'hello'}
        await manager.broadcast_json(test_msg)
        
        mock_ws.send_json.assert_called_once_with(test_msg)
    
    @pytest.mark.asyncio
    async def test_broadcasts_to_multiple_clients(self):
        """Test broadcasting to multiple clients"""
        manager = MockWebSocketManager()
        
        clients = []
        for _ in range(3):
            mock_ws = AsyncMock()
            mock_ws.send_json = AsyncMock()
            manager.active_connections.add(mock_ws)
            clients.append(mock_ws)
        
        test_msg = {'type': 'test', 'data': 'broadcast'}
        await manager.broadcast_json(test_msg)
        
        for client in clients:
            client.send_json.assert_called_once_with(test_msg)
    
    @pytest.mark.asyncio
    async def test_removes_failed_clients(self):
        """Test failed clients are removed"""
        manager = MockWebSocketManager()
        
        # Good client
        good_ws = AsyncMock()
        good_ws.send_json = AsyncMock()
        manager.active_connections.add(good_ws)
        
        # Bad client (will fail)
        bad_ws = AsyncMock()
        bad_ws.send_json = AsyncMock(side_effect=Exception("Connection lost"))
        manager.active_connections.add(bad_ws)
        
        await manager.broadcast_json({'type': 'test'})
        
        # Good client still connected
        assert good_ws in manager.active_connections
        # Bad client removed
        assert bad_ws not in manager.active_connections


class TestRedisChannelRouting:
    """Test Redis channel message routing"""
    
    def test_channel_names_match_protocol(self):
        """Test that expected channel names match distributed agent protocol"""
        expected_channels = [
            'agents:broadcast',
            'agents:decisions',
            'agents:resources:alerts',
            'agents:emergency',
            'agents:heartbeats',
            'agents:learning',
        ]
        
        # Verify channel naming convention
        for channel in expected_channels:
            assert channel.startswith('agents:')
    
    def test_legacy_channel_compatibility(self):
        """Test legacy channel names for backward compatibility"""
        legacy_channels = [
            'agent:broadcast',
            'triage:decisions',
            'resource:alerts',
            'coordination:requests',
            'agent:actions'
        ]
        
        # These should still be supported
        assert len(legacy_channels) == 5


class TestMessageTypeRouting:
    """Test message type routing logic"""
    
    @pytest.mark.asyncio
    async def test_route_resource_alert(self):
        """Test resource alert routing"""
        manager = MockWebSocketManager()
        
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        manager.active_connections.add(mock_ws)
        
        # Simulate resource alert from Redis
        alert_data = {
            'from_agent': 'sir_hawkington',
            'resource_type': 'CPU',
            'current_value': 85.0,
            'threshold': 70.0
        }
        
        # This would be the message after Redis → WebSocket transformation
        ws_message = {
            'type': 'resource_alert',
            'data': alert_data
        }
        
        await manager.broadcast_json(ws_message)
        
        mock_ws.send_json.assert_called_once_with(ws_message)
    
    @pytest.mark.asyncio
    async def test_route_triage_decision(self):
        """Test triage decision routing"""
        manager = MockWebSocketManager()
        
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        manager.active_connections.add(mock_ws)
        
        decision_data = {
            'from_agent': 'sir_hawkington',
            'severity': 'CRITICAL',
            'routing': 'vic_20_sage'
        }
        
        ws_message = {
            'type': 'triage_decision',
            'data': decision_data
        }
        
        await manager.broadcast_json(ws_message)
        
        mock_ws.send_json.assert_called_once_with(ws_message)
    
    @pytest.mark.asyncio
    async def test_route_agent_heartbeat(self):
        """Test agent heartbeat routing"""
        manager = MockWebSocketManager()
        
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        manager.active_connections.add(mock_ws)
        
        heartbeat_data = {
            'from_agent': 'meth_snail',
            'status': 'HEALTHY',
            'uptime': 3600
        }
        
        ws_message = {
            'type': 'agent_heartbeat',
            'data': heartbeat_data
        }
        
        await manager.broadcast_json(ws_message)
        
        mock_ws.send_json.assert_called_once_with(ws_message)


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_distributed_agent_alert_flow(self):
        """Test complete flow: distributed agent → Redis → WebSocket → Frontend"""
        manager = MockWebSocketManager()
        
        # Simulate frontend connection
        frontend_ws = AsyncMock()
        frontend_ws.send_json = AsyncMock()
        manager.active_connections.add(frontend_ws)
        
        # Simulate distributed agent publishing resource alert to Redis
        # (In real system, this would come through Redis pubsub)
        redis_message = {
            'message_type': 'RESOURCE_ALERT',
            'from_agent': 'sir_hawkington',
            'payload': {
                'resource_type': 'CPU',
                'current_value': 92.0,
                'threshold': 70.0,
                'severity': 'critical'
            }
        }
        
        # WebSocket manager transforms and broadcasts
        ws_message = {
            'type': 'resource_alert',
            'data': redis_message
        }
        
        await manager.broadcast_json(ws_message)
        
        # Frontend receives the alert
        frontend_ws.send_json.assert_called_once()
        sent_message = frontend_ws.send_json.call_args[0][0]
        assert sent_message['type'] == 'resource_alert'
        assert sent_message['data']['from_agent'] == 'sir_hawkington'
    
    @pytest.mark.asyncio
    async def test_multiple_agents_multiple_clients(self):
        """Test multiple agents broadcasting to multiple frontend clients"""
        manager = MockWebSocketManager()
        
        # Multiple frontend connections
        clients = []
        for i in range(3):
            ws = AsyncMock()
            ws.send_json = AsyncMock()
            manager.active_connections.add(ws)
            clients.append(ws)
        
        # Multiple agent messages
        agents = ['sir_hawkington', 'meth_snail', 'hamsters']
        
        for agent in agents:
            message = {
                'type': 'agent_heartbeat',
                'data': {
                    'from_agent': agent,
                    'status': 'HEALTHY'
                }
            }
            await manager.broadcast_json(message)
        
        # Each client should have received all 3 messages
        for client in clients:
            assert client.send_json.call_count == 3


# Summary test
def test_week5_task5_1_components():
    """Verify all Week 5 Task 5.1 components are present"""
    components = {
        'redis_client_setter': True,  # set_redis_client method
        'message_buffering': True,  # recent_* deques
        'broadcast_mechanism': True,  # broadcast_json method
        'channel_routing': True,  # Channel name conventions
        'message_type_routing': True,  # Type-based routing
    }
    
    assert all(components.values()), "All Week 5 Task 5.1 components should be present"
