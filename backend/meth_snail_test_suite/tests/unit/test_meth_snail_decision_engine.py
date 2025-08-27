# test_meth_snail_decision_engine.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from app.ai_agents.meth_snail.decision_engine import (
    MethSnailDecisionEngine, 
    DecisionResult, 
    AnalysisDepth,
    CaffeineEmergencyLevel
)

class TestMethSnailDecisionEngine:
    
    @pytest.mark.asyncio
    async def test_basic_analysis_normal_metrics(self, decision_engine, sample_metrics):
        """Test basic analysis with normal system metrics"""
        sample_metrics.update({
            "memory_usage": 45.0,
            "cpu_usage": 35.0,
            "response_time": 95.0
        })
        
        result = await decision_engine.analyze_metrics(sample_metrics, depth=AnalysisDepth.BASIC)
        
        assert isinstance(result, DecisionResult)
        assert result.agent_id == "meth_snail"
        assert result.decision_type in ["maintain", "optimize", "caffeinate"]
        assert result.confidence >= 0.5
        assert result.analysis_depth == AnalysisDepth.BASIC
        assert len(result.recommendations) > 0

    @pytest.mark.asyncio
    async def test_basic_analysis_high_memory_usage(self, decision_engine, sample_metrics):
        """Test basic analysis detecting memory pressure"""
        sample_metrics.update({
            "memory_usage": 88.5,  # High memory usage
            "cpu_usage": 35.0,
            "response_time": 150.0
        })
        
        result = await decision_engine.analyze_metrics(sample_metrics, depth=AnalysisDepth.BASIC)
        
        assert result.decision_type == "optimize"
        assert "memory pressure detected" in " ".join(result.recommendations).lower()
        assert result.confidence >= 0.7

    @pytest.mark.asyncio
    async def test_standard_analysis_with_trending(self, decision_engine, sample_metrics):
        """Test standard analysis with trend detection"""
        # Mock recent metrics for trending
        decision_engine.db_integration.get_recent_metrics = AsyncMock(return_value=[
            {"memory_usage": 60, "timestamp": datetime.utcnow() - timedelta(minutes=10)},
            {"memory_usage": 65, "timestamp": datetime.utcnow() - timedelta(minutes=5)},
            {"memory_usage": 70, "timestamp": datetime.utcnow()},
        ])
        
        sample_metrics["memory_usage"] = 75.0  # Continuing upward trend
        
        result = await decision_engine.analyze_metrics(sample_metrics, depth=AnalysisDepth.STANDARD)
        
        assert result.decision_type == "optimize"
        assert result.analysis_depth == AnalysisDepth.STANDARD
        assert "trending upward" in " ".join(result.recommendations).lower() or "increasing" in " ".join(result.recommendations).lower()

    @pytest.mark.asyncio
    async def test_thorough_analysis_with_historical(self, decision_engine, sample_metrics, historical_data):
        """Test thorough analysis using historical data patterns"""
        decision_engine.db_integration.get_historical_performance = AsyncMock(return_value=historical_data)
        
        # Simulate pattern recognition
        sample_metrics.update({
            "memory_usage": 82.0,
            "cpu_usage": 55.0,
            "response_time": 180.0
        })
        
        result = await decision_engine.analyze_metrics(sample_metrics, depth=AnalysisDepth.THOROUGH)
        
        assert result.analysis_depth == AnalysisDepth.THOROUGH
        assert result.decision_type in ["optimize", "caffeinate", "emergency_protocol"]
        assert len(result.historical_context) > 0
        assert result.pattern_confidence is not None
        decision_engine.db_integration.get_historical_performance.assert_called_once()

    @pytest.mark.asyncio
    async def test_shell_spin_detection_and_recording(self, decision_engine, sample_metrics):
        """Test shell spin incident detection and recording"""
        # Simulate shell spinning conditions
        sample_metrics.update({
            "memory_usage": 15.0,  # Very low - indicates spinning
            "cpu_usage": 95.0,     # Very high CPU
            "response_time": 2500.0  # Extremely slow
        })
        
        with patch.object(decision_engine, '_record_shell_spin') as mock_record:
            result = await decision_engine.analyze_metrics(sample_metrics, depth=AnalysisDepth.STANDARD)
        
        assert result.decision_type == "shell_spin_control"
        mock_record.assert_called_once()
        assert decision_engine._shell_spin_count == 1

    @pytest.mark.asyncio
    async def test_caffeine_level_management(self, decision_engine):
        """Test caffeine level updates and safety protocols"""
        initial_caffeine = decision_engine._current_caffeine
        
        # Test caffeine increase
        await decision_engine._update_caffeine_level(15)
        assert decision_engine._current_caffeine == initial_caffeine + 15
        
        # Test caffeine safety limit
        decision_engine._current_caffeine = 95
        await decision_engine._update_caffeine_level(10)
        assert decision_engine._current_caffeine <= 100  # Should be capped
        
        # Verify WebSocket notification
        decision_engine.websocket_handler.send_caffeine_update.assert_called()

    @pytest.mark.asyncio
    async def test_jitter_level_calculation(self, decision_engine, sample_metrics):
        """Test jitter level calculation based on system stress"""
        # High stress metrics should increase jitter
        high_stress_metrics = {
            "memory_usage": 92.0,
            "cpu_usage": 88.0,
            "response_time": 300.0,
            "error_rate": 0.05
        }
        
        initial_jitter = decision_engine._current_jitter
        jitter_increase = decision_engine._calculate_jitter_increase(high_stress_metrics)
        
        assert jitter_increase > 0
        assert jitter_increase <= 20  # Maximum reasonable increase
        
        # Low stress should decrease jitter
        low_stress_metrics = {
            "memory_usage": 25.0,
            "cpu_usage": 15.0,
            "response_time": 80.0,
            "error_rate": 0.001
        }
        
        jitter_change = decision_engine._calculate_jitter_increase(low_stress_metrics)
        assert jitter_change <= 0  # Should be negative (decrease)

    @pytest.mark.asyncio
    async def test_energy_drink_authorization(self, decision_engine):
        """Test emergency energy drink authorization protocols"""
        # Set up emergency conditions
        decision_engine._current_jitter = 95
        decision_engine._shell_spin_count = 4
        decision_engine._current_caffeine = 30  # Low caffeine, high jitter = emergency
        
        emergency_level = await decision_engine._calculate_energy_drink_needed()
        
        assert emergency_level == CaffeineEmergencyLevel.CRITICAL
        
        # Test authorization
        authorized = await decision_engine._authorize_energy_drink(emergency_level)
        assert authorized is True
        
        # Verify emergency protocols activated
        decision_engine.websocket_handler.send_emergency_alert.assert_called()

    @pytest.mark.asyncio
    async def test_decision_persistence(self, decision_engine, sample_metrics):
        """Test that decisions are properly stored in the database"""
        result = await decision_engine.analyze_metrics(sample_metrics, depth=AnalysisDepth.STANDARD)
        
        # Verify decision was stored
        decision_engine.db_integration.store_decision.assert_called_once()
        stored_call = decision_engine.db_integration.store_decision.call_args
        
        assert stored_call[0][0].agent_id == "meth_snail"
        assert stored_call[0][0].decision_type == result.decision_type
        assert stored_call[0][0].confidence == result.confidence

    @pytest.mark.asyncio
    async def test_concurrent_analysis_handling(self, decision_engine, sample_metrics):
        """Test handling of concurrent analysis requests"""
        # Start multiple analyses simultaneously
        tasks = []
        for i in range(5):
            modified_metrics = sample_metrics.copy()
            modified_metrics["memory_usage"] = 50 + i * 5
            
            task = asyncio.create_task(
                decision_engine.analyze_metrics(modified_metrics, depth=AnalysisDepth.BASIC)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 5
        for result in results:
            assert isinstance(result, DecisionResult)
            assert result.agent_id == "meth_snail"
        
        # Verify no race conditions in jitter/caffeine levels
        assert 0 <= decision_engine._current_jitter <= 100
        assert 0 <= decision_engine._current_caffeine <= 100

    @pytest.mark.asyncio
    async def test_error_handling_and_graceful_degradation(self, decision_engine, sample_metrics):
        """Test error handling when database or external services fail"""
        # Simulate database failure
        decision_engine.db_integration.get_recent_metrics = AsyncMock(side_effect=Exception("Database connection failed"))
        
        result = await decision_engine.analyze_metrics(sample_metrics, depth=AnalysisDepth.STANDARD)
        
        # Should gracefully degrade to basic analysis
        assert result is not None
        assert result.analysis_depth == AnalysisDepth.BASIC
        assert "degraded mode" in " ".join(result.recommendations).lower()
        assert result.confidence < 0.7  # Lower confidence due to degradation

    @pytest.mark.asyncio
    async def test_adaptive_thresholds(self, decision_engine, historical_data):
        """Test adaptive threshold adjustment based on historical patterns"""
        # Mock historical data showing higher baseline memory usage
        high_baseline_data = [entry for entry in historical_data]
        for entry in high_baseline_data:
            entry.data["memory_usage"] = entry.data["memory_usage"] + 20
        
        decision_engine.db_integration.get_historical_performance = AsyncMock(return_value=high_baseline_data)
        
        await decision_engine._adapt_thresholds()
        
        # Thresholds should adjust upward
        assert decision_engine._adaptive_memory_threshold > decision_engine._base_memory_threshold
        decision_engine.db_integration.get_historical_performance.assert_called_once()