# Dual-Write Migration Strategy

## Overview

Strategy for migrating existing Central Memory Bank (CMB) data to agent-specific tables while maintaining system availability and data integrity.

## Current State Assessment

### Data Inventory
```sql
-- Check existing CMB records by agent
SELECT 
    agent_name,
    COUNT(*) as total_records,
    MIN(occurred_at) as earliest_record,
    MAX(occurred_at) as latest_record,
    AVG(LENGTH(details::text)) as avg_details_size
FROM central_memory_bank
GROUP BY agent_name
ORDER BY total_records DESC;
```

### Expected Results
```
agent_name              | total_records | earliest_record | latest_record | avg_details_size
------------------------|---------------|-----------------|---------------|------------------
sir_hawkington          | 15,234        | 2024-01-15      | 2025-10-13    | 2,456
the_stick               | 8,912         | 2024-02-01      | 2025-10-13    | 1,823
meth_snail              | 6,543         | 2024-02-15      | 2025-10-13    | 3,102
hamsters                | 12,456        | 2024-01-20      | 2025-10-13    | 2,789
quantum_shadow_people   | 4,321         | 2024-03-01      | 2025-10-13    | 4,567
vic20_sage              | 3,210         | 2024-03-15      | 2025-10-13    | 1,234
```

## Migration Approaches

### Option 1: Big Bang Migration (NOT RECOMMENDED)
**Pros**: Simple, complete cutover  
**Cons**: Downtime required, high risk, no rollback

### Option 2: Gradual Migration (RECOMMENDED)
**Pros**: Zero downtime, testable, reversible  
**Cons**: More complex, temporary dual-read overhead

### Option 3: Hybrid Approach (BEST)
**Pros**: Combines benefits of both  
**Cons**: Requires careful coordination

## Recommended Strategy: Phased Hybrid Migration

### Phase 0: Preparation (Week 1)

#### 1. Backup Everything
```bash
# PostgreSQL backup
pg_dump -h localhost -U postgres system_rebellion > backup_pre_migration_$(date +%Y%m%d).sql

# SQLite backup
cp system_rebellion.db system_rebellion_backup_$(date +%Y%m%d).db

# Verify backup
pg_restore --list backup_pre_migration_*.sql | head -20
```

#### 2. Create Migration Tables
```sql
-- Track migration progress
CREATE TABLE migration_progress (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    total_records INTEGER NOT NULL,
    migrated_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, completed, failed
    error_log TEXT
);

-- Track individual record migrations
CREATE TABLE migration_log (
    id SERIAL PRIMARY KEY,
    central_memory_id VARCHAR(36) NOT NULL,
    agent_memory_id VARCHAR(36),
    agent_name VARCHAR(50) NOT NULL,
    migration_status VARCHAR(20), -- success, failed, skipped
    error_message TEXT,
    migrated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_migration_log_cmb_id ON migration_log(central_memory_id);
CREATE INDEX idx_migration_log_agent ON migration_log(agent_name, migration_status);
```

#### 3. Analyze Data Quality
```python
# backend/scripts/analyze_migration_data.py
import asyncio
from sqlalchemy import select, func
from app.core.database import get_async_db
from app.models.agent_memory_banks import CentralMemoryBank

async def analyze_data_quality():
    """Analyze CMB data to identify migration challenges"""
    async with get_async_db() as db:
        # Check for missing required fields
        result = await db.execute(
            select(
                CentralMemoryBank.agent_name,
                func.count(CentralMemoryBank.id).label('total'),
                func.sum(
                    func.case(
                        (CentralMemoryBank.details.is_(None), 1),
                        else_=0
                    )
                ).label('missing_details'),
                func.sum(
                    func.case(
                        (CentralMemoryBank.occurred_at.is_(None), 1),
                        else_=0
                    )
                ).label('missing_timestamp')
            )
            .group_by(CentralMemoryBank.agent_name)
        )
        
        print("Data Quality Analysis:")
        for row in result:
            print(f"{row.agent_name}:")
            print(f"  Total: {row.total}")
            print(f"  Missing details: {row.missing_details}")
            print(f"  Missing timestamp: {row.missing_timestamp}")
            print(f"  Quality: {((row.total - row.missing_details) / row.total * 100):.1f}%")

asyncio.run(analyze_data_quality())
```

