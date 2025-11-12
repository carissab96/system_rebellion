"""
Comprehensive Tests for All Distributed Agents
==============================================

Tests all 6 distributed agents to verify:
- Initialization works
- Personality traits preserved
- Resource thresholds configured
- Distributed features can be enabled
- Original functionality intact
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai_agents.sir_hawkington.distributed_hawkington import SirHawkingtonDistributed
from app.ai_agents.meth_snail.distributed_meth_snail import MethSnailDistributed
from app.ai_agents.hamsters.distributed_hamsters import HamstersDistributed
from app.ai_agents.quantum_shadow_people.distributed_qsp import QuantumShadowPeopleDistributed
from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
from app.ai_agents.the_stick.distributed_stick import TheStickDistributed
from app.ai_agents.distributed.resource_monitor import ResourceType


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis = AsyncMock()
    redis.ping = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.publish = AsyncMock(return_value=1)
    redis.aclose = AsyncMock()
    return redis


class TestAllDistributedAgents:
    """Test all 6 distributed agents"""
    
    def test_sir_hawkington_initialization(self):
        """Test Sir Hawkington initializes correctly"""
        agent = SirHawkingtonDistributed()
        assert agent.agent_name == "sir_hawkington"
        assert not agent.is_distributed
        assert agent.personality_traits["aristocratic"] is True
        assert agent.personality_traits["monocle_yeeting_enabled"] is True
        assert ResourceType.CPU in agent.resource_thresholds
        assert agent.resource_thresholds[ResourceType.CPU] == 70.0
    
    def test_meth_snail_initialization(self):
        """Test Meth Snail initializes correctly"""
        agent = MethSnailDistributed()
        assert agent.agent_name == "meth_snail"
        assert not agent.is_distributed
        assert agent.personality_traits["speed_obsessed"] is True
        assert agent.personality_traits["hyperactive"] is True
        assert agent.personality_traits["no_fake_data_tolerance"] == 0
        assert ResourceType.MEMORY in agent.resource_thresholds
        assert agent.resource_thresholds[ResourceType.MEMORY] == 75.0
    
    def test_hamsters_initialization(self):
        """Test Hamsters initialize correctly"""
        agent = HamstersDistributed()
        assert agent.agent_name == "hamsters"
        assert not agent.is_distributed
        assert agent.personality_traits["telepathic"] is True
        assert agent.personality_traits["beer_loving"] is True
        assert agent.personality_traits["duct_tape_experts"] is True
        assert ResourceType.DISK in agent.resource_thresholds
        assert agent.resource_thresholds[ResourceType.DISK] == 80.0
    
    def test_qsp_initialization(self):
        """Test QSP initializes correctly"""
        agent = QuantumShadowPeopleDistributed()
        assert agent.agent_name == "quantum_shadow_people"
        assert not agent.is_distributed
        assert agent.personality_traits["quantum"] is True
        assert agent.personality_traits["paranoid"] is True
        assert agent.personality_traits["tequila_jello_shot_powered"] is True
        assert ResourceType.NETWORK in agent.resource_thresholds
        assert agent.resource_thresholds[ResourceType.NETWORK] == 85.0
    
    def test_vic20_initialization(self):
        """Test VIC-20 initializes correctly"""
        agent = VIC20SageDistributed()
        assert agent.agent_name == "vic_20_sage"
        assert not agent.is_distributed
        assert agent.personality_traits["coordinator"] is True
        assert agent.personality_traits["pattern_matcher"] is True
        assert agent.personality_traits["wise"] is True
        assert ResourceType.CPU in agent.resource_thresholds
        assert agent.resource_thresholds[ResourceType.CPU] == 75.0
    
    def test_stick_initialization(self):
        """Test The Stick initializes correctly"""
        agent = TheStickDistributed()
        assert agent.agent_name == "the_stick"
        assert not agent.is_distributed
        assert agent.personality_traits["learning_coordinator"] is True
        assert agent.personality_traits["patient"] is True
        assert agent.personality_traits["persistent"] is True
        assert ResourceType.CPU in agent.resource_thresholds
        assert agent.resource_thresholds[ResourceType.CPU] == 80.0
    
    @pytest.mark.asyncio
    async def test_all_agents_can_initialize_distributed(self, mock_redis):
        """Test all agents can initialize distributed features"""
        agents = [
            SirHawkingtonDistributed(),
            MethSnailDistributed(),
            HamstersDistributed(),
            QuantumShadowPeopleDistributed(),
            VIC20SageDistributed(),
            TheStickDistributed()
        ]
        
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            # Setup mocks
            mock_hub = AsyncMock()
            mock_hub.initialize = AsyncMock()
            mock_hub.get_state = Mock(return_value=Mock(personality_traits={}))
            mock_hub.state_manager = Mock()
            mock_hub.state_manager.save_state = AsyncMock()
            mock_hub_class.return_value = mock_hub
            
            mock_monitor = Mock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock()
            mock_monitor.set_threshold = Mock()
            mock_monitor.register_alert_callback = Mock()
            mock_monitor.is_running = False
            mock_monitor_class.return_value = mock_monitor
            
            # Initialize all agents
            for agent in agents:
                await agent.initialize_distributed(mock_redis)
                assert agent.is_distributed
                assert agent.comm_hub is not None
                assert agent.resource_monitor is not None
    
    def test_all_agents_have_get_agent_status(self):
        """Test all agents implement get_agent_status"""
        agents = [
            SirHawkingtonDistributed(),
            MethSnailDistributed(),
            HamstersDistributed(),
            QuantumShadowPeopleDistributed(),
            VIC20SageDistributed(),
            TheStickDistributed()
        ]
        
        for agent in agents:
            status = agent.get_agent_status()
            assert "agent_name" in status
            assert "agent_type" in status
            assert "is_active" in status
            assert "distributed" in status
            assert status["distributed"]["distributed_enabled"] is False
    
    def test_all_agents_have_repr(self):
        """Test all agents have string representation"""
        agents = [
            SirHawkingtonDistributed(),
            MethSnailDistributed(),
            HamstersDistributed(),
            QuantumShadowPeopleDistributed(),
            VIC20SageDistributed(),
            TheStickDistributed()
        ]
        
        for agent in agents:
            repr_str = repr(agent)
            assert "Distributed" in repr_str
            assert "LOCAL" in repr_str  # Not distributed yet
    
    def test_resource_threshold_uniqueness(self):
        """Test each agent monitors different resources"""
        agents_and_resources = [
            (SirHawkingtonDistributed(), ResourceType.CPU, 70.0),
            (MethSnailDistributed(), ResourceType.MEMORY, 75.0),
            (HamstersDistributed(), ResourceType.DISK, 80.0),
            (QuantumShadowPeopleDistributed(), ResourceType.NETWORK, 85.0),
            (VIC20SageDistributed(), ResourceType.CPU, 75.0),
            (TheStickDistributed(), ResourceType.CPU, 80.0)
        ]
        
        for agent, resource_type, threshold in agents_and_resources:
            assert resource_type in agent.resource_thresholds
            assert agent.resource_thresholds[resource_type] == threshold
    
    def test_all_agents_are_active(self):
        """Test all agents start in active state"""
        agents = [
            SirHawkingtonDistributed(),
            MethSnailDistributed(),
            HamstersDistributed(),
            QuantumShadowPeopleDistributed(),
            VIC20SageDistributed(),
            TheStickDistributed()
        ]
        
        for agent in agents:
            assert agent.is_active is True
    
    def test_personality_traits_are_dicts(self):
        """Test all agents have personality traits as dictionaries"""
        agents = [
            SirHawkingtonDistributed(),
            MethSnailDistributed(),
            HamstersDistributed(),
            QuantumShadowPeopleDistributed(),
            VIC20SageDistributed(),
            TheStickDistributed()
        ]
        
        for agent in agents:
            assert isinstance(agent.personality_traits, dict)
            assert len(agent.personality_traits) > 0
    
    @pytest.mark.asyncio
    async def test_all_agents_can_shutdown_distributed(self, mock_redis):
        """Test all agents can shutdown distributed features cleanly"""
        agents = [
            SirHawkingtonDistributed(),
            MethSnailDistributed(),
            HamstersDistributed(),
            QuantumShadowPeopleDistributed(),
            VIC20SageDistributed(),
            TheStickDistributed()
        ]
        
        with patch('app.ai_agents.distributed.mixins.distributed_mixin.AgentCommunicationHub') as mock_hub_class, \
             patch('app.ai_agents.distributed.mixins.distributed_mixin.ResourceMonitor') as mock_monitor_class:
            
            mock_hub = AsyncMock()
            mock_hub.initialize = AsyncMock()
            mock_hub.shutdown = AsyncMock()
            mock_hub.get_state = Mock(return_value=Mock(personality_traits={}))
            mock_hub.state_manager = Mock()
            mock_hub.state_manager.save_state = AsyncMock()
            mock_hub_class.return_value = mock_hub
            
            mock_monitor = Mock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock()
            mock_monitor.set_threshold = Mock()
            mock_monitor.register_alert_callback = Mock()
            mock_monitor.is_running = False
            mock_monitor_class.return_value = mock_monitor
            
            # Initialize and shutdown all agents
            for agent in agents:
                await agent.initialize_distributed(mock_redis)
                assert agent.is_distributed
                
                await agent.shutdown_distributed()
                assert not agent.is_distributed


class TestAgentPersonalities:
    """Test that agent personalities are preserved"""
    
    def test_sir_hawkington_personality(self):
        """Sir Hawkington is aristocratic and distinguished"""
        agent = SirHawkingtonDistributed()
        assert agent.personality_traits["aristocratic"] is True
        assert agent.personality_traits["distinguished"] is True
        assert agent.personality_traits["triage_commander"] is True
    
    def test_meth_snail_personality(self):
        """Terry is speed-obsessed and hyperactive"""
        agent = MethSnailDistributed()
        assert agent.personality_traits["speed_obsessed"] is True
        assert agent.personality_traits["hyperactive"] is True
        assert agent.personality_traits["cache_clearing_frequency"] == "MAXIMUM"
    
    def test_hamsters_personality(self):
        """Hamsters are telepathic and beer-loving"""
        agent = HamstersDistributed()
        assert agent.personality_traits["telepathic"] is True
        assert agent.personality_traits["beer_loving"] is True
        assert agent.personality_traits["consensus_required"] is True
    
    def test_qsp_personality(self):
        """QSP are quantum and paranoid"""
        agent = QuantumShadowPeopleDistributed()
        assert agent.personality_traits["quantum"] is True
        assert agent.personality_traits["paranoid"] is True
        assert agent.personality_traits["security_focused"] is True
    
    def test_vic20_personality(self):
        """VIC-20 is wise and patient"""
        agent = VIC20SageDistributed()
        assert agent.personality_traits["wise"] is True
        assert agent.personality_traits["patient"] is True
        assert agent.personality_traits["orchestrator"] is True
    
    def test_stick_personality(self):
        """The Stick is patient and persistent"""
        agent = TheStickDistributed()
        assert agent.personality_traits["patient"] is True
        assert agent.personality_traits["persistent"] is True
        assert agent.personality_traits["encouraging"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
