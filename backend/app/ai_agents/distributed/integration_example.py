

"""
Integration Example: Distributed Agents with Existing System
=============================================================

This shows how to integrate the distributed agent system with your
existing System Rebellion architecture.
"""

import asyncio
import logging
from typing import Dict, Any

from app.core.redis import get_redis_client
from app.ai_agents.distributed.example_agents import (
    SirHawkingtonDistributed,
    TerryMethSnailDistributed,
    BobHamsterDistributed,
    QuantumShadowPeopleDistributed
)
from app.ai_agents.the_stick.distributed_stick import TheStickDistributed
from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
from app.api.endpoints.distributed_agents import register_agent
from app.ai_agents.distributed.behavior_tracker import get_behavior_tracker

logger = logging.getLogger(__name__)


class DistributedAgentManager:
    """
    Manager for distributed agents.
    
    Handles initialization, lifecycle, and coordination of all distributed agents.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", db_getter=None):
        self.redis_url = redis_url
        self.redis_client = None
        self.db_getter = db_getter
        self.agents: Dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize all distributed agents"""
        if self._initialized:
            logger.warning("Distributed agents already initialized")
            return
        
        try:
            # Get Redis client
            logger.info(f"Connecting to Redis at {self.redis_url}")
            self.redis_client = await get_redis_client()
            
            # Initialize agents
            logger.info("Initializing distributed agents...")
            
            # Sir Hawkington - CPU Monitor
            sir_hawk = SirHawkingtonDistributed(self.redis_client)
            await sir_hawk.initialize()
            self.agents["sir_hawkington"] = sir_hawk
            register_agent("sir_hawkington", sir_hawk)
            logger.info("✅ Sir Hawkington initialized")
            
            # Terry the Meth Snail - Memory Monitor
            terry = TerryMethSnailDistributed(self.redis_client)
            await terry.initialize()
            self.agents["terry_meth_snail"] = terry
            register_agent("terry_meth_snail", terry)
            logger.info("✅ Terry the Meth Snail initialized")
            
            # The Hamsters - Disk Monitor (Steve, Bob and Carl)
            hamsters = BobHamsterDistributed(self.redis_client)
            await hamsters.initialize()
            # Keep bob_hamster as the key for backward compatibility
            self.agents["bob_hamster"] = hamsters
            register_agent("bob_hamster", hamsters)
            logger.info("✅ The Hamsters initialized (Steve, Bob and Carl)")
            
            # Quantum Shadow People - Network Monitor
            shadows = QuantumShadowPeopleDistributed(self.redis_client)
            await shadows.initialize()
            self.agents["quantum_shadow_people"] = shadows
            register_agent("quantum_shadow_people", shadows)
            logger.info("✅ Quantum Shadow People initialized")
            
            # The Stick - Learning Coordinator
            stick = TheStickDistributed(db_getter=self.db_getter)
            await stick.initialize_distributed(self.redis_client)
            self.agents["the_stick"] = stick
            register_agent("the_stick", stick)
            logger.info("✅ The Stick initialized")
            
            # VIC-20 Sage - Orchestrator
            vic20 = VIC20SageDistributed(db_getter=self.db_getter)
            await vic20.initialize_distributed(self.redis_client)
            self.agents["vic_20_sage"] = vic20
            register_agent("vic_20_sage", vic20)
            logger.info("✅ VIC-20 Sage initialized")
            
            # Start behavior tracker for research recording
            tracker = get_behavior_tracker()
            await tracker.start(snapshot_interval=2.0)
            logger.info("🔍 Behavior tracker started (research recording active)")
            
            self._initialized = True
            logger.info(f"🌐 All {len(self.agents)} distributed agents initialized!")
            
        except Exception as e:
            logger.error(f"Failed to initialize distributed agents: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown all distributed agents"""
        if not self._initialized:
            return
        
        logger.info("Shutting down distributed agents...")
        
        # Stop behavior tracker
        try:
            tracker = get_behavior_tracker()
            await tracker.stop()
            logger.info("🔍 Behavior tracker stopped")
        except Exception as e:
            logger.error(f"Error stopping behavior tracker: {e}")
        
        for agent_name, agent in self.agents.items():
            try:
                await agent.shutdown()
                logger.info(f"✅ {agent_name} shutdown complete")
            except Exception as e:
                logger.error(f"Error shutting down {agent_name}: {e}")
        
        self.agents.clear()
        self._initialized = False
        logger.info("🛑 All distributed agents shut down")
    
    def get_agent(self, agent_name: str):
        """Get agent by name"""
        return self.agents.get(agent_name)
    
    def get_all_agents(self):
        """Get all agents"""
        return self.agents.copy()
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            "initialized": self._initialized,
            "total_agents": len(self.agents),
            "agents": {}
        }
        
        for agent_name, agent in self.agents.items():
            try:
                status["agents"][agent_name] = agent.get_agent_status()
            except Exception as e:
                status["agents"][agent_name] = {"error": str(e)}
        
        return status


# Global instance
_distributed_manager: DistributedAgentManager = None