### Phase 1: Deploy Dual-Write Code (Week 2)

#### 1. Deploy New Code (Already Done ✅)
- All 6 agents have dual-write implementation
- New writes go to both tables
- Old data remains in CMB only

#### 2. Monitor New Writes
```python
# Add monitoring to database_integration.py
from prometheus_client import Counter, Histogram

dual_write_counter = Counter(
    'dual_write_operations_total',
    'Total dual-write operations',
    ['agent', 'status']
)

@with_monitoring
async def store_decision(self, user_id: str, decision: HawkingtonDecision) -> str:
    try:
        result = await self._store_decision_impl(user_id, decision)
        dual_write_counter.labels(agent='sir_hawkington', status='success').inc()
        return result
    except Exception as e:
        dual_write_counter.labels(agent='sir_hawkington', status='failure').inc()
        raise
```

#### 3. Verify Dual-Write Working
```bash
# Check that new records are in both tables
psql -d system_rebellion -c "
SELECT 
    cmb.agent_name,
    COUNT(DISTINCT cmb.memory_id) as cmb_records,
    COUNT(DISTINCT shm.memory_id) as agent_records,
    COUNT(DISTINCT shm.central_memory_id) as linked_records
FROM central_memory_bank cmb
LEFT JOIN sir_hawkington_memory_bank shm ON cmb.memory_id = shm.central_memory_id
WHERE cmb.created_at > NOW() - INTERVAL '1 day'
GROUP BY cmb.agent_name;
"
```

### Phase 2: Backfill Historical Data (Week 3-4)

