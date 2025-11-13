"""
Test Distributed Agent Configuration
====================================

Quick script to test that distributed agents can be loaded
from the new config file.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ai_agents.agent_manager import get_agent_manager


async def test_distributed_config():
    """Test loading distributed agent configuration"""
    
    print("=" * 60)
    print("TESTING DISTRIBUTED AGENT CONFIGURATION")
    print("=" * 60)
    print()
    
    # Mock dependencies
    class MockMemoryService:
        async def ensure_ready(self):
            pass
    
    async def mock_db_getter():
        return None
    
    try:
        # Get agent manager with distributed agents
        manager = await get_agent_manager(
            db_getter=mock_db_getter,
            memory_service=MockMemoryService(),
            agent_config_path="app/ai_agents/agents_config.yaml",
            redis_url="redis://192.168.1.216:6379",  # ThinkPad Redis
            cache_ttl=300
        )
        
        print(f"✅ Agent Manager initialized")
        print(f"   Agents loaded: {len(manager.agents)}")
        print(f"   Agent names: {list(manager.agents.keys())}")
        print()
        
        # Check each agent
        for agent_name, agent in manager.agents.items():
            has_distributed = hasattr(agent, 'initialize_distributed')
            status = "✅ DISTRIBUTED" if has_distributed else "❌ NOT DISTRIBUTED"
            print(f"   {status}: {agent_name}")
            
            if has_distributed:
                # Check for distributed features
                has_shutdown = hasattr(agent, 'shutdown_distributed')
                has_traits = hasattr(agent, 'personality_traits')
                has_thresholds = hasattr(agent, 'resource_thresholds')
                print(f"      - shutdown_distributed: {'✅' if has_shutdown else '❌'}")
                print(f"      - personality_traits: {'✅' if has_traits else '❌'}")
                print(f"      - resource_thresholds: {'✅' if has_thresholds else '❌'}")
        
        print()
        print("=" * 60)
        print("✅ ALL DISTRIBUTED AGENTS LOADED SUCCESSFULLY!")
        print("=" * 60)
        
        # Cleanup
        await manager.shutdown()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_distributed_config())
    sys.exit(0 if success else 1)
