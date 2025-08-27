"""
Test Suite for Meth Snail Decision Engine + Database Integration
Comprehensive testing of the refactored components working together.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
import json

# Import the components we're testing
from app.ai_agents.meth_snail.decision_engine import (
    MethSnailBrainV2,
    OptimizationDecision,
    OptimizationPriority,
    AnalysisDepth,
    # ShellSpinIncidents,
    # meth_snail_brain
)
from app.ai_agents.meth_snail.database_integration import MethSnailDatabaseIntegration
from app.ai_agents.meth_snail.data_types import EnergyDrinkType


@pytest.fixture
async def mock_session():
    """Create a mock database session"""
    session = AsyncMock()
    session.execute.return_value.scalars.return_value.all.return_value = []
    session.execute.return_value.scalars.return_value.first.return_value = None
    session.execute.return_value.scalar.return_value = 0
    return session


@pytest.fixture
async def mock_session_factory(mock_session):
    """Create a mock session factory"""
    async def session_factory():
        yield mock_session
    return session_factory


@pytest.fixture
async def db_integration(mock_session_factory):
    """Create database integration with mock session factory"""
    return MethSnailDatabaseIntegration(mock_session_factory)


@pytest.fixture
async def decision_engine(mock_session_factory):
    """Create decision engine with mock database"""
    return MethSnailBrainV2(mock_session_factory)


@pytest.fixture
def valid_metrics():
    """Valid system metrics for testing"""
    return {
        'cpu_usage': 75.5,
        'memory_usage': 80.2,
        'disk_usage': 60.0,
        'network': {
            'sent_rate': 1024,
            'recv_rate': 2048
        },
        'process_count': 150
    }


@pytest.fixture
def invalid_metrics():
    """Invalid system metrics for testing shell spinning"""
    return {
        'cpu_usage': None,  # Missing critical metric
        'memory_usage': 150.0,  # Invalid range
        'disk_usage': -10.0,  # Invalid range
    }


class TestMethSnailDatabaseIntegration:
    """Test database integration methods"""

    @pytest.mark.asyncio
    async def test_store_optimization_metrics_success(self, db_integration, mock_session):
        """Test successful metrics storage"""
        # Mock the log_agent_event_async function
        with patch('app.agents.meth_snail.database_integration.log_agent_event_async') as mock_log:
            mock_record = MagicMock()
            mock_record.memory_id = 12345
            mock_log.return_value = mock_record

            metrics_data = {
                'cpu_usage_before': 80.0,
                'memory_usage_before': 75.0,
                'shell_spin_count': 0,
                'data_quality_score': 0.9
            }

            result = await db_integration.store_optimization_metrics("user_123", metrics_data)

            assert result == 12345
            mock_log.assert_called_once_with(
                mock_session,
                agent_name="meth_snail",
                event_type="optimization_metrics",
                user_id="user_123",
                details=metrics_data,
                metadata={
                    "source": "meth_snail_optimization_engine",
                    "schema": "central_memory_bank.v1",
                    "data_quality_score": 0.9,
                    "shell_spin_count": 0
                }
            )

    @pytest.mark.asyncio
    async def test_get_historical_performance_no_data(self, db_integration, mock_session):
        """Test historical performance with no data"""
        # Mock empty result
        mock_session.execute.return_value.scalars.return_value.all.return_value = []

        result = await db_integration.get_historical_performance("user_123", days=7)

        assert result["status"] == "no_data"
        assert result["message"] == "No historical data yet"
        assert result["data"] == []

    @pytest.mark.asyncio
    async def test_get_historical_performance_with_data(self, db_integration, mock_session):
        """Test historical performance with actual data"""
        # Mock database record
        mock_record = MagicMock()
        mock_record.occurred_at = datetime.now(timezone.utc)
        mock_record.details = {
            'cpu_usage_before': 85.0,
            'cpu_usage_after': 70.0,
            'memory_usage_before': 90.0,
            'memory_usage_after': 75.0,
            'optimization_success': True,
            'shell_spin_count': 1,
            'confidence_level': 0.8
        }
        mock_record.event_type = "optimization_decision"

        mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_record]

        result = await db_integration.get_historical_performance("user_123", days=7)

        assert result["status"] == "success"
        assert len(result["data"]) == 1
        
        record = result["data"][0]
        assert record["cpu_improvement"] == 15.0  # 85 - 70
        assert record["memory_improvement"] == 15.0  # 90 - 75
        assert record["optimization_success"] is True
        assert record["shell_spin_count"] == 1

    @pytest.mark.asyncio
    async def test_store_decision_success(self, db_integration, mock_session):
        """Test successful decision storage"""
        with patch('app.agents.meth_snail.database_integration.log_agent_event_async') as mock_log:
            mock_record = MagicMock()
            mock_record.memory_id = 67890
            mock_log.return_value = mock_record

            decision_data = {
                "decision_type": "optimization",
                "context": "Memory usage high",
                "confidence_level": 0.85,
                "optimization_applied": True,
                "shell_spinning_triggered": False,
                "result": {
                    "actions": [{"type": "memory_cleanup"}],
                    "urgency": "soon",
                    "priority": "efficiency"
                }
            }

            result = await db_integration.store_decision("user_123", decision_data)

            assert result == 67890
            mock_log.assert_called_once_with(
                mock_session,
                agent_name="meth_snail",
                event_type="optimization_decision",
                user_id="user_123",
                details=decision_data["result"],
                metadata={
                    "decision_type": "optimization",
                    "context": "Memory usage high",
                    "confidence_level": 0.85,
                    "optimization_applied": True,
                    "shell_spinning_triggered": False,
                    "actions_count": 1,
                    "urgency": "soon",
                    "priority": "efficiency"
                }
            )

    @pytest.mark.asyncio
    async def test_jitter_level_methods(self, db_integration, mock_session):
        """Test jitter level storage and retrieval"""
        with patch('app.agents.meth_snail.database_integration.log_agent_event_async') as mock_log:
            mock_record = MagicMock()
            mock_record.memory_id = 11111
            mock_log.return_value = mock_record

            jitter_data = {
                "current_jitter_level": 0.6,
                "caffeine_level_mg": 150.0,
                "jitter_trend": "increasing"
            }

            # Test storage
            result = await db_integration.update_jitter_levels("user_123", jitter_data)
            assert result == 11111

            # Test retrieval with data
            mock_db_record = MagicMock()
            mock_db_record.details = jitter_data
            mock_db_record.occurred_at = datetime.now(timezone.utc)
            mock_session.execute.return_value.scalars.return_value.first.return_value = mock_db_record

            result = await db_integration.get_recent_jitter_levels("user_123")
            
            assert result["status"] == "success"
            assert result["current_jitter"] == 0.6
            assert result["caffeine_level_mg"] == 150.0
            assert result["jitter_trend"] == "increasing"


class TestMethSnailDecisionEngine:
    """Test decision engine functionality"""

    @pytest.mark.asyncio
    async def test_analyze_metrics_success(self, decision_engine, valid_metrics):
        """Test successful metrics analysis"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.store_optimization_metrics.return_value = 12345
            mock_db.get_historical_performance.return_value = {'status': 'no_data', 'data': []}
            mock_db.store_decision.return_value = 67890
            
            result = await decision_engine.analyze_metrics(
                valid_metrics, 
                user_id="user_123",
                analysis_depth=AnalysisDepth.STANDARD
            )

            assert result is not None
            assert isinstance(result, OptimizationDecision)
            assert result.analysis_depth == AnalysisDepth.STANDARD
            assert result.data_quality_score > 0.5  # Should have good quality score
            assert result.shell_spin_count == 0  # No shell spins for valid data

    @pytest.mark.asyncio
    async def test_analyze_metrics_shell_spinning(self, decision_engine, invalid_metrics):
        """Test metrics analysis with invalid data causes shell spinning"""
        with patch.object(decision_engine, '_record_shell_spin') as mock_shell_spin:
            result = await decision_engine.analyze_metrics(
                invalid_metrics,
                user_id="user_123"
            )

            assert result is None  # Should return None for invalid data
            mock_shell_spin.assert_called()  # Should record shell spin

    @pytest.mark.asyncio
    async def test_basic_analysis_logic(self, decision_engine):
        """Test basic analysis decision logic"""
        # High memory usage should trigger optimization
        decision = await decision_engine._basic_analysis(
            cpu_usage=70.0,
            memory_usage=90.0,
            disk_usage=50.0,
            shell_spin_count=0,
            data_quality_score=0.8
        )

        assert decision.priority == OptimizationPriority.BALANCED
        assert len(decision.actions) > 0
        assert any("memory" in action.get("type", "") for action in decision.actions)
        assert decision.confidence > 0.6

    @pytest.mark.asyncio
    async def test_standard_analysis_logic(self, decision_engine):
        """Test standard analysis decision logic"""
        decision = await decision_engine._standard_analysis(
            cpu_usage=90.0,  # High CPU
            memory_usage=85.0,  # High memory
            disk_usage=70.0,
            network_data={'sent_rate': 1000, 'recv_rate': 2000, 'valid': True},
            process_count=200,
            shell_spin_count=0,
            data_quality_score=0.9
        )

        assert decision.priority == OptimizationPriority.SPEED  # CPU priority
        assert len(decision.actions) >= 1  # Should have CPU and/or memory actions
        assert decision.confidence > 0.8  # High confidence for clear issues
        assert decision.urgency == "immediate"  # High urgency for multiple issues

    @pytest.mark.asyncio
    async def test_thorough_analysis_with_historical(self, decision_engine):
        """Test thorough analysis with historical data"""
        historical_data = [
            {'memory_usage': 60.0, 'timestamp': datetime.now() - timedelta(hours=1)},
            {'memory_usage': 65.0, 'timestamp': datetime.now() - timedelta(hours=2)},
            {'memory_usage': 70.0, 'timestamp': datetime.now() - timedelta(hours=3)},
        ]

        decision = await decision_engine._thorough_analysis(
            cpu_usage=75.0,
            memory_usage=85.0,  # 30% above average (65%)
            disk_usage=90.0,  # High disk
            network_data={'sent_rate': 1000, 'recv_rate': 2000, 'valid': True},
            process_count=150,
            historical_data=historical_data,
            shell_spin_count=0,
            data_quality_score=0.95
        )

        assert decision.priority == OptimizationPriority.AGGRESSIVE  # Disk critical
        assert len(decision.actions) >= 1
        assert any("trend" in action.get("type", "") for action in decision.actions)  # Historical analysis
        assert any("disk" in action.get("type", "") for action in decision.actions)  # Disk cleanup
        assert decision.confidence > 0.8

    @pytest.mark.asyncio
    async def test_jitter_level_updates(self, decision_engine):
        """Test jitter level calculation and updates"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.update_jitter_levels.return_value = 11111

            # Test caffeine increase
            initial_jitter = decision_engine._current_jitter
            new_jitter = await decision_engine.update_jitter_levels(caffeine_change=100.0)

            assert new_jitter > initial_jitter  # Should increase with caffeine
            assert decision_engine._caffeine_level > 0  # Should have caffeine
            
            # Verify database storage was called
            mock_db.update_jitter_levels.assert_called()

    @pytest.mark.asyncio
    async def test_energy_drink_authorization(self, decision_engine):
        """Test energy drink authorization flow"""
        with patch.object(decision_engine, '_calculate_current_jitter_level') as mock_jitter:
            with patch.object(decision_engine, 'db_integration') as mock_db:
                mock_jitter.return_value = 0.3  # Safe jitter level
                mock_db.get_energy_drink_consumption.return_value = {
                    'status': 'success', 'total_consumed': 100.0
                }

                with patch.object(decision_engine, '_get_time_since_last_drink') as mock_time:
                    mock_time.return_value = 60  # 1 hour since last drink

                    authorization = await decision_engine.request_energy_drink_authorization(
                        user_id="user_123",
                        energy_drink_type=EnergyDrinkType.COFFEE,
                        caffeine_mg=95.0,
                        consumption_reason="optimization_session"
                    )

                    assert authorization.authorized is True  # Should be authorized
                    assert authorization.recommended_caffeine_mg <= 200.0  # Capped
                    assert "authorized" in authorization.authorization_notes.lower()


class TestIntegrationBetweenComponents:
    """Test decision engine and database integration working together"""

    @pytest.mark.asyncio
    async def test_full_analysis_with_database_storage(self, decision_engine, valid_metrics):
        """Test complete analysis flow with database storage"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.store_optimization_metrics.return_value = 12345
            mock_db.get_historical_performance.return_value = {
                'status': 'success', 'data': []
            }
            mock_db.store_decision.return_value = 67890

            result = await decision_engine.analyze_metrics(
                valid_metrics,
                user_id="user_123",
                analysis_depth=AnalysisDepth.STANDARD
            )

            # Verify result
            assert result is not None
            assert isinstance(result, OptimizationDecision)
            
            # Verify database calls were made
            mock_db.store_optimization_metrics.assert_called_once()
            mock_db.store_decision.assert_called_once()
            
            # Verify data was stored correctly
            store_call = mock_db.store_optimization_metrics.call_args
            assert store_call[0][0] == "user_123"  # user_id
            assert "cpu_usage_before" in store_call[0][1]  # metrics data
            
            decision_call = mock_db.store_decision.call_args
            assert decision_call[0][0] == "user_123"  # user_id
            assert "confidence_level" in decision_call[0][1]  # decision data

    @pytest.mark.asyncio
    async def test_shell_spin_recording_integration(self, decision_engine):
        """Test shell spin incident recording"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.record_shell_spin_incident.return_value = 99999

            # Trigger shell spin with invalid data
            invalid_metrics = {'cpu_usage': None, 'memory_usage': None, 'disk_usage': None}
            
            result = await decision_engine.analyze_metrics(
                invalid_metrics,
                user_id="user_123"
            )

            assert result is None  # Analysis should fail
            
            # Verify shell spin was recorded
            mock_db.record_shell_spin_incident.assert_called()
            
            # Check shell spin data
            call_args = mock_db.record_shell_spin_incident.call_args
            incident_data = call_args[0][1]  # Second argument is incident data
            assert len(incident_data["missing_metrics"]) > 0
            assert "cpu_usage" in incident_data["missing_metrics"]

    @pytest.mark.asyncio
    async def test_cross_agent_learning_integration(self, db_integration, mock_session):
        """Test cross-agent learning data retrieval"""
        # Mock successful pattern from another agent
        mock_record = MagicMock()
        mock_record.agent_name = "hamsters"
        mock_record.event_type = "disk_optimization"
        mock_record.occurred_at = datetime.now(timezone.utc)
        mock_record.details = {
            "disk_usage_before": 90.0,
            "disk_usage_after": 70.0,
            "optimization_success": True,
            "technique": "duct_tape_cleanup"
        }
        mock_record.metadata = {
            "success_rate": 0.95,
            "confidence_level": 0.9,
            "agent_personality": "redneck_engineer"
        }
        
        mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_record]
        
        patterns = await db_integration.get_cross_agent_patterns(
            user_id="user_123",
            event_types=["disk_optimization", "memory_optimization"],
            min_success_rate=0.8,
            days_back=30
        )
        
        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern["agent_type"] == "hamsters"
        assert pattern["event_type"] == "disk_optimization"
        assert pattern["success_indicators"]["success_rate"] == 0.95
        assert pattern["event_data"]["technique"] == "duct_tape_cleanup"

    @pytest.mark.asyncio
    async def test_database_error_handling(self, decision_engine, valid_metrics):
        """Test graceful handling of database errors"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            # Simulate database connection error
            mock_db.store_optimization_metrics.side_effect = Exception("Database connection failed")
            
            # Analysis should still complete despite database error
            result = await decision_engine.analyze_metrics(
                valid_metrics,
                user_id="user_123"
            )
            
            assert result is not None  # Should still return a decision
            assert isinstance(result, OptimizationDecision)
            # Database error should be logged but not crash the analysis

    @pytest.mark.asyncio
    async def test_multiple_analysis_depths_integration(self, decision_engine, valid_metrics):
        """Test all analysis depths with database integration"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.store_optimization_metrics.return_value = 12345
            mock_db.store_decision.return_value = 67890
            mock_db.get_historical_performance.return_value = {'status': 'success', 'data': []}
            
            # Test each analysis depth
            for depth in [AnalysisDepth.BASIC, AnalysisDepth.STANDARD, AnalysisDepth.THOROUGH]:
                result = await decision_engine.analyze_metrics(
                    valid_metrics,
                    user_id="user_123",
                    analysis_depth=depth
                )
                
                assert result is not None
                assert result.analysis_depth == depth
                
                # Thorough analysis should have higher confidence
                if depth == AnalysisDepth.THOROUGH:
                    assert result.confidence >= 0.7
                elif depth == AnalysisDepth.BASIC:
                    assert result.confidence >= 0.5

    @pytest.mark.asyncio
    async def test_concurrent_analyses(self, decision_engine, valid_metrics):
        """Test concurrent analysis requests"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.store_optimization_metrics.return_value = 12345
            mock_db.store_decision.return_value = 67890
            mock_db.get_historical_performance.return_value = {'status': 'success', 'data': []}
            
            # Run multiple concurrent analyses
            tasks = []
            for i in range(5):
                task = decision_engine.analyze_metrics(
                    valid_metrics,
                    user_id=f"user_{i}",
                    analysis_depth=AnalysisDepth.STANDARD
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # All analyses should complete successfully
            assert len(results) == 5
            for result in results:
                assert result is not None
                assert isinstance(result, OptimizationDecision)
            
            # Verify database calls were made for each analysis
            assert mock_db.store_optimization_metrics.call_count == 5
            assert mock_db.store_decision.call_count == 5


class TestRealTimeScenarios:
    """Test realistic system monitoring scenarios"""

    @pytest.mark.asyncio
    async def test_memory_spike_scenario(self, decision_engine):
        """Test handling of sudden memory spike"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.store_optimization_metrics.return_value = 12345
            mock_db.store_decision.return_value = 67890
            mock_db.get_historical_performance.return_value = {
                'status': 'success', 
                'data': [
                    {'memory_usage': 60.0, 'timestamp': datetime.now() - timedelta(minutes=1)},
                    {'memory_usage': 62.0, 'timestamp': datetime.now() - timedelta(minutes=2)},
                ]
            }
            
            # Sudden memory spike scenario
            spike_metrics = {
                'cpu_usage': 45.0,
                'memory_usage': 95.0,  # Sudden spike from ~60% to 95%
                'disk_usage': 55.0,
                'process_count': 180
            }
            
            result = await decision_engine.analyze_metrics(
                spike_metrics,
                user_id="user_123",
                analysis_depth=AnalysisDepth.THOROUGH
            )
            
            assert result is not None
            assert result.urgency == "immediate"  # High urgency for spike
            assert any("memory" in action.get("type", "") for action in result.actions)
            assert result.confidence > 0.8  # High confidence in memory issue

    @pytest.mark.asyncio
    async def test_degrading_system_scenario(self, decision_engine):
        """Test gradual system degradation detection"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.store_optimization_metrics.return_value = 12345
            mock_db.store_decision.return_value = 67890
            
            # Simulate gradual degradation with historical data
            historical_data = [
                {'cpu_usage': 50.0, 'memory_usage': 60.0, 'timestamp': datetime.now() - timedelta(hours=6)},
                {'cpu_usage': 55.0, 'memory_usage': 65.0, 'timestamp': datetime.now() - timedelta(hours=4)},
                {'cpu_usage': 60.0, 'memory_usage': 70.0, 'timestamp': datetime.now() - timedelta(hours=2)},
                {'cpu_usage': 65.0, 'memory_usage': 75.0, 'timestamp': datetime.now() - timedelta(hours=1)},
            ]
            
            mock_db.get_historical_performance.return_value = {'status': 'success', 'data': historical_data}
            
            current_metrics = {
                'cpu_usage': 70.0,  # Continuing upward trend
                'memory_usage': 80.0,  # Continuing upward trend
                'disk_usage': 65.0,
                'process_count': 200
            }
            
            result = await decision_engine.analyze_metrics(
                current_metrics,
                user_id="user_123",
                analysis_depth=AnalysisDepth.THOROUGH,
                historical_data=historical_data
            )
            
            assert result is not None
            assert len(result.actions) > 0  # Should recommend optimizations
            assert any("trend" in action.get("type", "") for action in result.actions)  # Should detect trend

    @pytest.mark.asyncio
    async def test_caffeine_emergency_scenario(self, decision_engine):
        """Test high caffeine emergency scenario"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            with patch.object(decision_engine, '_calculate_current_jitter_level') as mock_jitter:
                mock_jitter.return_value = 0.9  # CRITICAL jitter level
                mock_db.get_energy_drink_consumption.return_value = {
                    'status': 'success', 'total_consumed': 600.0  # Very high consumption
                }
                
                with patch.object(decision_engine, '_get_time_since_last_drink') as mock_time:
                    mock_time.return_value = 15  # Recent consumption
                    
                    authorization = await decision_engine.request_energy_drink_authorization(
                        user_id="user_123",
                        energy_drink_type=EnergyDrinkType.ENERGY_DRINK,
                        caffeine_mg=200.0,
                        consumption_reason="emergency_optimization"
                    )
                    
                    assert authorization.authorized is False  # Should be denied
                    assert len(authorization.safety_warnings) > 0
                    assert any("jitter" in warning.lower() for warning in authorization.safety_warnings)

    @pytest.mark.asyncio
    async def test_data_quality_degradation_scenario(self, decision_engine):
        """Test handling of progressively degrading data quality"""
        scenarios = [
            # Good data
            {'cpu_usage': 70.0, 'memory_usage': 75.0, 'disk_usage': 60.0, 'expected_quality': 0.6},
            # Missing network data
            {'cpu_usage': 70.0, 'memory_usage': 75.0, 'disk_usage': 60.0, 'expected_quality': 0.4},
            # Invalid range data - should cause shell spin
            {'cpu_usage': 150.0, 'memory_usage': 75.0, 'disk_usage': 60.0, 'expected_result': None},
            # Missing critical data - should cause shell spin
            {'cpu_usage': None, 'memory_usage': 75.0, 'disk_usage': 60.0, 'expected_result': None},
        ]
        
        for i, scenario in enumerate(scenarios):
            with patch.object(decision_engine, 'db_integration') as mock_db:
                mock_db.store_optimization_metrics.return_value = 12345
                mock_db.store_decision.return_value = 67890
                mock_db.record_shell_spin_incident.return_value = 99999
                
                result = await decision_engine.analyze_metrics(
                    scenario,
                    user_id=f"user_{i}",
                    analysis_depth=AnalysisDepth.STANDARD
                )
                
                if 'expected_result' in scenario and scenario['expected_result'] is None:
                    assert result is None  # Should fail for invalid data
                    mock_db.record_shell_spin_incident.assert_called()
                else:
                    assert result is not None
                    if 'expected_quality' in scenario:
                        # Check data quality is approximately correct
                        assert abs(result.data_quality_score - scenario['expected_quality']) < 0.2


class TestPerformanceAndReliability:
    """Test performance and reliability aspects"""

    @pytest.mark.asyncio
    async def test_large_historical_data_handling(self, decision_engine):
        """Test handling of large amounts of historical data"""
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.store_optimization_metrics.return_value = 12345
            mock_db.store_decision.return_value = 67890
            
            # Create large historical dataset (simulate 100 data points)
            large_historical_data = []
            for i in range(100):
                large_historical_data.append({
                    'cpu_usage': 50 + (i * 0.3),  # Gradual increase
                    'memory_usage': 60 + (i * 0.2),
                    'timestamp': datetime.now() - timedelta(minutes=i)
                })
            
            mock_db.get_historical_performance.return_value = {
                'status': 'success', 'data': large_historical_data
            }
            
            start_time = datetime.now()
            
            result = await decision_engine.analyze_metrics(
                {'cpu_usage': 80.0, 'memory_usage': 80.0, 'disk_usage': 70.0},
                user_id="user_123",
                analysis_depth=AnalysisDepth.THOROUGH,
                historical_data=large_historical_data
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            assert result is not None
            assert processing_time < 5.0  # Should complete within 5 seconds
            assert result.confidence > 0.7  # Should have good confidence with lots of data

    @pytest.mark.asyncio
    async def test_memory_usage_tracking(self, decision_engine):
        """Test that the decision engine doesn't leak memory"""
        import gc
        import sys
        
        with patch.object(decision_engine, 'db_integration') as mock_db:
            mock_db.store_optimization_metrics.return_value = 12345
            mock_db.store_decision.return_value = 67890
            mock_db.get_historical_performance.return_value = {'status': 'success', 'data': []}
            
            # Record initial memory usage
            gc.collect()
            initial_objects = len(gc.get_objects())
            
            # Run many analyses
            for i in range(50):
                await decision_engine.analyze_metrics(
                    {'cpu_usage': 70.0, 'memory_usage': 75.0, 'disk_usage': 60.0},
                    user_id=f"user_{i}",
                    analysis_depth=AnalysisDepth.STANDARD
                )
            
            # Check memory usage after
            gc.collect()
            final_objects = len(gc.get_objects())
            
            # Should not have significantly increased object count
            object_growth = final_objects - initial_objects
            assert object_growth < 1000  # Reasonable threshold for object growth

    @pytest.mark.asyncio
    async def test_decision_engine_state_isolation(self, mock_session_factory):
        """Test that multiple decision engine instances don't interfere"""
        engine1 = MethSnailBrainV2(mock_session_factory)
        engine2 = MethSnailBrainV2(mock_session_factory)
        
        # Modify state in engine1
        engine1._caffeine_level = 200.0
        engine1._current_jitter = 0.7
        
        # Engine2 should have independent state
        assert engine2._caffeine_level != 200.0
        assert engine2._current_jitter != 0.7
        
        # Both should be able to analyze independently
        with patch.object(engine1, 'db_integration'), patch.object(engine2, 'db_integration'):
            result1 = await engine1.analyze_metrics(
                {'cpu_usage': 70.0, 'memory_usage': 75.0, 'disk_usage': 60.0},
                user_id="user_1"
            )
            result2 = await engine2.analyze_metrics(
                {'cpu_usage': 80.0, 'memory_usage': 85.0, 'disk_usage': 70.0},
                user_id="user_2"
            )
            
            assert result1 is not None
            assert result2 is not None
            # Results should be independent
            assert result1.timestamp != result2.timestamp


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])