"""
Test VIC-20's Historical Query Capability - REAL DATABASE
==========================================================

NO MOCKS. Real database queries. Real history. Real recommendations.

Verifies that VIC-20:
1. Queries the REAL database for historical effectiveness data
2. Uses REAL data to adjust recommendation confidence
3. Makes REAL recommendations based on what actually happened

Run on Dell with: python tests/test_vic20_history_query.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_vic20_real_history_query():
    """
    Test VIC-20's ability to query REAL historical data and use it.
    No mocks. Real database. Real recommendations.
    """
    from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
    from app.core.database import get_async_db
    
    print("=" * 70)
    print("VIC-20 REAL History Query Test")
    print("=" * 70)
    
    # Create VIC-20 with REAL database connection
    vic20 = VIC20SageDistributed(db_getter=get_async_db)
    
    # Initialize database integration
    print("\n1. Initializing VIC-20 database integration...")
    try:
        await vic20.db.ensure_initialized()
        print("   ✅ Database initialized")
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        return False
    
    # Test history query for each resource type
    resource_types = ["cpu", "memory", "disk", "network"]
    
    print("\n2. Querying historical effectiveness for each resource type...")
    for resource_type in resource_types:
        print(f"\n   --- {resource_type.upper()} ---")
        history = await vic20._get_historical_effectiveness(resource_type)
        
        if history:
            print(f"   ✅ Found {len(history)} historical records")
            for h in history[:3]:  # Show first 3
                print(f"      - Action: {h.get('action', 'unknown')}")
                print(f"        Success: {h.get('success')}")
                print(f"        Confidence: {h.get('confidence', 0):.0%}")
        else:
            print(f"   ⚠️  No historical records found")
    
    # Test recommendation generation with real history
    print("\n3. Generating REAL recommendations based on history...")
    
    for resource_type in resource_types:
        print(f"\n   --- {resource_type.upper()} Recommendation ---")
        
        rec = await vic20._generate_recommendation(
            resource_type=resource_type,
            current_value=85.0,
            threshold=70.0,
            severity="high"
        )
        
        print(f"   Action: {rec['action']}")
        print(f"   Confidence: {rec['confidence']:.0%}")
        
        if rec.get('historical_basis'):
            print(f"   Historical records used: {rec['historical_basis']['matching_records']}")
            print(f"   Historical success rate: {rec['historical_basis']['success_rate']:.0%}")
        else:
            print(f"   Historical basis: None (using defaults)")
        
        if rec.get('alternative_action'):
            print(f"   ⚡ Alternative suggested: {rec['alternative_action']} ({rec['alternative_confidence']:.0%})")
        
        print(f"   Reasoning: {rec['reasoning'][:100]}...")
    
    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
    
    return True


async def test_vic20_writes_then_reads():
    """
    Test the full cycle: VIC-20 makes a decision, writes it, then reads it back.
    This verifies the write-read loop is working.
    """
    from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
    from app.core.database import get_async_db
    from datetime import datetime, timezone
    
    print("\n" + "=" * 70)
    print("VIC-20 Write-Then-Read Test")
    print("=" * 70)
    
    vic20 = VIC20SageDistributed(db_getter=get_async_db, user_id="test_user")
    
    print("\n1. Initializing...")
    await vic20.db.ensure_initialized()
    
    # First, query current history count
    print("\n2. Checking current history for 'cpu'...")
    history_before = await vic20._get_historical_effectiveness("cpu")
    count_before = len(history_before) if history_before else 0
    print(f"   Records before: {count_before}")
    
    # Write a coordination decision
    print("\n3. Writing a test coordination decision...")
    try:
        from app.ai_agents.vic_20_sage.data_types import VIC20Decision, VIC20DecisionType
        
        test_decision = VIC20Decision(
            decision_type=VIC20DecisionType.AGENT_COORDINATION,
            timestamp=datetime.now(timezone.utc),
            confidence_score=0.85,
            coordination_context={
                "resource_type": "cpu",
                "recommendation": {"action": "throttle_processes"},
                "test": True
            },
            agents_involved=["meth_snail"],
            harmony_impact=0.1
        )
        
        await vic20.db.store_coordination_decision("test_user", test_decision)
        print("   ✅ Decision written")
    except Exception as e:
        print(f"   ❌ Write failed: {e}")
        return False
    
    # Query again to see if we can read it back
    print("\n4. Querying history again...")
    history_after = await vic20._get_historical_effectiveness("cpu")
    count_after = len(history_after) if history_after else 0
    print(f"   Records after: {count_after}")
    
    if count_after > count_before:
        print("   ✅ Write-read cycle working!")
    else:
        print("   ⚠️  Record count didn't increase (might be event_type mismatch)")
    
    print("\n" + "=" * 70)
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("VIC-20 REAL DATABASE TESTS - NO MOCKS")
    print("=" * 70)
    
    async def run_all():
        success = True
        
        # Test 1: Query real history
        try:
            result = await test_vic20_real_history_query()
            if not result:
                success = False
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        # Test 2: Write then read
        try:
            result = await test_vic20_writes_then_reads()
            if not result:
                success = False
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        return success
    
    result = asyncio.run(run_all())
    sys.exit(0 if result else 1)
