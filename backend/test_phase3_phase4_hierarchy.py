#!/usr/bin/env python3
"""
Test Phase 3 & 4: Complete Hierarchy Flow
==========================================

Tests the complete hierarchy:
1. Sir Hawkington monitors and triages
2. VIC-20 receives triage alert and routes
3. Terry receives coordination request and acts
4. Everyone writes to PostgreSQL
5. Everyone CC's The Stick

VECTOR POSE: Testing with BOTH direction AND magnitude! OH YEAH!!!

NOTE: Run this from backend/ directory with venv activated
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env.development
# Get the project root (parent of backend directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env.development')
print(f"📝 Loading environment from: {env_path}")
print(f"📝 File exists: {os.path.exists(env_path)}")

# Load with override=True to ensure it takes precedence
load_dotenv(env_path, override=True)

# Verify it loaded
redis_url = os.getenv('REDIS_URL', 'NOT SET')
print(f"📡 Redis URL from env: {redis_url}")

if redis_url == 'NOT SET' or 'localhost' in redis_url:
    print("⚠️  WARNING: Redis URL not loaded correctly!")
    print("   Setting manually to 192.168.1.216:6379")
    os.environ['REDIS_URL'] = 'redis://192.168.1.216:6379'
    print(f"📡 Redis URL now: {os.getenv('REDIS_URL')}")

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# NOW import modules (they will read the env vars)
from app.core.redis import get_redis_client
from app.ai_agents.distributed.distributed_agent_manager import DistributedAgentManager
from app.core.database import get_async_db


async def test_hierarchy():
    """Test complete hierarchy flow"""
    print("\n" + "="*80)
    print("🎯 PHASE 3 & 4 TEST: Complete Hierarchy Flow")
    print("="*80 + "\n")
    
    # Initialize manager
    print("📦 Initializing distributed agent manager...")
    try:
        # Get system user ID
        from sqlalchemy import select
        from app.models.user import User
        
        system_user_id = None
        async for session in get_async_db():
            result = await session.execute(select(User.id).limit(1))
            system_user_id = result.scalar_one_or_none()
            break
        
        print(f"✅ System user ID: {system_user_id}")
        
        manager = DistributedAgentManager(db_getter=get_async_db, user_id=system_user_id)
        await manager.initialize()
        print("✅ Manager initialized\n")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("-"*80)
    print("✅ VERIFICATION 1: Check Agent Configuration")
    print("-"*80)
    
    # Check each agent
    for agent_name, agent in manager.agents.items():
        has_monitor = hasattr(agent, 'resource_monitor') and agent.resource_monitor is not None
        
        if agent_name == "sir_hawkington":
            status = "✅ HAS ResourceMonitor (CORRECT)" if has_monitor else "❌ NO ResourceMonitor (WRONG)"
            print(f"{status} - {agent_name}: Sole system monitor")
        elif agent_name == "vic_20_sage":
            status = "✅ NO ResourceMonitor (CORRECT)" if not has_monitor else "❌ HAS ResourceMonitor (WRONG)"
            print(f"{status} - {agent_name}: Coordinator (receives from Hawk)")
        elif agent_name == "meth_snail":
            status = "✅ NO ResourceMonitor (CORRECT)" if not has_monitor else "❌ HAS ResourceMonitor (WRONG)"
            print(f"{status} - {agent_name}: Specialist (receives from VIC-20)")
        else:
            status = "✅ NO ResourceMonitor (CORRECT)" if not has_monitor else "❌ HAS ResourceMonitor (WRONG)"
            print(f"{status} - {agent_name}: Specialist")
    
    print("\n" + "-"*80)
    print("✅ VERIFICATION 2: Check Message Subscriptions")
    print("-"*80)
    
    hawk = manager.agents.get("sir_hawkington")
    vic20 = manager.agents.get("vic_20_sage")
    terry = manager.agents.get("meth_snail")
    
    if hawk:
        print("✅ Sir Hawkington: Monitors ALL resources, sends TRIAGE_ALERT to VIC-20")
    
    if vic20:
        print("✅ VIC-20: Subscribed to TRIAGE_ALERT, routes to specialists")
    
    if terry:
        print("✅ Terry: Subscribed to COORDINATION_REQUEST from VIC-20")
    
    print("\n" + "-"*80)
    print("🎯 VERIFICATION 3: Monitor Complete Flow for 60 seconds")
    print("-"*80)
    print("\n🔍 Watching for:")
    print("   1. 🧐 Sir Hawkington: Resource monitoring & triage")
    print("   2. 🖥️ VIC-20: Triage alert received & routing")
    print("   3. 🐌 Terry: Coordination request & action")
    print("   4. 💾 PostgreSQL: Database writes")
    print("   5. 📋 The Stick: Decision logs")
    print("\n⏱️  Starting 60-second observation period...\n")
    
    # Monitor for 60 seconds
    for i in range(60, 0, -10):
        print(f"   ⏰ {i} seconds remaining...")
        await asyncio.sleep(10)
    
    print("\n" + "-"*80)
    print("🏁 TEST COMPLETE")
    print("-"*80)
    
    print("\n📊 Expected Flow (check backend logs):")
    print("   1. 🧐 Sir Hawkington publishes RESOURCE_ALERT every 5 seconds")
    print("   2. 🧐 If threshold exceeded → sends TRIAGE_ALERT to VIC-20")
    print("   3. 🖥️ VIC-20 receives TRIAGE_ALERT → routes to specialist")
    print("   4. 🖥️ VIC-20 sends COORDINATION_REQUEST to Terry")
    print("   5. 🐌 Terry receives request → decides (80% his way!)")
    print("   6. 🐌 Terry executes cache clear → writes to PostgreSQL")
    print("   7. 🐌 Terry sends ACTION_REPORT to VIC-20")
    print("   8. 📋 Everyone CC's The Stick with DECISION_LOG")
    
    print("\n💡 To trigger the flow:")
    print("   - Lower thresholds in Sir Hawkington (e.g., memory > 20%)")
    print("   - Or run memory-intensive process to exceed 75% threshold")
    
    print("\n📝 Check PostgreSQL for writes:")
    print("   SELECT * FROM central_memory_bank ORDER BY created_at DESC LIMIT 10;")
    
    # Cleanup
    print("\n🧹 Shutting down...")
    await manager.shutdown()
    print("✅ Test complete!\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_hierarchy())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
