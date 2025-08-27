# test_meth_snail_database_integration.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from sqlalchemy import select

from app.ai_agents.meth_snail.database_integration import MethSnailDBIntegration
from agent_memory_banks import AgentMemoryEntry

class TestMethSnailDatabaseIntegration:
    
    @pytest.mark.asyncio
    async def test_store_decision_success(self, db_integration, mock_async_session):
        """Test successful decision storage"""
        from app.ai_agents.meth_snail.decision_engine import DecisionResult
        
        decision = DecisionResult(
            agent_id="meth_snail",
            decision_type="optimize",
            confidence=0.85,
            recommendations=["Increase cache size", "Clear memory buffers"],
            metrics_analyzed={"memory_usage": 78.5},
            analysis_depth="standard"
        )
        
        await db_integration.store_decision(decision)
        
        # Verify session operations
        mock_async_session.add.assert_called_once()
        mock_async_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recent_metrics(self, db_integration, mock_async_session):
        """Test retrieval of recent metrics for trend analysis"""
        # Mock database results
        mock_results = [
            MagicMock(data={
                "memory_usage": 65.0,
                "cpu_usage": 45.0,
                "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat()
            }),
            MagicMock(data={
                "memory_usage": 70.0,
                "cpu_usage": 50.0,
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
            })
        ]
        
        mock_async_session.scalars.return_value.all.return_value = mock_results
        
        results = await db_integration.get_recent_metrics(minutes=15)
        
        assert len(results) == 2
        assert results[0]["memory_usage"] == 65.0
        assert results[1]["memory_usage"] == 70.0
        mock_async_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_historical_performance(self, db_integration, mock_async_session, historical_data):
        """Test historical performance data retrieval"""
        mock_async_session.scalars.return_value.all.return_value = historical_data[:50]  # Return subset
        
        results = await db_integration.get_historical_performance(hours=24)
        
        assert len(results) == 50
        assert all(entry.agent_id == "meth_snail" for entry in results)
        mock_async_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_shell_spin_incident(self, db_integration, mock_async_session):
        """Test shell spin incident recording"""
        incident_data = {
            "memory_usage": 12.5,
            "cpu_usage": 98.2,
            "response_time": 3500.0,
            "shell_spin_duration": 45.7,
            "recovery_actions": ["force_gc", "restart_service"]
        }
        
        await db_integration.store_shell_spin_incident(incident_data)
        
        mock_async_session.add.assert_called_once()
        mock_async_session.commit.assert_called_once()
        
        # Verify the stored entry has correct type
        stored_entry = mock_async_session.add.call_args[0][0]
        assert stored_entry.entry_type == "shell_spin_incident"
        assert stored_entry.agent_id == "meth_snail"

    @pytest.mark.asyncio
    async def test_update_jitter_level(self, db_integration, mock_async_session):
        """Test jitter level updates in database"""
        new_jitter = 67.5
        
        await db_integration.update_jitter_level(new_jitter)
        
        mock_async_session.add.assert_called_once()
        mock_async_session.commit.assert_called_once()
        
        stored_entry = mock_async_session.add.call_args[0][0]
        assert stored_entry.data["jitter_level"] == new_jitter
        assert stored_entry.entry_type == "jitter_update"

    @pytest.mark.asyncio
    async def test_get_optimization_metrics(self, db_integration, mock_async_session):
        """Test optimization metrics retrieval"""
        mock_results = [
            MagicMock(data={
                "optimization_type": "memory_cleanup",
                "before_memory": 85.0,
                "after_memory": 62.0,
                "improvement": 23.0,
                "timestamp": datetime.utcnow().isoformat()
            }),
            MagicMock(data={
                "optimization_type": "cache_optimization",
                "cache_hit_ratio_before": 0.65,
                "cache_hit_ratio_after": 0.89,
                "improvement": 0.24,
                "timestamp": datetime.utcnow().isoformat()
            })
        ]
        
        mock_async_session.scalars.return_value.all.return_value = mock_results
        
        metrics = await db_integration.get_optimization_metrics(limit=10)
        
        assert len(metrics) == 2
        assert metrics[0]["optimization_type"] == "memory_cleanup"
        assert metrics[1]["optimization_type"] == "cache_optimization"

    @pytest.mark.asyncio
    async def test_cross_agent_learning_storage(self, db_integration, central_memory_bank):
        """Test cross-agent learning data storage"""
        learning_data = {
            "source_agent": "meth_snail",
            "target_agent": "sir_hawkington",
            "insight_type": "memory_pattern",
            "confidence": 0.78,
            "data": {
                "pattern": "memory_spike_before_cpu_surge",
                "correlation": 0.85,
                "recommendation": "preemptive_memory_cleanup"
            }
        }
        
        await db_integration.store_cross_agent_insight(learning_data)
        
        central_memory_bank.store_entry.assert_called_once()
        stored_call = central_memory_bank.store_entry.call_args[0][0]
        assert stored_call.entry_type == "cross_agent_insight"
        assert stored_call.data["source_agent"] == "meth_snail"

    @pytest.mark.asyncio
    async def test_database_error_handling(self, db_integration, mock_async_session):
        """Test database error handling and recovery"""
        # Simulate database error
        mock_async_session.commit.side_effect = Exception("Database connection lost")
        
        from app.ai_agents.meth_snail.decision_engine import DecisionResult
        decision = DecisionResult(
            agent_id="meth_snail",
            decision_type="optimize",
            confidence=0.85,
            recommendations=["Test recommendation"],
            metrics_analyzed={"memory_usage": 78.5}
        )
        
        # Should not raise exception, should handle gracefully
        try:
            await db_integration.store_decision(decision)
        except Exception:
            pytest.fail("Database error was not handled gracefully")
        
        # Verify rollback was called
        mock_async_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_management(self, db_integration, mock_session_factory, mock_async_session):
        """Test proper session lifecycle management"""
        await db_integration.store_optimization_metric("test_metric", {"value": 42})
        
        # Verify session was properly opened and closed
        mock_session_factory.assert_called_once()
        mock_async_session.__aenter__.assert_called_once()
        mock_async_session.__aexit__.assert_called_once()