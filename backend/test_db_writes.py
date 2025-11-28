#!/usr/bin/env python3
"""
Test if database writes are working at all
Directly queries PostgreSQL to see recent activity
"""

import asyncio
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, '/home/carissa/Documents/system_rebellion/backend')

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

async def check_recent_writes():
    """Check for recent database writes"""
    
    # Get database URL - try multiple sources
    db_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL")
    
    if not db_url:
        # Default for Dell (localhost since we're running ON the Dell)
        db_url = "postgresql+asyncpg://carissab@localhost:5432/system_rebellion"
    
    print("="*60)
    print("DATABASE WRITE CHECK")
    print("="*60)
    print(f"Database: {db_url}")
    print()
    print("Connecting...")
    print()
    
    engine = create_async_engine(db_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Check central_memory_bank
            print("📊 CENTRAL MEMORY BANK (last 10 entries):")
            result = await conn.execute(text("""
                SELECT 
                    memory_id,
                    agent_name,
                    event_type,
                    created_at,
                    priority
                FROM central_memory_bank 
                ORDER BY created_at DESC 
                LIMIT 10
            """))
            
            rows = result.fetchall()
            if rows:
                for row in rows:
                    print(f"  - {row[1]:20s} | {row[2]:30s} | {row[3]} | P{row[4]}")
            else:
                print("  ❌ NO ENTRIES FOUND")
            
            print()
            
            # Check agent-specific tables
            agent_tables = [
                'vic20_memory_bank',
                'sir_hawkington_memory_bank',
                'meth_snail_memory_bank',
                'hamsters_memory_bank',
                'the_stick_memory_bank',
                'quantum_shadow_people_memory_bank'
            ]
            
            for table in agent_tables:
                try:
                    result = await conn.execute(text(f"""
                        SELECT COUNT(*) as count, MAX(created_at) as last_write
                        FROM {table}
                    """))
                    row = result.fetchone()
                    count = row[0] if row else 0
                    last_write = row[1] if row and row[1] else "Never"
                    
                    status = "✅" if count > 0 else "❌"
                    print(f"{status} {table:35s}: {count:5d} entries | Last: {last_write}")
                except Exception as e:
                    print(f"❌ {table:35s}: Table error - {e}")
            
            print()
            
            # Check vector tables
            print("🔮 VECTOR TABLES:")
            vector_tables = [
                'agent_decision_vectors',
                'agent_pattern_vectors',
                'agent_interaction_vectors'
            ]
            
            for table in vector_tables:
                try:
                    result = await conn.execute(text(f"""
                        SELECT COUNT(*) as count, MAX(occurred_at) as last_write
                        FROM {table}
                    """))
                    row = result.fetchone()
                    count = row[0] if row else 0
                    last_write = row[1] if row and row[1] else "Never"
                    
                    status = "✅" if count > 0 else "❌"
                    print(f"{status} {table:35s}: {count:5d} entries | Last: {last_write}")
                except Exception as e:
                    print(f"⚠️  {table:35s}: {e}")
            
            print()
            
            # Check for writes in last 5 minutes
            five_min_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
            result = await conn.execute(text("""
                SELECT COUNT(*) as recent_count
                FROM central_memory_bank
                WHERE created_at > :cutoff
            """), {"cutoff": five_min_ago})
            
            recent = result.fetchone()[0]
            
            if recent > 0:
                print(f"✅ {recent} writes in last 5 minutes - SYSTEM IS ACTIVE")
            else:
                print(f"⚠️  NO writes in last 5 minutes - agents may not be making decisions")
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        print()
        print("Common issues:")
        print("1. Database not running: sudo systemctl status postgresql")
        print("2. Wrong password: Check .env file or use: psql -U carissab -d system_rebellion")
        print("3. Wrong host: Are you on the Dell? Use localhost. On HP? Use 192.168.1.127")
        print()
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(check_recent_writes())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
