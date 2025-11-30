#!/usr/bin/env python3
"""
Simple Phase 2 Test - No Manager Import
========================================

This test checks the code directly without running the full system.
Avoids circular import issues.
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

print("\n" + "="*80)
print("🧪 PHASE 2 SIMPLE TEST: Code Inspection")
print("="*80 + "\n")

print("-"*80)
print("✅ TEST 1: Check DistributedAgent base class")
print("-"*80)

try:
    from app.ai_agents.distributed.distributed_agent import DistributedAgent
    import inspect
    
    # Check __init__ signature
    sig = inspect.signature(DistributedAgent.__init__)
    params = list(sig.parameters.keys())
    
    if 'enable_resource_monitor' in params:
        print("✅ DistributedAgent has 'enable_resource_monitor' parameter")
        
        # Check default value
        default = sig.parameters['enable_resource_monitor'].default
        if default == False:
            print(f"✅ Default value is False (correct)")
        else:
            print(f"❌ Default value is {default} (should be False)")
    else:
        print("❌ DistributedAgent missing 'enable_resource_monitor' parameter")
        print(f"   Available parameters: {params}")
    
except Exception as e:
    print(f"❌ Error checking DistributedAgent: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "-"*80)
print("✅ TEST 2: Check Sir Hawkington configuration")
print("-"*80)

try:
    # Just read the file, don't import
    hawk_file = os.path.join(backend_path, 'app/ai_agents/sir_hawkington/distributed_hawkington.py')
    
    with open(hawk_file, 'r') as f:
        content = f.read()
    
    # Check for key patterns
    checks = [
        ("enable_resource_monitoring=True", "ResourceMonitor enabled"),
        ("ResourceType.CPU", "Monitors CPU"),
        ("ResourceType.MEMORY", "Monitors Memory"),
        ("ResourceType.DISK", "Monitors Disk"),
        ("ResourceType.NETWORK", "Monitors Network"),
        ("ResourceType.SWAP", "Monitors Swap"),
        ("_assess_confidence", "Has _assess_confidence method"),
        ("_should_escalate_to_vic20", "Has _should_escalate_to_vic20 method"),
        ("_send_triage_alert_to_vic20", "Has _send_triage_alert_to_vic20 method"),
        ("_cc_the_stick", "Has _cc_the_stick method"),
        ("MessageType.TRIAGE_ALERT", "Uses TRIAGE_ALERT message type"),
    ]
    
    for pattern, description in checks:
        if pattern in content:
            print(f"✅ {description}")
        else:
            print(f"❌ Missing: {description}")
    
except Exception as e:
    print(f"❌ Error checking Hawkington: {e}")

print("\n" + "-"*80)
print("✅ TEST 3: Check message protocol")
print("-"*80)

try:
    from app.ai_agents.distributed.message_protocol import MessageType
    
    required_types = [
        'TRIAGE_ALERT',
        'RECOMMENDED_FIX',
        'ACTION_REPORT',
        'DECISION_LOG'
    ]
    
    for msg_type in required_types:
        if hasattr(MessageType, msg_type):
            print(f"✅ MessageType.{msg_type} exists")
        else:
            print(f"❌ MessageType.{msg_type} missing")
    
except Exception as e:
    print(f"❌ Error checking message protocol: {e}")

print("\n" + "-"*80)
print("✅ TEST 4: Check DistributedAgentManager")
print("-"*80)

try:
    manager_file = os.path.join(backend_path, 'app/ai_agents/distributed/distributed_agent_manager.py')
    
    with open(manager_file, 'r') as f:
        content = f.read()
    
    # Check that system_monitor is NOT present
    if 'self.resource_monitor = ResourceMonitor' in content:
        print("❌ Manager still has ResourceMonitor (should be removed)")
    else:
        print("✅ Manager does NOT have ResourceMonitor (correct)")
    
    if 'Sir Hawkington will handle all system monitoring' in content:
        print("✅ Manager has hierarchy comment")
    else:
        print("⚠️  Manager missing hierarchy comment")
    
except Exception as e:
    print(f"❌ Error checking manager: {e}")

print("\n" + "-"*80)
print("🏁 STATIC ANALYSIS COMPLETE")
print("-"*80)
print("\nThis test checks the code without running it.")
print("For runtime testing, check backend logs when running:")
print("  ./run_with_logging.sh")
print("\nLook for:")
print("  - '📊 Resource monitoring enabled for sir_hawkington'")
print("  - '🎯 No resource monitoring for meth_snail' (and others)")
print("")