#### Migration Script Architecture
```python
# backend/scripts/migrate_historical_data.py
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class HistoricalDataMigrator:
    """Migrate historical CMB data to agent-specific tables"""
    
    def __init__(self, batch_size: int = 100, dry_run: bool = False):
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    async def migrate_agent(
        self, 
        agent_name: str,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        """Migrate all records for a specific agent"""
        logger.info(f"Starting migration for {agent_name}")
        
        # Get total count
        count_query = select(func.count(CentralMemoryBank.id)).where(
            CentralMemoryBank.agent_name == agent_name
        )
        if start_date:
            count_query = count_query.where(CentralMemoryBank.occurred_at >= start_date)
        if end_date:
            count_query = count_query.where(CentralMemoryBank.occurred_at <= end_date)
        
        result = await db.execute(count_query)
        total_records = result.scalar()
        
        logger.info(f"Found {total_records} records to migrate for {agent_name}")
        
        # Process in batches
        offset = 0
        while offset < total_records:
            batch = await self._get_batch(db, agent_name, offset, start_date, end_date)
            await self._process_batch(db, agent_name, batch)
            
            offset += self.batch_size
            progress = (offset / total_records) * 100
            logger.info(f"Progress: {progress:.1f}% ({offset}/{total_records})")
            
            # Commit after each batch
            if not self.dry_run:
                await db.commit()
    
    async def _get_batch(
        self,
        db: AsyncSession,
        agent_name: str,
        offset: int,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ):
        """Get a batch of records to migrate"""
        query = (
            select(CentralMemoryBank)
            .where(CentralMemoryBank.agent_name == agent_name)
            .order_by(CentralMemoryBank.occurred_at)
            .offset(offset)
            .limit(self.batch_size)
        )
        
        if start_date:
            query = query.where(CentralMemoryBank.occurred_at >= start_date)
        if end_date:
            query = query.where(CentralMemoryBank.occurred_at <= end_date)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _process_batch(
        self,
        db: AsyncSession,
        agent_name: str,
        batch: list
    ):
        """Process a batch of records"""
        for cmb_record in batch:
            try:
                # Check if already migrated
                if await self._is_migrated(db, cmb_record.memory_id):
                    self.stats['skipped'] += 1
                    continue
                
                # Extract and transform data
                agent_record = await self._transform_record(agent_name, cmb_record)
                
                if agent_record is None:
                    # Record cannot be migrated (missing required data)
                    self.stats['skipped'] += 1
                    await self._log_migration(
                        db, cmb_record.memory_id, agent_name, 
                        'skipped', 'Missing required data'
                    )
                    continue
                
                # Insert into agent table
                if not self.dry_run:
                    db.add(agent_record)
                    await db.flush()
                
                self.stats['success'] += 1
                await self._log_migration(
                    db, cmb_record.memory_id, agent_name,
                    'success', None, agent_record.memory_id
                )
                
            except Exception as e:
                self.stats['failed'] += 1
                logger.error(f"Failed to migrate {cmb_record.memory_id}: {e}")
                await self._log_migration(
                    db, cmb_record.memory_id, agent_name,
                    'failed', str(e)
                )
    
    async def _is_migrated(self, db: AsyncSession, central_memory_id: str) -> bool:
        """Check if record already migrated"""
        result = await db.execute(
            select(migration_log).where(
                and_(
                    migration_log.c.central_memory_id == central_memory_id,
                    migration_log.c.migration_status == 'success'
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def _transform_record(
        self,
        agent_name: str,
        cmb_record: CentralMemoryBank
    ) -> Optional[Any]:
        """Transform CMB record to agent-specific format"""
        if agent_name == 'sir_hawkington':
            return await self._transform_hawkington(cmb_record)
        elif agent_name == 'the_stick':
            return await self._transform_stick(cmb_record)
        elif agent_name == 'meth_snail':
            return await self._transform_snail(cmb_record)
        elif agent_name == 'hamsters':
            return await self._transform_hamsters(cmb_record)
        elif agent_name == 'quantum_shadow_people':
            return await self._transform_qsp(cmb_record)
        elif agent_name == 'vic20_sage':
            return await self._transform_vic20(cmb_record)
        else:
            logger.warning(f"Unknown agent: {agent_name}")
            return None
    
    async def _transform_hawkington(
        self,
        cmb_record: CentralMemoryBank
    ) -> Optional[SirHawkingtonMemoryBank]:
        """Transform CMB record to Hawkington format"""
        details = cmb_record.details or {}
        
        # Extract required fields
        if not details.get('decision_type'):
            return None  # Cannot migrate without decision type
        
        # Determine memory category
        event_type = cmb_record.event_type
        if 'triage' in event_type:
            category = 'triage'
        elif 'monocle_yeet' in event_type:
            category = 'monocle_yeet'
        else:
            category = 'quality_analysis'
        
        # Build data quality pattern from available data
        data_quality_pattern = None
        if 'metrics' in details:
            metrics = details['metrics']
            data_quality_pattern = {
                'cpu_valid': metrics.get('cpu_usage') is not None,
                'memory_valid': metrics.get('memory_usage') is not None,
                'disk_valid': metrics.get('disk_usage') is not None
            }
        
        # Build triage context
        triage_context = {
            'decision_type': details.get('decision_type'),
            'system_impact': details.get('system_impact'),
            'confidence': cmb_record.numeric_value
        }
        
        return SirHawkingtonMemoryBank(
            memory_id=str(uuid.uuid4()),
            user_id=cmb_record.user_id,
            timestamp=cmb_record.occurred_at,
            memory_category=category,
            data_quality_pattern=data_quality_pattern,
            triage_decision_context=triage_context,
            accuracy_improvement=None,  # Historical data doesn't have this
            false_positive_reduction=None,
            shared_with_central=True,
            central_memory_id=cmb_record.memory_id
        )
    
    async def _log_migration(
        self,
        db: AsyncSession,
        central_memory_id: str,
        agent_name: str,
        status: str,
        error_message: Optional[str],
        agent_memory_id: Optional[str] = None
    ):
        """Log migration result"""
        if self.dry_run:
            return
        
        await db.execute(
            migration_log.insert().values(
                central_memory_id=central_memory_id,
                agent_memory_id=agent_memory_id,
                agent_name=agent_name,
                migration_status=status,
                error_message=error_message
            )
        )

# CLI interface
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate historical CMB data')
    parser.add_argument('--agent', help='Specific agent to migrate')
    parser.add_argument('--batch-size', type=int, default=100)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    migrator = HistoricalDataMigrator(
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )
    
    async with get_async_db() as db:
        if args.agent:
            await migrator.migrate_agent(args.agent, db)
        else:
            # Migrate all agents
            agents = [
                'sir_hawkington',
                'the_stick',
                'meth_snail',
                'hamsters',
                'quantum_shadow_people',
                'vic20_sage'
            ]
            for agent in agents:
                await migrator.migrate_agent(agent, db)
    
    print("\nMigration Statistics:")
    print(f"Total: {migrator.stats['total']}")
    print(f"Success: {migrator.stats['success']}")
    print(f"Failed: {migrator.stats['failed']}")
    print(f"Skipped: {migrator.stats['skipped']}")

if __name__ == '__main__':
    asyncio.run(main())
```

