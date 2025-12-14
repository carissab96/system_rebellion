"""
Diagnostic: Check if Triage Flow is Actually Happening
=======================================================

Checks the database to see if:
1. Hawkington is sending TRIAGE_ALERT messages
2. VIC-20 is receiving them and generating recommendations
3. Specialists are receiving COORDINATION_REQUEST messages
4. Specialists are sending ACTION_REPORT messages back
5. VIC-20 is logging coordination outcomes to The Stick

This helps diagnose where the feedback loop is breaking.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def check_triage_flow():
    """
    Check the database for evidence of the complete triage flow.
    """
    from app.core.database import get_async_db
    from sqlalchemy import text
    
    print("=" * 70)
    print("TRIAGE FLOW DIAGNOSTIC")
    print("=" * 70)
    
    async for session in get_async_db():
        # Check 1: Hawkington triage decisions
        print("\n1. Hawkington Triage Decisions (last 24 hours):")
        result = await session.execute(
            text("""
                SELECT 
                    decision_type,
                    metadata->>'resource_type' as resource_type,
                    metadata->>'severity' as severity,
                    created_at
                FROM agent_decision_vectors
                WHERE agent_name = 'sir_hawkington'
                    AND decision_type LIKE '%triage%'
                    AND created_at >= :cutoff
                ORDER BY created_at DESC
                LIMIT 10
            """),
            {"cutoff": datetime.now(timezone.utc) - timedelta(hours=24)}
        )
        rows = list(result.mappings())
        if rows:
            print(f"   Found {len(rows)} triage decisions:")
            for row in rows:
                print(f"   - {row['decision_type']}: {row['resource_type']} ({row['severity']}) at {row['created_at']}")
        else:
            print("   ⚠️  No triage decisions found - Hawkington may not be escalating")
        
        # Check 2: VIC-20 coordination decisions
        print("\n2. VIC-20 Coordination Decisions (last 24 hours):")
        result = await session.execute(
            text("""
                SELECT 
                    decision_type,
                    metadata->>'specialist' as specialist,
                    metadata->>'resource_type' as resource_type,
                    created_at
                FROM agent_decision_vectors
                WHERE agent_name = 'vic20_sage'
                    AND decision_type LIKE '%coordination%'
                    AND created_at >= :cutoff
                ORDER BY created_at DESC
                LIMIT 10
            """),
            {"cutoff": datetime.now(timezone.utc) - timedelta(hours=24)}
        )
        rows = list(result.mappings())
        if rows:
            print(f"   Found {len(rows)} coordination decisions:")
            for row in rows:
                print(f"   - {row['decision_type']}: routed to {row['specialist']} for {row['resource_type']} at {row['created_at']}")
        else:
            print("   ⚠️  No coordination decisions found - VIC-20 may not be receiving triage alerts")
        
        # Check 3: Specialist action decisions
        print("\n3. Specialist Actions (last 24 hours):")
        result = await session.execute(
            text("""
                SELECT 
                    agent_name,
                    decision_type,
                    metadata->>'action' as action,
                    metadata->>'followed_vic20' as followed_vic20,
                    created_at
                FROM agent_decision_vectors
                WHERE agent_name IN ('meth_snail', 'hamsters', 'quantum_shadow_people')
                    AND decision_type LIKE '%action%'
                    AND created_at >= :cutoff
                ORDER BY created_at DESC
                LIMIT 10
            """),
            {"cutoff": datetime.now(timezone.utc) - timedelta(hours=24)}
        )
        rows = list(result.mappings())
        if rows:
            print(f"   Found {len(rows)} specialist actions:")
            for row in rows:
                print(f"   - {row['agent_name']}: {row['action']} (followed VIC-20: {row['followed_vic20']}) at {row['created_at']}")
        else:
            print("   ⚠️  No specialist actions found - Specialists may not be receiving coordination requests")
        
        # Check 4: The Stick's decision logs
        print("\n4. The Stick's Decision Logs (last 24 hours):")
        result = await session.execute(
            text("""
                SELECT 
                    event_type,
                    details->'payload'->>'decision_type' as decision_type,
                    details->'payload'->>'from_agent' as from_agent,
                    occurred_at
                FROM central_memory_bank
                WHERE agent_name = 'the_stick'
                    AND event_type = 'decision_log'
                    AND occurred_at >= :cutoff
                ORDER BY occurred_at DESC
                LIMIT 10
            """),
            {"cutoff": datetime.now(timezone.utc) - timedelta(hours=24)}
        )
        rows = list(result.mappings())
        if rows:
            print(f"   Found {len(rows)} decision logs:")
            for row in rows:
                print(f"   - {row['decision_type']} from {row['from_agent']} at {row['occurred_at']}")
        else:
            print("   ⚠️  No decision logs found - The Stick may not be receiving logs")
        
        # Check 5: Coordination outcomes specifically
        print("\n5. Coordination Outcomes with Success Data:")
        result = await session.execute(
            text("""
                SELECT 
                    details->'payload'->>'action' as action,
                    details->'payload'->>'success' as success,
                    details->'payload'->>'outcome' as outcome,
                    occurred_at
                FROM central_memory_bank
                WHERE agent_name = 'the_stick'
                    AND event_type = 'decision_log'
                    AND details->'payload'->>'decision_type' = 'coordination_outcome'
                ORDER BY occurred_at DESC
                LIMIT 10
            """)
        )
        rows = list(result.mappings())
        if rows:
            print(f"   ✅ Found {len(rows)} coordination outcomes:")
            for row in rows:
                print(f"   - {row['action']}: success={row['success']}, outcome={row['outcome']}")
        else:
            print("   ❌ No coordination outcomes found - This is the missing piece!")
            print("      This means VIC-20 is NOT receiving ACTION_REPORT messages from specialists")
        
        break
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    result = asyncio.run(check_triage_flow())
    sys.exit(0 if result else 1)
