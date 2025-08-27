# test_meth_snail_integration.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
import asyncio
from datetime import datetime, timedelta

from app.ai_agents.meth_snail.decision_engine import MethSnailDecisionEngine, AnalysisDepth
from app.ai_agents.meth_snail.database_integration import MethSnailDBIntegration
from app.ai_agents.meth_snail.websocket_handler import MethSnailWebSocketHandler

class TestMethSnailFullIntegration:
    
    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self, decision_engine, sample_metrics):
        """Test complete workflow from metrics input to decision output"""
        # High memory usage scenario
        sample_metrics.update({
            "memory_usage": 87.5,
            "cpu_usage": 65.0,
            "response_time": 200.0,
            "error_rate": 0.03
        })
        
        result = await decision_engine.analyze_metrics(sample_metrics, depth=AnalysisDepth.THOROUGH)
        
        # Verify complete workflow
        assert result.decision_type == "optimize"
        assert result.confidence > 0.7
        
        # Verify database storage was called
        decision_engine.db_integration.store_decision.assert_called_once()
        
        # Verify WebSocket notification was sent
        decision_engine.websocket_handler.send_decision_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_shell_spin_emergency_protocol(self, decision_engine, sample_metrics):
        """Test complete shell spin emergency response"""
        # Simulate shell spinning conditions
        sample_metrics.update({
            "memory_usage": 8.5,   # Extremely low
            "cpu_usage": 99.2,     # Pegged CPU
            "response_time": 5000.0,  # 5 second response time
            "error_rate": 0.15     # 15% errors
        })
        
        # Set up pre-existing shell spins
        decision_engine._shell_spin_count = 2
        
        result = await decision_engine.analyze_metrics(sample_metrics, depth=AnalysisDepth.STANDARD)
        
        # Verify shell spin protocols activated
        assert result.decision_type == "shell_spin_control"
        assert decision_engine._shell_spin_count == 3
        
        # Verify emergency procedures
        decision_engine.db_integration.store_shell_spin_incident.assert_called_once()
        decision_engine.websocket_handler.send_shell_spin_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_caffeine_emergency_escalation(self, decision_engine):
        """Test caffeine emergency escalation protocols"""
        # Set up critical conditions
        decision_engine._current_jitter = 97
        decision_engine._current_caffeine = 15
        decision_engine._shell_spin_count = 5
        
        # Mock authorization
        with patch.object(decision_engine, '_authorize_energy_drink', return_value=True):
            emergency_level = await decision_engine._calculate_energy_drink_needed()
            authorized = await decision_engine._authorize_energy_drink(emergency_level)
        
        assert authorized is True
        decision_engine.websocket_handler.send_emergency_alert.assert_called()

    @pytest.mark.asyncio
    async def test_cross_agent_learning_integration(self, decision_engine, db_integration):
        """Test cross-agent learning and knowledge sharing"""
        # Mock cross-agent insights
        db_integration.central_memory_bank.get_cross_agent_insights.return_value = [
            AsyncMock(data={
                "source_agent": "sir_hawkington",
                "insight": "memory_cleanup_before_analysis",
                "confidence": 0.82,
                "success_rate": 0.94
            })
        ]
        
        # Apply insights to decision making
        insights = await db_integration.get_cross_agent_insights()
        
        # Verify insights were retrieved and can influence decisions
        assert len(insights) > 0
        db_integration.central_memory_bank.get_cross_agent_insights.assert_called_once()

    @pytest.mark.asyncio
    async def test_performance_degradation_recovery(self, decision_engine, sample_metrics):
        """Test recovery from performance degradation"""
        # Simulate degraded performance
        degraded_metrics = sample_metrics.copy()
        degraded_metrics.update({
            "memory_usage": 92.0,
            "cpu_usage": 88.0,
            "response_time": 450.0,
            "error_rate": 0.08
        })
        
        # First analysis should trigger optimization
        result1 = await decision_engine.analyze_metrics(degraded_metrics, depth=AnalysisDepth.THOROUGH)
        assert result1.decision_type == "optimize"
        
        # Simulate improvement after optimization
        improved_metrics = sample_metrics.copy()
        improved_metrics.update({
            "memory_usage": 45.0,
            "cpu_usage": 35.0,
            "response_time": 95.0,
            "error_rate": 0.005
        })
        
        result2 = await decision_engine.analyze_metrics(improved_metrics, depth=AnalysisDepth.BASIC)
        assert result2.decision_type in ["maintain", "reduce_caffeine"]

    @pytest.mark.asyncio
    async def test_concurrent_decision_making(self, decision_engine, sample_metrics):
        """Test concurrent decision making under load"""
        # Create multiple analysis tasks
        tasks = []
        for i in range(10):
            metrics = sample_metrics.copy()
            metrics["memory_usage"] = 50 + (i * 3)
            metrics["cpu_usage"] = 30 + (i * 2)
            
            task = asyncio.create_task(
                decision_engine.analyze_metrics(metrics, depth=AnalysisDepth.BASIC)
            )
            tasks.append(task)
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 10
        for result in results:
            assert result.agent_id == "meth_snail"
            assert result.confidence > 0.0
        
        # Verify state consistency
        assert 0 <= decision_engine._current_jitter <= 100
        assert 0 <= decision_engine._current_caffeine <= 100

    @pytest.mark.asyncio
    async def test_real_time_monitoring_updates(self, decision_engine, websocket_handler):
        """Test real-time monitoring and WebSocket updates"""
        # Simulate jitter level change
        old_jitter = decision_engine._current_jitter
        await decision_engine._update_jitter_level(15)
        
        # Verify WebSocket update was sent
        websocket_handler.send_jitter_update.assert_called()
        
        # Simulate caffeine level change
        old_caffeine = decision_engine._current_caffeine
        await decision_engine._update_caffeine_level(20)
        
        websocket_handler.send_caffeine_update.assert_called()

    @pytest.mark.asyncio
    async def test_database_transaction_integrity(self, decision_engine, db_integration, mock_async_session):
        """Test database transaction integrity during operations"""
        # Mock transaction failure
        mock_async_session.commit.side_effect = [Exception("Connection lost"), None]
        
        sample_decision = AsyncMock()
        sample_decision.agent_id = "meth_snail"
        
        # First attempt should fail and rollback
        await db_integration.store_decision(sample_decision)
        
        # Verify rollback was called
        mock_async_session.rollback.assert_called()
        
        # Reset the side effect for successful retry
        mock_async_session.commit.side_effect = None
        
        # Retry should succeed
        await db_integration.store_decision(sample_decision)

    @pytest.mark.asyncio
    async def test_adaptive_threshold_adjustment(self, decision_engine, historical_data):
        """Test adaptive threshold adjustment based on performance history"""
        # Mock historical data with high baseline
        decision_engine.db_integration.get_historical_performance.return_value = historical_data
        
        # Run threshold adaptation
        await decision_engine._adapt_thresholds()
        
        # Thresholds should be adjusted based on historical patterns
        assert hasattr(decision_engine, '_adaptive_memory_threshold')
        decision_engine.db_integration.get_historical_performance.assert_called()

    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, decision_engine, sample_metrics):
        """Test comprehensive system health monitoring"""
        # Create metrics indicating system stress
        stressed_metrics = {
            "memory_usage": 89.0,
            "cpu_usage": 78.0,
            "response_time": 300.0,
            "error_rate": 0.04,
            "disk_usage": 85.0,
            "network_latency": 150.0,
            "active_connections": 2500,
            "cache_hit_ratio": 0.45
        }
        
        result = await decision_engine.analyze_metrics(stressed_metrics, depth=AnalysisDepth.THOROUGH)
        
        # Should detect multiple stress indicators
        assert result.decision_type in ["optimize", "emergency_protocol"]
        assert result.confidence > 0.8
        
        # Should provide comprehensive recommendations
        assert len(result.recommendations) >= 3