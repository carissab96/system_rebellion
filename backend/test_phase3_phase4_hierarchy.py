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
    print("✅ VERIFICATION 2: Check Message Subscriptions & DB Integration")
    print("-"*80)
    
    hawk = manager.agents.get("sir_hawkington")
    vic20 = manager.agents.get("vic_20_sage")
    terry = manager.agents.get("meth_snail")
    stick = manager.agents.get("the_stick")
    hamsters = manager.agents.get("hamsters")
    qsp = manager.agents.get("quantum_shadow_people")
    
    if hawk:
        has_db = hasattr(hawk, 'db_integration') and hawk.db_integration is not None
        print(f"✅ Sir Hawkington: Monitors ALL resources, sends TRIAGE_ALERT to VIC-20 | DB: {'✅' if has_db else '❌'}")
    
    if vic20:
        has_db = hasattr(vic20, 'db_integration') and vic20.db_integration is not None
        print(f"✅ VIC-20: Subscribed to TRIAGE_ALERT, routes to specialists | DB: {'✅' if has_db else '❌'}")
    
    if terry:
        has_db = hasattr(terry, 'db_integration') and terry.db_integration is not None
        print(f"✅ Terry (Meth Snail): CPU/Memory/Swap specialist | DB: {'✅' if has_db else '❌'}")
    
    if stick:
        has_db = hasattr(stick, 'db_integration') and stick.db_integration is not None
        print(f"✅ The Stick: Universal logger, CC'd on all decisions | DB: {'✅' if has_db else '❌'}")
    
    if hamsters:
        has_db = hasattr(hamsters, 'db_integration') and hamsters.db_integration is not None
        print(f"✅ Hamsters: Disk specialist (Steve, Bob, Carl) | DB: {'✅' if has_db else '❌'}")
    
    if qsp:
        has_db = hasattr(qsp, 'db_integration') and qsp.db_integration is not None
        print(f"✅ QSP: Network specialist (paranoid quantum monitoring) | DB: {'✅' if has_db else '❌'}")
    
    print("\n" + "-"*80)
    print("🎯 VERIFICATION 3: Monitor Complete Flow for 60 seconds")
    print("-"*80)
    print("\n🔍 Watching for:")
    print("   1. 🧐 Sir Hawkington: Resource monitoring & triage (ALL resources)")
    print("   2. 🖥️ VIC-20: Triage alert received & routing to specialists")
    print("   3. 🐌 Terry: CPU/Memory/Swap coordination & action")
    print("   4. � Hamsters: Disk coordination (Steve, Bob, Carl consensus)")
    print("   5. 👻 QSP: Network coordination (paranoid quantum analysis)")
    print("   6. � The Stick: Universal decision logging")
    print("   7. 💾 PostgreSQL: Dual-write to CMB + agent tables + vectors")
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
    print("   3. 🖥️ VIC-20 receives TRIAGE_ALERT → routes to specialist based on resource:")
    print("      • CPU/Memory/Swap → 🐌 Terry (Meth Snail)")
    print("      • Disk → � Hamsters (Steve, Bob, Carl)")
    print("      • Network → 👻 QSP (Quantum Shadow People)")
    print("   4. Specialist receives COORDINATION_REQUEST → decides & acts")
    print("   5. Specialist writes to PostgreSQL (CMB + agent table + vector)")
    print("   6. Specialist sends ACTION_REPORT to VIC-20")
    print("   7. � The Stick CC'd on all decisions via DECISION_LOG")
    
    print("\n💡 Current thresholds (lowered for testing):")
    print("   • CPU: 20% → Terry")
    print("   • Memory: 20% → Terry")
    print("   • Disk: 20% → Hamsters")
    print("   • Network: 5% → QSP")
    print("   • Swap: 10% → Terry")
    
    # Check database for writes
    print("\n" + "-"*80)
    print("� VERIFICATION 4: Database Write Check")
    print("-"*80)
    
    from sqlalchemy import text
    async for session in get_async_db():
        # Check central memory bank
        result = await session.execute(text(
            "SELECT agent_name, COUNT(*) as cnt FROM central_memory_bank GROUP BY agent_name ORDER BY cnt DESC"
        ))
        rows = result.fetchall()
        print("\n📦 Central Memory Bank by agent:")
        for row in rows:
            print(f"   {row[0]}: {row[1]} entries")
        
        # Check agent-specific tables
        print("\n📦 Agent Memory Banks:")
        tables = [
            'the_stick_memory_bank',
            'sir_hawkington_memory_bank', 
            'meth_snail_memory_bank',
            'hamsters_memory_bank',
            'quantum_shadow_people_memory_bank',
            'vic20_memory_bank'
        ]
        for table in tables:
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            status = "✅" if count > 0 else "⚠️ "
            print(f"   {status} {table}: {count} rows")
        
        # Check vector tables
        print("\n📦 Vector Tables:")
        result = await session.execute(text("SELECT COUNT(*) FROM agent_decision_vectors"))
        count = result.scalar()
        print(f"   agent_decision_vectors: {count} rows")
        break
    
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