async def initialize_distributed_agents(redis_url: str = "redis://localhost:6379", db_getter=None):
    """
    Initialize distributed agents system.
    
    Call this during FastAPI startup.
    
    Args:
        redis_url: Redis connection URL
        db_getter: Database session factory for agents that need database access
    """
    global _distributed_manager
    
    if _distributed_manager is None:
        _distributed_manager = DistributedAgentManager(redis_url, db_getter=db_getter)
    
    await _distributed_manager.initialize()
    return _distributed_manager


async def shutdown_distributed_agents():
    """
    Shutdown distributed agents system.
    
    Call this during FastAPI shutdown.
    """
    global _distributed_manager
    
    if _distributed_manager:
        await _distributed_manager.shutdown()
        _distributed_manager = None


def get_distributed_manager() -> DistributedAgentManager:
    """Get the distributed agent manager instance"""
    if _distributed_manager is None:
        raise RuntimeError("Distributed agents not initialized")
    return _distributed_manager


# Example: Integration with FastAPI main.py
"""
# In backend/main.py

from app.ai_agents.distributed.integration_example import (
    initialize_distributed_agents,
    shutdown_distributed_agents
)

@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...
    
    # Initialize distributed agents
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        await initialize_distributed_agents(redis_url)
        logger.info("🌐 Distributed agent system initialized")
    except Exception as e:
        logger.error(f"Failed to initialize distributed agents: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    # ... existing shutdown code ...
    
    # Shutdown distributed agents
    try:
        await shutdown_distributed_agents()
        logger.info("🛑 Distributed agent system shut down")
    except Exception as e:
        logger.error(f"Error shutting down distributed agents: {e}")

# Add the distributed agents router
from app.api.endpoints import distributed_agents
app.include_router(distributed_agents.router, prefix="/api/v1")
"""


# Example: Using agents in your existing code
"""
from app.ai_agents.distributed.integration_example import get_distributed_manager

# Get the manager
manager = get_distributed_manager()

# Get a specific agent
sir_hawk = manager.get_agent("sir_hawkington")

# Send a message
await sir_hawk.send_message_to_agent(
    to_agent="terry_meth_snail",
    message_type=MessageType.AGENT_QUERY,
    payload={"question": "How's the memory looking?"},
    priority=Priority.NORMAL
)

# Make a decision
decision = await sir_hawk.make_decision(
    decision_type="resource_optimization",
    input_data={"cpu_percent": 75.0},
    confidence=0.85
)

# Get system status
status = await manager.get_system_status()
print(f"Agents online: {status['total_agents']}")
"""


# Example: Custom agent integration with existing triage system
"""
from app.ai_agents.sir_hawkington.triage_engine import TriageEngine

class DistributedTriageEngine(TriageEngine):
    '''Enhanced triage engine with distributed agent coordination'''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.distributed_manager = None
    
    async def initialize(self):
        await super().initialize()
        
        # Get distributed manager
        from app.ai_agents.distributed.integration_example import get_distributed_manager
        self.distributed_manager = get_distributed_manager()
    
    async def process_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        # Process with existing triage logic
        result = await super().process_metrics(metrics)
        
        # Also broadcast to distributed agents
        if self.distributed_manager:
            sir_hawk = self.distributed_manager.get_agent("sir_hawkington")
            if sir_hawk:
                await sir_hawk.broadcast_message(
                    MessageType.SYSTEM_EVENT,
                    {
                        "event": "metrics_processed",
                        "severity": result.get("severity"),
                        "metrics": metrics
                    },
                    priority=Priority.NORMAL
                )
        
        return result
"""


if __name__ == "__main__":
    # Test the distributed agent system
    async def test():
        # Initialize
        manager = DistributedAgentManager()
        await manager.initialize()
        
        # Wait a bit for agents to start
        await asyncio.sleep(2)
        
        # Get status
        status = await manager.get_system_status()
        print("\n=== System Status ===")
        print(f"Initialized: {status['initialized']}")
        print(f"Total agents: {status['total_agents']}")
        
        for agent_name, agent_status in status['agents'].items():
            print(f"\n{agent_name}:")
            print(f"  Health: {agent_status.get('health')}")
            print(f"  Uptime: {agent_status.get('uptime_seconds')}s")
            print(f"  Decisions: {agent_status.get('total_decisions')}")
        
        # Test inter-agent communication
        print("\n=== Testing Communication ===")
        sir_hawk = manager.get_agent("sir_hawkington")
        
        from app.ai_agents.distributed.message_protocol import MessageType, Priority
        
        await sir_hawk.send_message_to_agent(
            to_agent="terry_meth_snail",
            message_type=MessageType.AGENT_QUERY,
            payload={"question": "How's the memory?"},
            priority=Priority.NORMAL
        )
        print("✅ Message sent from Sir Hawkington to Terry")
        
        # Wait for message processing
        await asyncio.sleep(1)
        
        # Shutdown
        await manager.shutdown()
        print("\n✅ Test complete")
    
    asyncio.run(test())
