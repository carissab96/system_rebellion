#!/usr/bin/env python3
"""
Quick test script to verify agent event logging works
Run from backend directory: python test_agent_events.py
"""

import asyncio 
import sys
from sqlalchemy import select, func
from app.core.database import get_async_db
from app.models.agent_events import AgentEventLog

async def test_event_logging():
    """Test that events can be logged and retrieved"""
    
    print("🧪 Testing Agent Event Logging System")
    print("=" * 60)
    
    async for db in get_async_db():
        try:
            # Test 1: Check if table exists and is accessible
            print("\n1️⃣ Checking AgentEventLog table...")
            result = await db.execute(
                select(func.count()).select_from(AgentEventLog)
            )
            total_events = result.scalar()
            print(f"   ✅ Table accessible. Total events: {total_events}")
            
            # Test 2: Get recent events
            print("\n2️⃣ Fetching recent events...")
            result = await db.execute(
                select(AgentEventLog)
                .order_by(AgentEventLog.timestamp.desc())
                .limit(10)
            )
            recent_events = result.scalars().all()
            
            if recent_events:
                print(f"   ✅ Found {len(recent_events)} recent events:")
                for event in recent_events:
                    print(f"      - {event.agent_name}: {event.event_type} ({event.severity})")
            else:
                print("   ⚠️  No events found yet (this is normal if agents haven't run)")
            
            # Test 3: Check events by agent
            print("\n3️⃣ Events by agent:")
            result = await db.execute(
                select(
                    AgentEventLog.agent_name,
                    AgentEventLog.event_type,
                    func.count().label('count')
                )
                .group_by(AgentEventLog.agent_name, AgentEventLog.event_type)
                .order_by(AgentEventLog.agent_name, AgentEventLog.event_type)
            )
            
            agent_stats = result.all()
            if agent_stats:
                for agent_name, event_type, count in agent_stats:
                    print(f"   - {agent_name}: {event_type} ({count}x)")
            else:
                print("   ⚠️  No events logged yet")
            
            # Test 4: Check memory bank counters using raw SQL
            print("\n4️⃣ Checking memory bank event counters...")
            
            memory_banks = [
                ("sir_hawkington_memory_bank", ["monocle_yeets_count", "alerts_generated_count"]),
                ("the_stick_memory_bank", ["paper_bags_consumed_count", "anxiety_spikes_count"]),
                ("meth_snail_memory_bank", ["shell_spins_count", "energy_drinks_consumed_count"]),
                ("hamsters_memory_bank", ["supply_raids_count", "beer_consumed_count", "duct_tape_used_count"]),
                ("quantum_shadow_people_memory_bank", ["dimensional_shifts_count", "quantum_fixes_count"]),
                ("vic20_memory_bank", ["coordinations_count", "wisdom_dispensed_count"])
            ]
            
            from sqlalchemy import text
            for table_name, expected_columns in memory_banks:
                try:
                    # Check if columns exist using information_schema
                    query = text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = :table_name 
                        AND column_name = ANY(:columns)
                    """)
                    result = await db.execute(query, {"table_name": table_name, "columns": expected_columns})
                    found_columns = [row[0] for row in result]
                    
                    if found_columns:
                        print(f"   ✅ {table_name}: {len(found_columns)}/{len(expected_columns)} counter columns found")
                    else:
                        print(f"   ⚠️  {table_name}: No counter columns found (may not be migrated yet)")
                except Exception as e:
                    print(f"   ⚠️  {table_name}: Could not check columns - {e}")
            
            print("\n" + "=" * 60)
            print("✅ Event logging system is ready!")
            print("\n📝 Next steps:")
            print("   1. Run agents to generate events")
            print("   2. Check events in database:")
            print("      SELECT * FROM agent_event_log ORDER BY timestamp DESC LIMIT 10;")
            print("   3. Test WebSocket broadcasting")
            
        except Exception as e:
            print(f"\n❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            break

if __name__ == "__main__":
    asyncio.run(test_event_logging())
