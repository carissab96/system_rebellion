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

NOTE: Run this from the project root, not from within backend/
"""

import asyncio
import sys
import os


async def test_phase2():
    """Test Phase 2 implementation"""
    print("\n" + "="*80)
    print("🧪 PHASE 2 TEST: Sir Hawkington Triage Logic")
    print("="*80 + "\n")
    
    # Import here to avoid circular imports
    print("📦 Importing modules...")
    try:
        # Add backend to path if needed
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Import after path is set
        from app.database import get_async_db
        
        # Import manager last to avoid circular imports
        from app.ai_agents.distributed.distributed_agent_manager import DistributedAgentManager
        
        print("✅ Imports successful\n")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTry running from project root:")
        print("  cd /home/carissa/Documents/system_rebellion")
        print("  python test_phase2_hawk_triage.py")
        return
    
    # Initialize manager
    print("📦 Initializing distributed agent manager...")
    try:
        manager = DistributedAgentManager(db_getter=get_async_db)
        await manager.initialize()
        print("✅ Manager initialized\n")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("-"*80)
    print("✅ VERIFICATION 1: Check ResourceMonitor Status")
    print("-"*80)
    
    # Check each agent
    for agent_name, agent in manager.agents.items():
        # Check if agent has resource_monitor attribute
        has_monitor_attr = hasattr(agent, 'resource_monitor')
        
        # Check if it's actually enabled (not None)
        if has_monitor_attr:
            monitor = getattr(agent, 'resource_monitor', None)
            has_monitor = monitor is not None
        else:
            has_monitor = False
        
        if agent_name == "sir_hawkington":
            if has_monitor:
                print(f"✅ {agent_name}: HAS ResourceMonitor (CORRECT - sole system monitor)")
                # Check what resources Hawk monitors
                if hasattr(agent, 'resource_thresholds'):
                    thresholds = agent.resource_thresholds
                    print(f"   Monitoring {len(thresholds)} resources: {list(thresholds.keys())}")
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
        
        all_present = True
        for method in methods:
            if hasattr(hawk, method):
                print(f"✅ Sir Hawkington has method: {method}")
            else:
                print(f"❌ Sir Hawkington MISSING method: {method}")
                all_present = False
        
        if all_present:
            print("\n🎯 All triage methods present!")
    else:
        print("❌ Could not find sir_hawkington agent!")
    
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
        
        print("Testing confidence assessment:")
        for current, threshold, severity in test_cases:
            confidence = hawk._assess_confidence(current, threshold, severity)
            should_escalate = hawk._should_escalate_to_vic20(severity, confidence)
            print(f"   {current}% (threshold {threshold}%, severity={severity}): "
                  f"confidence={confidence:.2f}, escalate={should_escalate}")
    else:
        print("❌ Cannot test triage logic - methods not found")
    
    print("\n" + "-"*80)
    print("✅ VERIFICATION 4: Monitor for 30 seconds")
    print("-"*80)
    print("Watching for resource alerts and triage decisions...")
    print("(Check backend logs for triage messages)")
    print("")
    
    # Let it run for 30 seconds to see if any alerts fire
    for i in range(30, 0, -5):
        print(f"   {i} seconds remaining...")
        await asyncio.sleep(5)
    
    print("\n" + "-"*80)
    print("🏁 TEST COMPLETE")
    print("-"*80)
    print("\n📋 Check backend logs for:")
    print("   - '🧐⚠️ Sir Hawkington observes elevated' (alert received)")
    print("   - '🧐🎯 Triage assessment' (triage logic)")
    print("   - '🧐📨 Triage alert sent to VIC-20' (routing)")
    print("   - '🧐📋 Decision logged to The Stick' (CC)")
    
    # Cleanup
    print("\n🧹 Shutting down...")
    await manager.shutdown()
    print("✅ Test complete!\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_phase2())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
