"""
Test Decision History Integration
=================================

Test that decision history can be queried from distributed agents.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockDistributedAgent:
    """Mock distributed agent with decision history"""
    
    def __init__(self, name):
        self.name = name
        self.decisions = [
            {
                "decision_id": f"{name}_decision_1",
                "decision_type": "test_decision",
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.95
            },
            {
                "decision_id": f"{name}_decision_2",
                "decision_type": "triage_routing_received",
                "timestamp": datetime.now().isoformat(),
                "confidence": 1.0
            }
        ]
    
    async def get_recent_decisions(self, limit=50):
        return self.decisions[:limit]


class MockRegularAgent:
    """Mock agent without distributed features"""
    
    def __init__(self, name):
        self.name = name


class TestDecisionHistory:
    """Test decision history integration"""
    
    @pytest.mark.asyncio
    async def test_get_decision_history_all_agents(self):
        """Test getting decision history from all agents"""
        
        from app.ai_agents.agent_manager import AIAgentManager
        
        # Create mock agent manager
        manager = AIAgentManager(
            memory_service=AsyncMock(),
            db_getter=AsyncMock(),
            redis_url="redis://localhost:6379"
        )
        
        # Add mock agents
        manager.agents = {
            "meth_snail": MockDistributedAgent("meth_snail"),
            "hamsters": MockDistributedAgent("hamsters"),
            "regular_agent": MockRegularAgent("regular_agent")
        }
        
        # Get decision history
        history = await manager.get_distributed_decision_history()
        
        # Verify structure
        assert "timestamp" in history
        assert "agents" in history
        
        # Verify distributed agents have decisions
        assert history["agents"]["meth_snail"]["status"] == "success"
        assert history["agents"]["meth_snail"]["decision_count"] == 2
        assert len(history["agents"]["meth_snail"]["decisions"]) == 2
        
        assert history["agents"]["hamsters"]["status"] == "success"
        assert history["agents"]["hamsters"]["decision_count"] == 2
        
        # Verify regular agent is marked as not distributed
        assert history["agents"]["regular_agent"]["status"] == "not_distributed"
    
    @pytest.mark.asyncio
    async def test_get_decision_history_specific_agent(self):
        """Test getting decision history from specific agent"""
        
        from app.ai_agents.agent_manager import AIAgentManager
        
        # Create mock agent manager
        manager = AIAgentManager(
            memory_service=AsyncMock(),
            db_getter=AsyncMock(),
            redis_url="redis://localhost:6379"
        )
        
        # Add mock agents
        manager.agents = {
            "meth_snail": MockDistributedAgent("meth_snail"),
            "hamsters": MockDistributedAgent("hamsters")
        }
        
        # Get decision history for specific agent
        history = await manager.get_distributed_decision_history(agent_name="meth_snail")
        
        # Verify only meth_snail is in results
        assert len(history["agents"]) == 1
        assert "meth_snail" in history["agents"]
        assert "hamsters" not in history["agents"]
        
        # Verify decisions
        assert history["agents"]["meth_snail"]["decision_count"] == 2
    
    @pytest.mark.asyncio
    async def test_get_decision_history_with_limit(self):
        """Test that limit parameter is passed to agents"""
        
        from app.ai_agents.agent_manager import AIAgentManager
        
        # Create mock agent manager
        manager = AIAgentManager(
            memory_service=AsyncMock(),
            db_getter=AsyncMock(),
            redis_url="redis://localhost:6379"
        )
        
        # Create agent with many decisions
        agent = MockDistributedAgent("test_agent")
        agent.decisions = [{"id": i} for i in range(100)]
        
        manager.agents = {"test_agent": agent}
        
        # Get history with limit
        history = await manager.get_distributed_decision_history(limit=10)
        
        # Verify limit was applied
        assert history["agents"]["test_agent"]["decision_count"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
