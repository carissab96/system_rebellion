#!/usr/bin/env python3
"""
Migrate data from SQLite to PostgreSQL
System Rebellion Database Migration Script
"""
import asyncio
import sys
from sqlalchemy import create_engine, select, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URLs
SQLITE_URL = "sqlite:///./system_rebellion.db"
POSTGRES_URL = "postgresql+asyncpg://rebellion_user:ChangeThisPassword123!@localhost:5432/system_rebellion"

# Tables to migrate (in order to respect foreign keys)
TABLES_TO_MIGRATE = [
    'users',
    'central_memory_bank',
    'sir_hawkington_memory_bank',
    'the_stick_memory_bank',
    'meth_snail_memory_bank',
    'hamsters_memory_bank',
    'quantum_shadow_people_memory_bank',
    'vic20_sage_memory_bank',
    'agent_learning_interactions',
    'user_learning_patterns',
    'agent_global_patterns',
    'system_logs',
    # Add other tables as needed
]

async def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""
    
    # Create sync engine for SQLite (read)
    sqlite_engine = create_engine(SQLITE_URL, echo=False)
    SqliteSession = sessionmaker(bind=sqlite_engine)
    
    # Create async engine for PostgreSQL (write)
    postgres_engine = create_async_engine(POSTGRES_URL, echo=False)
    PostgresSession = sessionmaker(postgres_engine, class_=AsyncSession, expire_on_commit=False)
    
    logger.info("🚀 Starting migration from SQLite to PostgreSQL...")
    
    # Get metadata from SQLite
    metadata = MetaData()
    metadata.reflect(bind=sqlite_engine)
    
    total_migrated = 0
    
    try:
        async with PostgresSession() as pg_session:
            with SqliteSession() as sqlite_session:
                
                for table_name in TABLES_TO_MIGRATE:
                    if table_name not in metadata.tables:
                        logger.warning(f"⚠️  Table '{table_name}' not found in SQLite, skipping...")
                        continue
                    
                    table = metadata.tables[table_name]
                    
                    # Read all rows from SQLite
                    logger.info(f"📖 Reading from SQLite table: {table_name}")
                    rows = sqlite_session.execute(select(table)).fetchall()
                    
                    if not rows:
                        logger.info(f"   ℹ️  No data in {table_name}, skipping...")
                        continue
                    
                    logger.info(f"   Found {len(rows)} rows")
                    
                    # Convert rows to dictionaries
                    row_dicts = []
                    for row in rows:
                        row_dict = dict(row._mapping)
                        row_dicts.append(row_dict)
                    
                    # Insert into PostgreSQL
                    logger.info(f"💾 Writing to PostgreSQL table: {table_name}")
                    try:
                        # Use raw SQL for bulk insert
                        for row_dict in row_dicts:
                            stmt = table.insert().values(**row_dict)
                            await pg_session.execute(stmt)
                        
                        await pg_session.commit()
                        total_migrated += len(row_dicts)
                        logger.info(f"   ✅ Migrated {len(row_dicts)} rows")
                        
                    except Exception as e:
                        logger.error(f"   ❌ Error migrating {table_name}: {str(e)}")
                        await pg_session.rollback()
                        # Continue with next table
                        continue
        
        logger.info(f"\n🎉 Migration complete! Total rows migrated: {total_migrated}")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await postgres_engine.dispose()
        sqlite_engine.dispose()

async def verify_migration():
    """Verify that data was migrated correctly"""
    logger.info("\n🔍 Verifying migration...")
    
    sqlite_engine = create_engine(SQLITE_URL, echo=False)
    postgres_engine = create_async_engine(POSTGRES_URL, echo=False)
    
    metadata = MetaData()
    metadata.reflect(bind=sqlite_engine)
    
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(postgres_engine, class_=AsyncSession)
    
    try:
        async with PostgresSession() as pg_session:
            with SqliteSession() as sqlite_session:
                
                for table_name in TABLES_TO_MIGRATE:
                    if table_name not in metadata.tables:
                        continue
                    
                    table = metadata.tables[table_name]
                    
                    # Count rows in SQLite
                    sqlite_count = sqlite_session.execute(select(table)).fetchall()
                    sqlite_count = len(sqlite_count)
                    
                    # Count rows in PostgreSQL
                    pg_result = await pg_session.execute(select(table))
                    pg_count = len(pg_result.fetchall())
                    
                    status = "✅" if sqlite_count == pg_count else "❌"
                    logger.info(f"{status} {table_name}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
        
        logger.info("\n✅ Verification complete!")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
    finally:
        await postgres_engine.dispose()
        sqlite_engine.dispose()

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║  System Rebellion - SQLite to PostgreSQL Migration        ║
║  🧐 Sir Hawkington oversees the data transfer             ║
║  🐌 Meth Snail optimizes the migration process            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("\n⚠️  WARNING: This will copy data from SQLite to PostgreSQL")
    print("   Make sure PostgreSQL database is empty or you may get duplicates!\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Migration cancelled")
        sys.exit(0)
    
    # Run migration
    asyncio.run(migrate_data())
    
    # Verify
    verify = input("\nRun verification? (yes/no): ").strip().lower()
    if verify == 'yes':
        asyncio.run(verify_migration())
