"""
Week 5 Task 5.1: Redis → WebSocket Bridge Tests
================================================

Tests the integration between Redis pub/sub and WebSocket broadcasting.
Ensures distributed agent messages are forwarded to connected WebSocket clients.

Test Coverage:
- Redis client connection to WebSocket manager
- Channel subscription (distributed protocol)
- Message forwarding from Redis to WebSocket
- Message buffering
- Multiple client handling
- Channel routing (decisions, alerts, heartbeats, etc.)
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.api.websockets import WebSocketManager, get_websocket_manager


class TestWebSocketManagerRedisIntegration:
    """Test WebSocket manager Redis integration"""
    
    @pytest.mark.asyncio
    async def test_set_redis_client(self):
        """Test setting Redis client on WebSocket manager"""
        manager = WebSocketManager()
        mock_redis = Mock()
        
        manager.set_redis_client(mock_redis)
        
        assert manager._redis_client == mock_redis
    
    @pytest.mark.asyncio
    async def test_start_with_redis_client(self):
        """Test WebSocket manager starts Redis subscription when client is set"""
        manager = WebSocketManager()
        mock_redis = Mock()
        manager.set_redis_client(mock_redis)
        
        # Mock the subscription task
        with patch.object(manager, '_subscribe_to_agent_messages', new_callable=AsyncMock) as mock_sub:
            await manager.start()
            
            assert manager._started is True
            assert manager._redis_subscription_task is not None
    
    @pytest.mark.asyncio
    async def test_start_without_redis_client(self):
        """Test WebSocket manager starts without Redis (graceful degradation)"""
        manager = WebSocketManager()
        
        await manager.start()
        
        assert manager._started is True
        assert manager._redis_subscription_task is None
    
    @pytest.mark.asyncio
    async def test_shutdown_cancels_redis_subscription(self):
        """Test shutdown cancels Redis subscription task"""
        manager = WebSocketManager()
        mock_redis = Mock()
        manager.set_redis_client(mock_redis)
        
        # Create a mock task
        mock_task = AsyncMock()
        mock_task.cancel = Mock()
        manager._redis_subscription_task = mock_task
        manager._started = True
        
        await manager.shutdown()
        
        mock_task.cancel.assert_called_once()
        assert manager._started is False


class TestRedisChannelSubscription:
    """Test Redis channel subscription"""
    
    @pytest.mark.asyncio
    async def test_subscribes_to_distributed_channels(self):
        """Test manager subscribes to distributed agent protocol channels"""
        manager = WebSocketManager()
        
        # Create mock Redis client with pubsub
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.get_message = AsyncMock(return_value=None)
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        
        mock_redis = Mock()
        mock_redis.pubsub = Mock(return_value=mock_pubsub)
        
        manager.set_redis_client(mock_redis)
        
        # Start subscription in background
        task = asyncio.create_task(manager._subscribe_to_agent_messages())
        
        # Give it time to subscribe
        await asyncio.sleep(0.1)
        
        # Cancel the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Verify subscription was called with correct channels
        mock_pubsub.subscribe.assert_called_once()
        call_args = mock_pubsub.subscribe.call_args[0]
        
        # Check for distributed protocol channels
        assert 'agents:broadcast' in call_args
        assert 'agents:decisions' in call_args
        assert 'agents:resources:alerts' in call_args
        assert 'agents:emergency' in call_args
        assert 'agents:heartbeats' in call_args
        assert 'agents:learning' in call_args


class TestMessageForwarding:
    """Test message forwarding from Redis to WebSocket"""
    
    @pytest.mark.asyncio
    async def test_forwards_resource_alert(self):
        """Test resource alert is forwarded to WebSocket clients"""
        manager = WebSocketManager()
        
        # Create mock WebSocket connection
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        manager.active_connections.add(mock_ws)
        
        # Create mock Redis message
        alert_data = {
            'from_agent': 'sir_hawkington',
            'resource_type': 'CPU',
            'current_value': 85.0,
            'threshold': 70.0,
            'severity': 'warning'
        }
        
        mock_message = {
            'type': 'message',
            'channel': b'agents:resources:alerts',
            'data': json.dumps(alert_data).encode('utf-8')
        }
        
        # Create mock pubsub that returns our message once
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        
        call_count = 0
        async def get_message_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_message
            return None
        
        mock_pubsub.get_message = AsyncMock(side_effect=get_message_side_effect)
        
        mock_redis = Mock()
        mock_redis.pubsub = Mock(return_value=mock_pubsub)
        
        manager.set_redis_client(mock_redis)
        
        # Start subscription
        task = asyncio.create_task(manager._subscribe_to_agent_messages())
        
        # Give it time to process message
        await asyncio.sleep(0.2)
        
        # Cancel the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Verify message was sent to WebSocket
        assert mock_ws.send_json.called
        sent_data = mock_ws.send_json.call_args[0][0]
        assert sent_data['type'] == 'resource_alert'
        assert sent_data['data']['from_agent'] == 'sir_hawkington'
        assert sent_data['data']['resource_type'] == 'CPU'
        
        # Verify message was buffered
        assert len(manager.recent_resource_alerts) == 1
    
    @pytest.mark.asyncio
    async def test_forwards_triage_decision(self):
        """Test triage decision is forwarded to WebSocket clients"""
        manager = WebSocketManager()
        
        # Create mock WebSocket connection
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        manager.active_connections.add(mock_ws)
        
        # Create mock triage decision
        decision_data = {
            'from_agent': 'sir_hawkington',
            'severity': 'CRITICAL',
            'routing': 'vic_20_sage',
            'reasoning': 'Monocle has been yeeted'
        }
        
        mock_message = {
            'type': 'message',
            'channel': b'agents:decisions',
            'data': json.dumps(decision_data).encode('utf-8')
        }
        
        # Create mock pubsub
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        
        call_count = 0
        async def get_message_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_message
            return None
        
        mock_pubsub.get_message = AsyncMock(side_effect=get_message_side_effect)
        
        mock_redis = Mock()
        mock_redis.pubsub = Mock(return_value=mock_pubsub)
        
        manager.set_redis_client(mock_redis)
        
        # Start subscription
        task = asyncio.create_task(manager._subscribe_to_agent_messages())
        
        # Give it time to process
        await asyncio.sleep(0.2)
        
        # Cancel
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Verify
        assert mock_ws.send_json.called
        sent_data = mock_ws.send_json.call_args[0][0]
        assert sent_data['type'] == 'triage_decision'
        assert sent_data['data']['severity'] == 'CRITICAL'
        
        # Verify buffering
        assert len(manager.recent_triage_decisions) == 1
    
    @pytest.mark.asyncio
    async def test_forwards_agent_heartbeat(self):
        """Test agent heartbeat is forwarded to WebSocket clients"""
        manager = WebSocketManager()
        
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        manager.active_connections.add(mock_ws)
        
        heartbeat_data = {
            'from_agent': 'meth_snail',
            'status': 'HEALTHY',
            'uptime': 3600
        }
        
        mock_message = {
            'type': 'message',
            'channel': b'agents:heartbeats',
            'data': json.dumps(heartbeat_data).encode('utf-8')
        }
        
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        
        call_count = 0
        async def get_message_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_message
            return None
        
        mock_pubsub.get_message = AsyncMock(side_effect=get_message_side_effect)
        
        mock_redis = Mock()
        mock_redis.pubsub = Mock(return_value=mock_pubsub)
        
        manager.set_redis_client(mock_redis)
        
        task = asyncio.create_task(manager._subscribe_to_agent_messages())
        await asyncio.sleep(0.2)
        
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        assert mock_ws.send_json.called
        sent_data = mock_ws.send_json.call_args[0][0]
        assert sent_data['type'] == 'agent_heartbeat'
        assert sent_data['data']['from_agent'] == 'meth_snail'


class TestMultipleClients:
    """Test broadcasting to multiple WebSocket clients"""
    
    @pytest.mark.asyncio
    async def test_broadcasts_to_all_clients(self):
        """Test message is broadcast to all connected clients"""
        manager = WebSocketManager()
        
        # Create multiple mock clients
        mock_ws1 = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.send_json = AsyncMock()
        mock_ws3 = AsyncMock()
        mock_ws3.send_json = AsyncMock()
        
        manager.active_connections.add(mock_ws1)
        manager.active_connections.add(mock_ws2)
        manager.active_connections.add(mock_ws3)
        
        # Broadcast a message
        test_message = {'type': 'test', 'data': 'hello'}
        await manager.broadcast_json(test_message)
        
        # Verify all clients received it
        mock_ws1.send_json.assert_called_once_with(test_message)
        mock_ws2.send_json.assert_called_once_with(test_message)
        mock_ws3.send_json.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_removes_failed_clients(self):
        """Test failed clients are removed from active connections"""
        manager = WebSocketManager()
        
        # Create clients, one will fail
        mock_ws1 = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.send_json = AsyncMock(side_effect=Exception("Connection closed"))
        mock_ws3 = AsyncMock()
        mock_ws3.send_json = AsyncMock()
        
        manager.active_connections.add(mock_ws1)
        manager.active_connections.add(mock_ws2)
        manager.active_connections.add(mock_ws3)
        
        # Broadcast
        await manager.broadcast_json({'type': 'test'})
        
        # Verify failed client was removed
        assert mock_ws1 in manager.active_connections
        assert mock_ws2 not in manager.active_connections
        assert mock_ws3 in manager.active_connections


class TestGlobalSingleton:
    """Test global WebSocket manager singleton"""
    
    def test_singleton_returns_same_instance(self):
        """Test get_websocket_manager returns same instance"""
        manager1 = get_websocket_manager()
        manager2 = get_websocket_manager()
        
        assert manager1 is manager2


class TestMessageBuffering:
    """Test message buffering for recent history"""
    
    @pytest.mark.asyncio
    async def test_buffers_resource_alerts(self):
        """Test resource alerts are buffered"""
        manager = WebSocketManager()
        
        # Add some alerts
        for i in range(5):
            alert = {
                'type': 'resource_alert',
                'data': {'alert_id': i}
            }
            await manager.broadcast_json(alert)
        
        # Verify buffering
        assert len(manager.recent_resource_alerts) == 5
    
    @pytest.mark.asyncio
    async def test_buffer_max_length(self):
        """Test buffers respect max length"""
        manager = WebSocketManager()
        
        # Add more than max (50 for agent messages)
        for i in range(60):
            msg = {
                'type': 'agent_message',
                'data': {'msg_id': i}
            }
            await manager.broadcast_json(msg)
        
        # Should only keep last 50
        assert len(manager.recent_agent_messages) == 50
        # Should have the most recent ones
        assert manager.recent_agent_messages[-1]['data']['msg_id'] == 59
