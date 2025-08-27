# test_meth_snail_websocket_handler.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
import json
from datetime import datetime

from app.ai_agents.meth_snail.websocket_handler import MethSnailWebSocketHandler

class TestMethSnailWebSocketHandler:
    
    @pytest.mark.asyncio
    async def test_send_decision_broadcast(self, websocket_handler, websocket_manager):
        """Test broadcasting decision results to connected clients"""
        from app.ai_agents.meth_snail.decision_engine import DecisionResult
        
        decision = DecisionResult(
            agent_id="meth_snail",
            decision_type="optimize",
            confidence=0.87,
            recommendations=["Clear memory buffers", "Optimize cache"],
            metrics_analyzed={"memory_usage": 78.5, "cpu_usage": 45.2}
        )
        
        await websocket_handler.send_decision_update(decision)
        
        # Verify broadcast was called with correct data
        websocket_manager.broadcast.assert_called_once()
        broadcast_data = websocket_manager.broadcast.call_args[0][0]
        
        assert broadcast_data["type"] == "decision_update"
        assert broadcast_data["agent_id"] == "meth_snail"
        assert broadcast_data["decision_type"] == "optimize"
        assert broadcast_data["confidence"] == 0.87
        assert len(broadcast_data["recommendations"]) == 2

    @pytest.mark.asyncio
    async def test_send_jitter_level_update(self, websocket_handler, websocket_manager):
        """Test jitter level update broadcasting"""
        jitter_level = 73.5
        caffeine_level = 62.0
        
        await websocket_handler.send_jitter_update(jitter_level, caffeine_level)
        
        websocket_manager.send_to_agent.assert_called_once()
        call_args = websocket_manager.send_to_agent.call_args
        
        assert call_args[0][0] == "meth_snail"  # agent_id
        
        message_data = call_args[0][1]
        assert message_data["type"] == "jitter_update"
        assert message_data["jitter_level"] == 73.5
        assert message_data["caffeine_level"] == 62.0
        assert "timestamp" in message_data

    @pytest.mark.asyncio
    async def test_send_shell_spin_alert(self, websocket_handler, websocket_manager):
        """Test shell spin incident alert broadcasting"""
        incident_data = {
            "spin_count": 3,
            "duration": 45.7,
            "memory_usage": 12.5,
            "cpu_usage": 98.2,
            "recovery_actions": ["force_gc", "restart_service"]
        }
        
        await websocket_handler.send_shell_spin_alert(incident_data)
        
        websocket_manager.broadcast.assert_called_once()
        alert_data = websocket_manager.broadcast.call_args[0][0]
        
        assert alert_data["type"] == "shell_spin_alert"
        assert alert_data["severity"] == "high"
        assert alert_data["agent_id"] == "meth_snail"
        assert alert_data["incident"]["spin_count"] == 3
        assert alert_data["incident"]["duration"] == 45.7

    @pytest.mark.asyncio
    async def test_send_caffeine_update(self, websocket_handler, websocket_manager):
        """Test caffeine level update notifications"""
        old_level = 45.0
        new_level = 62.0
        reason = "performance_optimization"
        
        await websocket_handler.send_caffeine_update(old_level, new_level, reason)
        
        websocket_manager.send_to_agent.assert_called_once()
        call_args = websocket_manager.send_to_agent.call_args
        
        message_data = call_args[0][1]
        assert message_data["type"] == "caffeine_update"
        assert message_data["old_level"] == 45.0
        assert message_data["new_level"] == 62.0
        assert message_data["reason"] == "performance_optimization"
        assert message_data["change"] == 17.0

    @pytest.mark.asyncio
    async def test_send_emergency_alert(self, websocket_handler, websocket_manager):
        """Test emergency caffeine protocol alerts"""
        emergency_data = {
            "level": "CRITICAL",
            "jitter_level": 95.0,
            "caffeine_level": 25.0,
            "shell_spins": 4,
            "energy_drink_authorized": True,
            "protocol_activated": "EMERGENCY_CAFFEINATION"
        }
        
        await websocket_handler.send_emergency_alert(emergency_data)
        
        # Should broadcast to all and send specific message to agent
        websocket_manager.broadcast.assert_called_once()
        websocket_manager.send_to_agent.assert_called_once()
        
        # Check broadcast message
        broadcast_data = websocket_manager.broadcast.call_args[0][0]
        assert broadcast_data["type"] == "emergency_alert"
        assert broadcast_data["priority"] == "CRITICAL"
        assert broadcast_data["agent_id"] == "meth_snail"

    @pytest.mark.asyncio
    async def test_send_performance_metrics(self, websocket_handler, websocket_manager):
        """Test performance metrics streaming"""
        metrics = {
            "analysis_time": 125.7,
            "decisions_per_minute": 15.2,
            "average_confidence": 0.82,
            "successful_optimizations": 47,
            "memory_savings": 2.3,  # GB
            "uptime": 3600  # seconds
        }
        
        await websocket_handler.send_performance_metrics(metrics)
        
        websocket_manager.send_to_agent.assert_called_once()
        call_args = websocket_manager.send_to_agent.call_args[0][1]
        
        assert call_args["type"] == "performance_metrics"
        assert call_args["metrics"]["analysis_time"] == 125.7
        assert call_args["metrics"]["decisions_per_minute"] == 15.2

    @pytest.mark.asyncio
    async def test_connection_status_handling(self, websocket_handler, websocket_manager):
        """Test handling of connection status changes"""
        # Test when not connected
        websocket_manager.is_connected.return_value = False
        
        decision = MagicMock()
        decision.agent_id = "meth_snail"
        decision.decision_type = "optimize"
        
        # Should not raise error when disconnected
        await websocket_handler.send_decision_update(decision)
        
        # Should not call broadcast when disconnected
        websocket_manager.broadcast.assert_not_called()

    @pytest.mark.asyncio
    async def test_message_queuing_when_disconnected(self, websocket_handler, websocket_manager):
        """Test message queuing when WebSocket is disconnected"""
        websocket_manager.is_connected.return_value = False
        
        # Send multiple messages while disconnected
        await websocket_handler.send_jitter_update(50.0, 60.0)
        await websocket_handler.send_jitter_update(55.0, 65.0)
        
        # Should queue messages
        assert len(websocket_handler._message_queue) == 2
        
        # Simulate reconnection
        websocket_manager.is_connected.return_value = True
        await websocket_handler._flush_message_queue()
        
        # Should send queued messages
        assert websocket_manager.send_to_agent.call_count == 2
        assert len(websocket_handler._message_queue) == 0

    @pytest.mark.asyncio
    async def test_error_handling_in_websocket_operations(self, websocket_handler, websocket_manager):
        """Test error handling in WebSocket operations"""
        # Simulate WebSocket error
        websocket_manager.broadcast.side_effect = Exception("WebSocket connection error")
        
        decision = MagicMock()
        decision.agent_id = "meth_snail"
        decision.decision_type = "optimize"
        
        # Should handle error gracefully
        try:
            await websocket_handler.send_decision_update(decision)
        except Exception:
            pytest.fail("WebSocket error was not handled gracefully")
        
        # Should log error and continue operation
        assert websocket_handler._last_error is not None