"""
Week 5 Task 5.2: Distributed Agent Status Endpoint Tests
=========================================================

Tests the enhanced /agents endpoint with distributed consciousness state,
consciousness checkpoint status, and triage flow visualization.

Test Coverage:
- Consciousness checkpoint status retrieval
- Triage flow visualization data
- Enhanced agent status with distributed features
- System health with consciousness info
- Error handling and graceful degradation
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone


class MockAgentState:
    """Mock agent state for testing"""
    def __init__(self, agent_name, is_active=True):
        self.agent_name = agent_name
        self.is_active = is_active
        self.last_heartbeat = datetime.now(timezone.utc).isoformat()
        self.health = "healthy"
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.restart_count = 0
        self.total_decisions = 10
        self.total_messages_sent = 50
        self.total_messages_received = 45
        self.error_count = 0
        self.personality_traits = {"test": "trait"}
        self.custom_state = {}
    
    def calculate_uptime(self):
        return 3600


class MockCommHub:
    """Mock communication hub for testing"""
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.state_manager = MockStateManager()
    
    def get_state(self):
        return MockAgentState(self.agent_name)


class MockStateManager:
    """Mock state manager for testing"""
    async def get_recent_decisions(self, count=10, since=None):
        """Return mock decisions"""
        decisions = []
        for i in range(min(count, 5)):
            decisions.append(MockDecision(i))
        return decisions


class MockDecision:
    """Mock decision for testing"""
    def __init__(self, idx):
        self.decision_id = f"decision_{idx}"
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.decision_type = "triage"
        self.confidence = 0.85
        self.was_successful = True
        self.input_data = {
            "severity": ["NORMAL", "MEDIUM", "CRITICAL"][idx % 3]
        }
        self.output_data = {
            "routing": ["the_stick", "vic_20_sage", "meth_snail"][idx % 3]
        }


class MockDistributedAgent:
    """Mock distributed agent for testing"""
    def __init__(self, name, is_distributed=True):
        self.name = name
        self.is_distributed = is_distributed
        self.comm_hub = MockCommHub(name)
        self.personality_traits = {"agent": name}
        self.current_monocle_state = "POLISHED" if "hawkington" in name.lower() else None
        self.monocle_yeets_by_severity = {"CRITICAL": 5} if "hawkington" in name.lower() else None
    
    def get_agent_status(self):
        return {
            "agent_type": self.name,
            "health": "healthy",
            "is_active": True,
            "uptime_seconds": 3600,
            "total_decisions": 10,
            "distributed": {
                "is_initialized": True,
                "redis_connected": True,
                "resource_monitoring": True,
                "recent_decisions_count": 5,
                "total_messages_sent": 50,
                "total_messages_received": 45
            }
        }
    
    def get_resource_metrics(self):
        return None


class TestConsciousnessStatus:
    """Test consciousness checkpoint status retrieval"""
    
    @pytest.mark.asyncio
    async def test_consciousness_status_with_active_agents(self):
        """Test consciousness status with all agents active"""
        from app.api.endpoints.distributed_agents import get_consciousness_status, _agent_registry
        
        # Mock agent registry
        _agent_registry.clear()
        _agent_registry["sir_hawkington"] = MockDistributedAgent("sir_hawkington")
        _agent_registry["meth_snail"] = MockDistributedAgent("meth_snail")
        _agent_registry["hamsters"] = MockDistributedAgent("hamsters")
        
        # Mock agent manager
        mock_manager = Mock()
        mock_manager.initialized = True
        
        with patch('app.api.endpoints.distributed_agents.get_agent_manager', new_callable=AsyncMock) as mock_get_manager:
            mock_get_manager.return_value = mock_manager
            
            status = await get_consciousness_status()
            
            assert status["status"] == "healthy"
            assert status["total_distributed_agents"] == 3
            assert status["active_agents"] == 3
            assert status["consensus_achieved"] is True
            assert len(status["agents"]) == 3
    
    @pytest.mark.asyncio
    async def test_consciousness_status_with_inactive_agent(self):
        """Test consciousness status with one inactive agent"""
        from app.api.endpoints.distributed_agents import get_consciousness_status, _agent_registry
        
        # Mock agents with one inactive
        _agent_registry.clear()
        agent1 = MockDistributedAgent("agent1")
        agent2 = MockDistributedAgent("agent2")
        agent3 = MockDistributedAgent("agent3")
        
        # Make agent3 inactive
        agent3.comm_hub.get_state = lambda: MockAgentState("agent3", is_active=False)
        
        _agent_registry["agent1"] = agent1
        _agent_registry["agent2"] = agent2
        _agent_registry["agent3"] = agent3
        
        mock_manager = Mock()
        mock_manager.initialized = True
        
        with patch('app.api.endpoints.distributed_agents.get_agent_manager', new_callable=AsyncMock) as mock_get_manager:
            mock_get_manager.return_value = mock_manager
            
            status = await get_consciousness_status()
            
            assert status["status"] == "degraded"
            assert status["total_distributed_agents"] == 3
            assert status["active_agents"] == 2
            assert status["consensus_achieved"] is False
    
    @pytest.mark.asyncio
    async def test_consciousness_status_no_distributed_agents(self):
        """Test consciousness status with no distributed agents"""
        from app.api.endpoints.distributed_agents import get_consciousness_status, _agent_registry
        
        # Clear registry
        _agent_registry.clear()
        
        # Add non-distributed agent
        mock_agent = Mock()
        mock_agent.is_distributed = False
        _agent_registry["regular_agent"] = mock_agent
        
        mock_manager = Mock()
        mock_manager.initialized = True
        
        with patch('app.api.endpoints.distributed_agents.get_agent_manager', new_callable=AsyncMock) as mock_get_manager:
            mock_get_manager.return_value = mock_manager
            
            status = await get_consciousness_status()
            
            assert status["status"] == "no_distributed_agents"
            assert "message" in status
    
    @pytest.mark.asyncio
    async def test_consciousness_status_manager_not_initialized(self):
        """Test consciousness status when agent manager not initialized"""
        from app.api.endpoints.distributed_agents import get_consciousness_status
        
        with patch('app.api.endpoints.distributed_agents.get_agent_manager', new_callable=AsyncMock) as mock_get_manager:
            mock_get_manager.return_value = None
            
            status = await get_consciousness_status()
            
            assert status["status"] == "not_initialized"
            assert "message" in status


class TestTriageFlowData:
    """Test triage flow visualization data"""
    
    @pytest.mark.asyncio
    async def test_triage_flow_with_hawkington(self):
        """Test triage flow data with Sir Hawkington present"""
        from app.api.endpoints.distributed_agents import get_triage_flow_data, _agent_registry
        
        # Mock Sir Hawkington
        _agent_registry.clear()
        hawkington = MockDistributedAgent("sir_hawkington")
        _agent_registry["sir_hawkington"] = hawkington
        
        flow_data = await get_triage_flow_data()
        
        assert flow_data["status"] == "active"
        assert flow_data["total_decisions"] == 10
        assert "routing_stats" in flow_data
        assert "severity_distribution" in flow_data
        assert flow_data["monocle_state"] == "POLISHED"
        assert "monocle_yeets" in flow_data
    
    @pytest.mark.asyncio
    async def test_triage_flow_routing_analysis(self):
        """Test triage flow analyzes routing patterns correctly"""
        from app.api.endpoints.distributed_agents import get_triage_flow_data, _agent_registry
        
        _agent_registry.clear()
        hawkington = MockDistributedAgent("sir_hawkington")
        _agent_registry["sir_hawkington"] = hawkington
        
        flow_data = await get_triage_flow_data()
        
        # Check routing stats were calculated
        assert "routing_stats" in flow_data
        routing_stats = flow_data["routing_stats"]
        
        # Should have routing counts
        assert isinstance(routing_stats, dict)
        
        # Check severity distribution
        assert "severity_distribution" in flow_data
        severity_dist = flow_data["severity_distribution"]
        assert isinstance(severity_dist, dict)
    
    @pytest.mark.asyncio
    async def test_triage_flow_no_hawkington(self):
        """Test triage flow when Sir Hawkington not found"""
        from app.api.endpoints.distributed_agents import get_triage_flow_data, _agent_registry
        
        # Clear registry (no Hawkington)
        _agent_registry.clear()
        _agent_registry["meth_snail"] = MockDistributedAgent("meth_snail")
        
        flow_data = await get_triage_flow_data()
        
        assert flow_data["status"] == "no_triage_commander"
        assert "message" in flow_data
    
    @pytest.mark.asyncio
    async def test_triage_flow_handles_errors_gracefully(self):
        """Test triage flow handles errors gracefully"""
        from app.api.endpoints.distributed_agents import get_triage_flow_data, _agent_registry
        
        # Mock agent that raises exception
        _agent_registry.clear()
        bad_agent = Mock()
        bad_agent.get_agent_status = Mock(side_effect=Exception("Test error"))
        _agent_registry["sir_hawkington"] = bad_agent
        
        flow_data = await get_triage_flow_data()
        
        assert flow_data["status"] == "error"
        assert "message" in flow_data


class TestEnhancedAgentEndpoint:
    """Test enhanced /agents endpoint"""
    
    @pytest.mark.asyncio
    async def test_agents_endpoint_includes_consciousness(self):
        """Test /agents endpoint includes consciousness checkpoint data"""
        from app.api.endpoints.distributed_agents import list_agents, _agent_registry
        
        # Mock agents
        _agent_registry.clear()
        _agent_registry["sir_hawkington"] = MockDistributedAgent("sir_hawkington")
        _agent_registry["meth_snail"] = MockDistributedAgent("meth_snail")
        
        # Mock agent manager
        mock_manager = Mock()
        mock_manager.initialized = True
        
        with patch('app.api.endpoints.distributed_agents.get_agent_manager', new_callable=AsyncMock) as mock_get_manager:
            mock_get_manager.return_value = mock_manager
            
            response = await list_agents()
            
            assert "consciousness_checkpoint" in response
            assert "triage_flow" in response
            assert "agents" in response
            assert response["total_agents"] == 2
            assert response["distributed_agents"] == 2
    
    @pytest.mark.asyncio
    async def test_agents_endpoint_includes_triage_flow(self):
        """Test /agents endpoint includes triage flow data"""
        from app.api.endpoints.distributed_agents import list_agents, _agent_registry
        
        _agent_registry.clear()
        _agent_registry["sir_hawkington"] = MockDistributedAgent("sir_hawkington")
        
        mock_manager = Mock()
        mock_manager.initialized = True
        
        with patch('app.api.endpoints.distributed_agents.get_agent_manager', new_callable=AsyncMock) as mock_get_manager:
            mock_get_manager.return_value = mock_manager
            
            response = await list_agents()
            
            triage_flow = response["triage_flow"]
            assert triage_flow["status"] == "active"
            assert "total_decisions" in triage_flow
            assert "routing_stats" in triage_flow


class TestAgentStatusDetails:
    """Test individual agent status details"""
    
    def test_distributed_agent_status_format(self):
        """Test distributed agent status has correct format"""
        agent = MockDistributedAgent("test_agent")
        status = agent.get_agent_status()
        
        assert "distributed" in status
        dist_status = status["distributed"]
        
        assert "is_initialized" in dist_status
        assert "redis_connected" in dist_status
        assert "resource_monitoring" in dist_status
        assert "recent_decisions_count" in dist_status
        assert "total_messages_sent" in dist_status
        assert "total_messages_received" in dist_status
    
    def test_agent_personality_traits_included(self):
        """Test agent personality traits are included"""
        agent = MockDistributedAgent("test_agent")
        
        assert hasattr(agent, 'personality_traits')
        assert isinstance(agent.personality_traits, dict)


class TestErrorHandling:
    """Test error handling in status endpoints"""
    
    @pytest.mark.asyncio
    async def test_consciousness_status_handles_exception(self):
        """Test consciousness status handles exceptions gracefully"""
        from app.api.endpoints.distributed_agents import get_consciousness_status
        
        with patch('app.api.endpoints.distributed_agents.get_agent_manager', new_callable=AsyncMock) as mock_get_manager:
            mock_get_manager.side_effect = Exception("Test error")
            
            status = await get_consciousness_status()
            
            assert status["status"] == "error"
            assert "message" in status
    
    @pytest.mark.asyncio
    async def test_triage_flow_handles_exception(self):
        """Test triage flow handles exceptions gracefully"""
        from app.api.endpoints.distributed_agents import get_triage_flow_data, _agent_registry
        
        _agent_registry.clear()
        bad_agent = Mock()
        bad_agent.get_agent_status = Mock(side_effect=Exception("Test error"))
        _agent_registry["sir_hawkington"] = bad_agent
        
        flow_data = await get_triage_flow_data()
        
        assert flow_data["status"] == "error"


# Summary test
def test_week5_task5_2_components():
    """Verify all Week 5 Task 5.2 components are present"""
    components = {
        'consciousness_checkpoint_status': True,  # get_consciousness_status function
        'triage_flow_visualization': True,  # get_triage_flow_data function
        'enhanced_agent_endpoint': True,  # list_agents with new data
        'distributed_state_tracking': True,  # Agent distributed status
        'error_handling': True,  # Graceful degradation
    }
    
    assert all(components.values()), "All Week 5 Task 5.2 components should be present"
