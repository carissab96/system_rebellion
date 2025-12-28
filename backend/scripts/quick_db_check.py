#!/usr/bin/env python3
"""
Quick database check - just the essentials
"""

import asyncio
import sys
sys.path.insert(0, '/home/carissa/Documents/system_rebellion/backend')

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os

async def quick_check():
    db_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL") or "postgresql+asyncpg://carissab@localhost:5432/system_rebellion"
    
    print("Quick Database Check")
    print("=" * 60)
    
    engine = create_async_engine(db_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Just get the last 10 entries
            result = await conn.execute(text("""
                SELECT agent_name, event_type, created_at
                FROM central_memory_bank 
                ORDER BY created_at DESC 
                LIMIT 10
            """))
            
            rows = result.fetchall()
            
            if rows:
                print(f"\n✅ Found {len(rows)} recent entries:\n")
                for i, row in enumerate(rows, 1):
                    print(f"{i}. {row[0]:20s} | {row[1]:30s} | {row[2]}")
            else:
                print("\n❌ No entries in central_memory_bank")
                print("   Agents are NOT making decisions!")
            
            # Count total
            result = await conn.execute(text("SELECT COUNT(*) FROM central_memory_bank"))
            total = result.fetchone()[0]
            print(f"\nTotal entries: {total}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(quick_check())