#### Running the Migration

**Dry Run First**:
```bash
# Test migration without writing
python backend/scripts/migrate_historical_data.py --dry-run

# Test specific agent
python backend/scripts/migrate_historical_data.py --agent sir_hawkington --dry-run

# Test date range
python backend/scripts/migrate_historical_data.py \
  --agent sir_hawkington \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --dry-run
```

**Production Migration**:
```bash
# Migrate one agent at a time
python backend/scripts/migrate_historical_data.py --agent sir_hawkington

# Monitor progress
watch -n 5 'psql -d system_rebellion -c "SELECT * FROM migration_progress"'

# Check for errors
psql -d system_rebellion -c "
SELECT agent_name, migration_status, COUNT(*) 
FROM migration_log 
GROUP BY agent_name, migration_status;
"
```

### Phase 3: Validation (Week 5)

#### 1. Data Integrity Checks
```sql
-- Verify all records migrated
SELECT 
    cmb.agent_name,
    COUNT(DISTINCT cmb.memory_id) as cmb_total,
    COUNT(DISTINCT ml.central_memory_id) as migrated,
    COUNT(DISTINCT cmb.memory_id) - COUNT(DISTINCT ml.central_memory_id) as remaining
FROM central_memory_bank cmb
LEFT JOIN migration_log ml ON cmb.memory_id = ml.central_memory_id 
    AND ml.migration_status = 'success'
GROUP BY cmb.agent_name;

-- Verify foreign key links
SELECT 
    'sir_hawkington' as agent,
    COUNT(*) as broken_links
FROM sir_hawkington_memory_bank shm
LEFT JOIN central_memory_bank cmb ON shm.central_memory_id = cmb.memory_id
WHERE cmb.memory_id IS NULL

UNION ALL

SELECT 
    'the_stick' as agent,
    COUNT(*) as broken_links
FROM the_stick_memory_bank tsm
LEFT JOIN central_memory_bank cmb ON tsm.central_memory_id = cmb.memory_id
WHERE cmb.memory_id IS NULL;
-- ... repeat for all agents
```

#### 2. Query Performance Validation
```python
# backend/scripts/validate_migration_performance.py
import asyncio
import time
from sqlalchemy import select

async def benchmark_queries():
    """Compare query performance before/after migration"""
    
    async with get_async_db() as db:
        # Query 1: Agent table (new way)
        start = time.time()
        result = await db.execute(
            select(SirHawkingtonMemoryBank)
            .where(SirHawkingtonMemoryBank.user_id == 'test-user')
            .where(SirHawkingtonMemoryBank.accuracy_improvement > 0.5)
            .limit(100)
        )
        agent_time = time.time() - start
        
        # Query 2: CMB (old way)
        start = time.time()
        result = await db.execute(
            select(CentralMemoryBank)
            .where(CentralMemoryBank.agent_name == 'sir_hawkington')
            .where(CentralMemoryBank.user_id == 'test-user')
        )
        records = result.scalars().all()
        # Filter in Python
        filtered = [r for r in records 
                   if r.details.get('accuracy_improvement', 0) > 0.5][:100]
        cmb_time = time.time() - start
        
        print(f"Agent table: {agent_time*1000:.2f}ms")
        print(f"CMB: {cmb_time*1000:.2f}ms")
        print(f"Speedup: {cmb_time/agent_time:.1f}x")

asyncio.run(benchmark_queries())
```

### Phase 4: Cutover (Week 6)

#### 1. Update Query Code
```python
# BEFORE (queries CMB):
async def get_historical_decisions(user_id: str):
    result = await db.execute(
        select(CentralMemoryBank)
        .where(CentralMemoryBank.agent_name == 'sir_hawkington')
        .where(CentralMemoryBank.user_id == user_id)
    )
    return result.scalars().all()

# AFTER (queries agent table):
async def get_historical_decisions(user_id: str):
    result = await db.execute(
        select(SirHawkingtonMemoryBank)
        .where(SirHawkingtonMemoryBank.user_id == user_id)
        .order_by(SirHawkingtonMemoryBank.timestamp.desc())
    )
    return result.scalars().all()
```

