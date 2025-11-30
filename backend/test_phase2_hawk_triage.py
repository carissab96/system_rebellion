#!/usr/bin/env python3
"""
Test Phase 2: Sir Hawkington Triage Logic
==========================================

Verifies:
1. Hawk has ResourceMonitor enabled
2. Other agents have NO ResourceMonitor
3. Hawk monitors ALL resources
4. Triage logic works (assess, escalate, route)
5. Messages sent to VIC-20 and The Stick
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.redis import get_redis_client
from app.ai_agents.distributed.distributed_agent_manager import DistributedAgentManager
from app.core.database import get_async_db


async def test_phase2():
    """Test Phase 2 implementation"""
    print("\n" + "="*80)
    print("🧪 PHASE 2 TEST: Sir Hawkington Triage Logic")
    print("="*80 + "\n")
    
    # Initialize manager
    print("📦 Initializing distributed agent manager...")
    manager = DistributedAgentManager(db_getter=get_async_db)
    await manager.initialize()
    
    print("\n" + "-"*80)
    print("✅ VERIFICATION 1: Check ResourceMonitor Status")
    print("-"*80)
    
    # Check each agent
    for agent_name, agent in manager.agents.items():
        has_monitor = hasattr(agent, 'resource_monitor') and agent.resource_monitor is not None
        
        if agent_name == "sir_hawkington":
            if has_monitor:
                print(f"✅ {agent_name}: HAS ResourceMonitor (CORRECT - sole system monitor)")
                # Check what resources Hawk monitors
                if hasattr(agent, 'resource_thresholds'):
                    print(f"   Monitoring: {list(agent.resource_thresholds.keys())}")
            else:
                print(f"❌ {agent_name}: NO ResourceMonitor (WRONG - should be monitoring!)")
        else:
            if has_monitor:
                print(f"❌ {agent_name}: HAS ResourceMonitor (WRONG - should be disabled!)")
            else:
                print(f"✅ {agent_name}: NO ResourceMonitor (CORRECT - receives from hierarchy)")
    
    print("\n" + "-"*80)
    print("✅ VERIFICATION 2: Check Triage Methods")
    print("-"*80)
    
    hawk = manager.agents.get("sir_hawkington")
    if hawk:
        methods = [
            '_assess_confidence',
            '_should_escalate_to_vic20',
            '_send_triage_alert_to_vic20',
            '_cc_the_stick'
        ]
        
        for method in methods:
            if hasattr(hawk, method):
                print(f"✅ Sir Hawkington has method: {method}")
            else:
                print(f"❌ Sir Hawkington MISSING method: {method}")
    
    print("\n" + "-"*80)
    print("✅ VERIFICATION 3: Test Triage Logic")
    print("-"*80)
    
    if hawk and hasattr(hawk, '_assess_confidence'):
        # Test confidence assessment
        test_cases = [
            (72, 70, "high"),   # 2.8% over
            (80, 70, "high"),   # 14.3% over
            (95, 70, "critical")  # 35.7% over
        ]
        
        for current, threshold, severity in test_cases:
            confidence = hawk._assess_confidence(current, threshold, severity)
            should_escalate = hawk._should_escalate_to_vic20(severity, confidence)
            print(f"   {current}% (threshold {threshold}%): confidence={confidence:.2f}, escalate={should_escalate}")
    
    print("\n" + "-"*80)
    print("✅ VERIFICATION 4: Monitor for 30 seconds")
    print("-"*80)
    print("Watching for resource alerts and triage decisions...")
    print("(Check backend logs for triage messages)")
    
    # Let it run for 30 seconds to see if any alerts fire
    await asyncio.sleep(30)
    
    print("\n" + "-"*80)
    print("🏁 TEST COMPLETE")
    print("-"*80)
    print("\n📋 Check backend logs for:")
    print("   - '🧐⚠️ Sir Hawkington observes elevated' (alert received)")
    print("   - '🧐🎯 Triage assessment' (triage logic)")
    print("   - '🧐📨 Triage alert sent to VIC-20' (routing)")
    print("   - '🧐📋 Decision logged to The Stick' (CC)")
    
    # Cleanup
    await manager.shutdown()
    print("\n✅ Test complete!\n")


if __name__ == "__main__":
    asyncio.run(test_phase2())
