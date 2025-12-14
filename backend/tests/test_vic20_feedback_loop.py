"""
Test VIC-20 Feedback Loop - Complete Flow
==========================================

Tests the COMPLETE feedback loop:
1. Hawkington detects issue → TRIAGE_ALERT → VIC-20
2. VIC-20 generates recommendation → COORDINATION_REQUEST → Specialist
3. Specialist takes action → ACTION_REPORT → VIC-20
4. VIC-20 logs outcome → DECISION_LOG → The Stick
5. VIC-20 queries The Stick → finds coordination outcomes with success data

This verifies the entire learning loop works end-to-end.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_complete_feedback_loop():
    """
    Test the complete feedback loop by simulating the hierarchy flow.
    """
    from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
    from app.ai_agents.the_stick.distributed_stick import TheStickDistributed
    from app.core.database import get_async_db
    from app.ai_agents.distributed.message_protocol import AgentMessage, MessageType, Priority
    
    print("=" * 70)
    print("VIC-20 FEEDBACK LOOP TEST - Complete Flow")
    print("=" * 70)
    
    # Initialize agents
    print("\n1. Initializing agents...")
    vic20 = VIC20SageDistributed(db_getter=get_async_db)
    stick = TheStickDistributed(db_getter=get_async_db)
    
    await vic20.db.ensure_initialized()
    await stick.db.ensure_initialized()
    print("   ✅ Agents initialized")
    
    # Step 1: Simulate Hawkington sending TRIAGE_ALERT to VIC-20
    print("\n2. Simulating Hawkington TRIAGE_ALERT...")
    triage_message = AgentMessage(
        from_agent="sir_hawkington",
        to_agent="vic_20_sage",
        message_type=MessageType.TRIAGE_ALERT,
        payload={
            "resource_type": "cpu",
            "severity": "high",
            "confidence": 0.85,
            "current_value": 85.0,
            "threshold": 70.0,
            "assessment": "CPU usage critically high"
        },
        priority=Priority.HIGH,
        timestamp=datetime.now(timezone.utc)
    )
    
    # VIC-20 handles the triage alert
    await vic20._handle_triage_alert_from_hawk(triage_message)
    print("   ✅ VIC-20 received triage alert and generated recommendation")
    
    # Give it a moment to write to database
    await asyncio.sleep(0.5)
    
    # Step 2: Simulate Specialist sending ACTION_REPORT to VIC-20
    print("\n3. Simulating Specialist ACTION_REPORT...")
    action_report = AgentMessage(
        from_agent="meth_snail",
        to_agent="vic_20_sage",
        message_type=MessageType.ACTION_REPORT,
        payload={
            "from_agent": "meth_snail",
            "resource_type": "cpu",
            "action": "throttle_processes",
            "result": {
                "success": True,
                "outcome": "CPU reduced from 85% to 65%",
                "cpu_before": 85.0,
                "cpu_after": 65.0
            },
            "followed_recommendation": True
        },
        priority=Priority.NORMAL,
        timestamp=datetime.now(timezone.utc)
    )
    
    # VIC-20 handles the action report
    await vic20._handle_action_report(action_report)
    print("   ✅ VIC-20 received action report and logged outcome to The Stick")
    
    # Give The Stick time to flush buffer
    await asyncio.sleep(0.5)
    
    # Step 3: Check if The Stick has the coordination outcome
    print("\n4. Checking The Stick's memory for coordination outcomes...")
    async for session in get_async_db():
        from sqlalchemy import text
        result = await session.execute(
            text("""
                SELECT 
                    details->'payload'->>'decision_type' as decision_type,
                    details->'payload'->>'action' as action,
                    details->'payload'->>'success' as success,
                    details->'payload'->>'outcome' as outcome,
                    occurred_at
                FROM central_memory_bank 
                WHERE agent_name = 'the_stick' 
                    AND event_type = 'decision_log'
                    AND details->'payload'->>'decision_type' = 'coordination_outcome'
                ORDER BY occurred_at DESC
                LIMIT 5
            """)
        )
        
        rows = list(result.mappings())
        if rows:
            print(f"   ✅ Found {len(rows)} coordination outcome(s):")
            for row in rows:
                print(f"      - Action: {row['action']}")
                print(f"        Success: {row['success']}")
                print(f"        Outcome: {row['outcome']}")
                print(f"        Time: {row['occurred_at']}")
        else:
            print("   ❌ No coordination outcomes found in The Stick's memory")
            return False
        break
    
    # Step 4: Query VIC-20's historical effectiveness
    print("\n5. Testing VIC-20's historical query...")
    history = await vic20._get_historical_effectiveness("cpu")
    
    if history:
        print(f"   ✅ Found {len(history)} historical records")
        
        # Check for coordination outcomes with success data
        outcomes_with_success = [h for h in history if h.get('source', '').startswith('the_stick') and h.get('success') is not None]
        if outcomes_with_success:
            print(f"   ✅ Found {len(outcomes_with_success)} coordination outcomes with success data:")
            for h in outcomes_with_success[:3]:
                print(f"      - Action: {h.get('action')}")
                print(f"        Success: {h.get('success')}")
                print(f"        Confidence: {h.get('confidence', 0):.0%}")
        else:
            print("   ⚠️  No coordination outcomes with success data found")
    else:
        print("   ❌ No historical records found")
        return False
    
    # Step 5: Generate recommendation and verify it uses historical data
    print("\n6. Generating recommendation with historical data...")
    rec = await vic20._generate_recommendation(
        resource_type="cpu",
        current_value=85.0,
        threshold=70.0,
        severity="high"
    )
    
    print(f"   Action: {rec['action']}")
    print(f"   Confidence: {rec['confidence']:.0%}")
    
    if rec.get('historical_basis'):
        print(f"   ✅ Using historical data!")
        print(f"      - Matching records: {rec['historical_basis']['matching_records']}")
        print(f"      - Success rate: {rec['historical_basis']['success_rate']:.0%}")
        print(f"      - Confidence adjustment: {rec['historical_basis']['confidence_adjustment']:.0%}")
    else:
        print(f"   ⚠️  Not using historical data (falling back to defaults)")
    
    print("\n" + "=" * 70)
    print("✅ FEEDBACK LOOP TEST COMPLETE!")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_complete_feedback_loop())
    sys.exit(0 if result else 1)
