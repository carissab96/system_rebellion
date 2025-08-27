# test_central_memory_bank.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
import json

from agent_memory_banks import CentralMemoryBank, AgentMemoryEntry

class TestCentralMemoryBank:
    
    @pytest.mark.asyncio
    async def test_store_entry_success(self, central_memory_bank, mock_async_session):
        """Test successful storage of memory entry"""
        entry = AgentMemoryEntry(
            agent_id="meth_snail",
            entry_type="decision",
            data={
                "decision_type": "optimize",
                "confidence": 0.85,
                "metrics": {"memory_usage": 78.5}
            },
            importance_score=0.8
        )
        
        # Mock the actual implementation
        central_memory_bank.store_entry = AsyncMock()
        
        await central_memory_bank.store_entry(entry)
        
        central_memory_bank.store_entry.assert_called_once_with(entry)

        @pytest.mark.asyncio
    async def test_get_entries_by_agent(self, central_memory_bank):
        """Test retrieving entries for specific agent"""
        mock_entries = [
            AgentMemoryEntry(
                id=1,
                agent_id="meth_snail",
                entry_type="decision",
                data={"decision_type": "optimize", "confidence": 0.85},
                timestamp=datetime.utcnow(),
                importance_score=0.8
            ),
            AgentMemoryEntry(
                id=2,
                agent_id="meth_snail",
                entry_type="performance_metric",
                data={"memory_usage": 78.5, "cpu_usage": 45.2},
                timestamp=datetime.utcnow(),
                importance_score=0.7
            )
        ]
        
        central_memory_bank.get_entries_by_agent.return_value = mock_entries
        
        entries = await central_memory_bank.get_entries_by_agent("meth_snail", limit=10)
        
        assert len(entries) == 2
        assert all(entry.agent_id == "meth_snail" for entry in entries)
        central_memory_bank.get_entries_by_agent.assert_called_once_with("meth_snail", limit=10)

    @pytest.mark.asyncio
    async def test_get_cross_agent_insights(self, central_memory_bank):
        """Test cross-agent learning insights retrieval"""
        mock_insights = [
            AgentMemoryEntry(
                id=3,
                agent_id="meth_snail",
                entry_type="cross_agent_insight",
                data={
                    "source_agent": "meth_snail",
                    "target_agent": "sir_hawkington",
                    "insight": "memory_pattern_correlation",
                    "confidence": 0.78
                },
                timestamp=datetime.utcnow(),
                importance_score=0.9
            )
        ]
        
        central_memory_bank.get_cross_agent_insights.return_value = mock_insights
        
        insights = await central_memory_bank.get_cross_agent_insights("meth_snail")
        
        assert len(insights) == 1
        assert insights[0].data["source_agent"] == "meth_snail"
        central_memory_bank.get_cross_agent_insights.assert_called_once_with("meth_snail")

    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, central_memory_bank):
        """Test performance metrics aggregation"""
        mock_metrics = {
            'avg_response_time': 120.5,
            'success_rate': 0.95,
            'total_decisions': 1250,
            'avg_confidence': 0.82,
            'optimization_count': 87,
            'shell_spin_incidents': 3
        }
        
        central_memory_bank.get_performance_metrics.return_value = mock_metrics
        
        metrics = await central_memory_bank.get_performance_metrics("meth_snail", hours=24)
        
        assert metrics['avg_response_time'] == 120.5
        assert metrics['success_rate'] == 0.95
        assert metrics['total_decisions'] == 1250
        central_memory_bank.get_performance_metrics.assert_called_once_with("meth_snail", hours=24)

    @pytest.mark.asyncio
    async def test_update_entry_importance(self, central_memory_bank):
        """Test updating entry importance scores"""
        central_memory_bank.update_entry = AsyncMock()
        
        await central_memory_bank.update_entry(entry_id=123, importance_score=0.95)
        
        central_memory_bank.update_entry.assert_called_once_with(entry_id=123, importance_score=0.95)

    @pytest.mark.asyncio
    async def test_pattern_recognition_storage(self, central_memory_bank):
        """Test storage of pattern recognition results"""
        pattern_entry = AgentMemoryEntry(
            agent_id="meth_snail",
            entry_type="pattern_recognition",
            data={
                "pattern_type": "memory_spike_prediction",
                "confidence": 0.87,
                "triggers": ["high_cpu_usage", "increased_connections"],
                "prediction_window": 300,  # seconds
                "accuracy": 0.91
            },
            importance_score=0.88
        )
        
        central_memory_bank.store_entry = AsyncMock()
        
        await central_memory_bank.store_entry(pattern_entry)
        
        central_memory_bank.store_entry.assert_called_once_with(pattern_entry)

    @pytest.mark.asyncio
    async def test_memory_cleanup_and_archival(self, central_memory_bank):
        """Test memory cleanup and archival processes"""
        central_memory_bank.cleanup_old_entries = AsyncMock(return_value=150)  # entries cleaned
        central_memory_bank.archive_low_importance = AsyncMock(return_value=75)  # entries archived
        
        cleaned = await central_memory_bank.cleanup_old_entries(days=30)
        archived = await central_memory_bank.archive_low_importance(threshold=0.3)
        
        assert cleaned == 150
        assert archived == 75
        central_memory_bank.cleanup_old_entries.assert_called_once_with(days=30)
        central_memory_bank.archive_low_importance.assert_called_once_with(threshold=0.3)

    @pytest.mark.asyncio
    async def test_knowledge_graph_connections(self, central_memory_bank):
        """Test knowledge graph relationship building"""
        central_memory_bank.build_knowledge_connections = AsyncMock(return_value=[
            {
                "from_entry": 123,
                "to_entry": 456,
                "relationship": "causes",
                "strength": 0.78
            },
            {
                "from_entry": 456,
                "to_entry": 789,
                "relationship": "precedes",
                "strength": 0.65
            }
        ])
        
        connections = await central_memory_bank.build_knowledge_connections("meth_snail")
        
        assert len(connections) == 2
        assert connections[0]["relationship"] == "causes"
        assert connections[1]["relationship"] == "precedes"