#### 2. Deploy Updated Code
```bash
# Deploy with feature flag
export USE_AGENT_TABLES=true

# Gradual rollout
# 10% of users
# 50% of users
# 100% of users
```

#### 3. Monitor Performance
```python
# Add monitoring
from prometheus_client import Histogram

query_latency = Histogram(
    'agent_table_query_latency_seconds',
    'Agent table query latency',
    ['agent', 'query_type']
)

@query_latency.labels(agent='sir_hawkington', query_type='historical').time()
async def get_historical_decisions(user_id: str):
    # ... query code
```

### Phase 5: Cleanup (Week 7+)

#### 1. Archive Old CMB Data
```sql
-- Create archive table
CREATE TABLE central_memory_bank_archive AS
SELECT * FROM central_memory_bank
WHERE created_at < '2025-10-01';

-- Verify archive
SELECT COUNT(*) FROM central_memory_bank_archive;

-- Delete archived records (after verification)
DELETE FROM central_memory_bank
WHERE created_at < '2025-10-01'
AND memory_id IN (
    SELECT central_memory_id 
    FROM migration_log 
    WHERE migration_status = 'success'
);
```

#### 2. Drop Migration Tables
```sql
-- After successful migration and verification
DROP TABLE migration_log;
DROP TABLE migration_progress;
```

## Rollback Plan

### If Migration Fails

#### 1. Stop Migration
```bash
# Kill migration process
pkill -f migrate_historical_data.py

# Check what was migrated
psql -d system_rebellion -c "SELECT * FROM migration_progress"
```

#### 2. Rollback Agent Tables
```sql
-- Delete migrated records
DELETE FROM sir_hawkington_memory_bank
WHERE memory_id IN (
    SELECT agent_memory_id 
    FROM migration_log 
    WHERE migration_status = 'success'
);

-- Repeat for all agents
```

#### 3. Restore from Backup
```bash
# If needed, restore entire database
pg_restore -d system_rebellion backup_pre_migration_*.sql
```

### If Performance Degrades

#### 1. Revert to CMB Queries
```python
# Feature flag to switch back
if os.getenv('USE_AGENT_TABLES') == 'false':
    # Use old CMB queries
    return await query_cmb(user_id)
else:
    # Use new agent table queries
    return await query_agent_table(user_id)
```

#### 2. Add Missing Indexes
```sql
-- If queries are slow, add indexes
CREATE INDEX idx_hawkington_user_timestamp 
ON sir_hawkington_memory_bank(user_id, timestamp DESC);

CREATE INDEX idx_hawkington_category_timestamp
ON sir_hawkington_memory_bank(memory_category, timestamp DESC);
```

## Timeline Summary

| Week | Phase | Activities | Success Criteria |
|------|-------|------------|------------------|
| 1 | Preparation | Backup, analyze, create migration tables | Backups verified, data quality assessed |
| 2 | Deploy | Deploy dual-write code, monitor | New writes in both tables, no errors |
| 3-4 | Backfill | Migrate historical data | 95%+ records migrated successfully |
| 5 | Validation | Verify integrity, benchmark performance | No broken links, 10x+ speedup |
| 6 | Cutover | Update queries, gradual rollout | All queries use agent tables |
| 7+ | Cleanup | Archive old data, drop migration tables | CMB cleaned up, system optimized |

## Risk Mitigation

### Risk 1: Data Loss
**Mitigation**: 
- Full backups before migration
- Dry run testing
- Batch processing with rollback
- Migration logging

### Risk 2: Performance Degradation
**Mitigation**:
- Benchmark before/after
- Gradual rollout with feature flags
- Monitoring and alerts
- Quick rollback plan

### Risk 3: Downtime
**Mitigation**:
- Zero-downtime migration strategy
- Dual-write during transition
- No service interruption

### Risk 4: Foreign Key Violations
**Mitigation**:
- Validate FK links after each batch
- Automated integrity checks
- Repair scripts ready

## Success Metrics

- ✅ 100% of records migrated or accounted for
- ✅ 0 broken foreign key links
- ✅ 10x+ query performance improvement
- ✅ 0 downtime during migration
- ✅ <1% error rate during migration

---

**Status**: Ready for execution  
**Estimated Duration**: 7 weeks  
**Risk Level**: Medium (with mitigation)  
**Rollback Time**: <1 hour
