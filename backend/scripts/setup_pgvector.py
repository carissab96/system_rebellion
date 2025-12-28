#!/usr/bin/env python3
"""
Setup pgvector extension in PostgreSQL
Run this on the machine where PostgreSQL is running (Dell)
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def setup_pgvector():
    """Install and enable pgvector extension"""
    
    # Get database URL from environment
    db_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL") or "postgresql+asyncpg://carissab@localhost:5432/system_rebellion"
    
    print(f"🔗 Connecting to database...")
    print(f"   URL: {db_url[:50]}...")
    
    engine = create_async_engine(db_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Check if pgvector is already installed
            print("\n📦 Checking for pgvector extension...")
            result = await conn.execute(
                text("SELECT * FROM pg_extension WHERE extname = 'vector'")
            )
            existing = result.fetchone()
            
            if existing:
                print("✅ pgvector extension already installed!")
            else:
                print("⚠️  pgvector extension not found")
                print("📥 Installing pgvector extension...")
                
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    print("✅ pgvector extension installed successfully!")
                except Exception as e:
                    print(f"❌ Failed to install pgvector: {e}")
                    print()
                    print("🔧 Manual installation required:")
                    print("   On the database server (Dell), run:")
                    print("   1. sudo apt-get install postgresql-16-pgvector")
                    print("      (or appropriate version for your PostgreSQL)")
                    print("   2. Then run this script again")
                    return False
            
            # Test vector operations
            print("\n🧪 Testing vector operations...")
            await conn.execute(text("CREATE TEMP TABLE test_vectors (id int, embedding vector(3))"))
            await conn.execute(text("INSERT INTO test_vectors VALUES (1, '[1,2,3]'), (2, '[4,5,6]')"))
            result = await conn.execute(
                text("SELECT id, embedding <-> '[1,2,3]' AS distance FROM test_vectors ORDER BY distance")
            )
            rows = result.fetchall()
            print(f"✅ Vector operations working! Test query returned {len(rows)} rows")
            
            print("\n🎉 pgvector setup complete!")
            print()
            print("📊 Vector capabilities:")
            print("   - Cosine similarity: embedding <=> query")
            print("   - L2 distance: embedding <-> query")
            print("   - Inner product: embedding <#> query")
            print("   - HNSW index support: CREATE INDEX USING hnsw")
            print()
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(setup_pgvector())
    exit(0 if success else 1)
