# Dual-Write Integration Testing Strategy

## Overview

Comprehensive testing plan for the dual-write implementation across all 6 AI agents, ensuring data integrity, performance, and reliability.

## Test Categories

### 1. Unit Tests (Per Agent)

#### Test File Structure
```
backend/tests/dual_write/
├── test_sir_hawkington_dual_write.py
├── test_the_stick_dual_write.py
├── test_meth_snail_dual_write.py
├── test_hamsters_dual_write.py
├── test_quantum_shadow_people_dual_write.py
├── test_vic20_dual_write.py
└── test_dual_write_base.py (shared utilities)
```

#### Base Test Class
```python
# tests/dual_write/test_dual_write_base.py
import pytest
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.models.agent_memory_banks import CentralMemoryBank

class DualWriteTestBase:
    """Base class for dual-write testing"""
    
    @pytest.fixture
    async def db_session(self):
        """Provide clean database session for each test"""
        # Setup
        async with get_test_db() as session:
            yield session
        # Teardown
        await cleanup_test_data(session)
    
    async def verify_dual_write(
        self, 
        agent_table_model,
        central_memory_id: str,
        agent_memory_id: str,
        db_session
    ):
        """
        Verify both tables were written correctly
        
        Checks:
        1. Agent table record exists
        2. Central memory bank record exists
        3. Foreign key link is correct
        4. Timestamps are consistent
        5. No data duplication
        """
        # Check agent table
        agent_result = await db_session.execute(
            select(agent_table_model).where(
                agent_table_model.memory_id == agent_memory_id
            )
        )
        agent_record = agent_result.scalar_one_or_none()
        assert agent_record is not None, "Agent table record not found"
        
        # Check central memory bank
        cmb_result = await db_session.execute(
            select(CentralMemoryBank).where(
                CentralMemoryBank.memory_id == central_memory_id
            )
        )
        cmb_record = cmb_result.scalar_one_or_none()
        assert cmb_record is not None, "CMB record not found"
        
        # Verify foreign key link
        assert agent_record.central_memory_id == cmb_record.memory_id, \
            "Foreign key link broken"
        
        # Verify bidirectional reference
        assert cmb_record.agent_metadata.get('agent_memory_id') == agent_memory_id, \
            "Bidirectional reference missing"
        
        # Verify no data duplication
        self._verify_no_duplication(agent_record, cmb_record)
        
        return agent_record, cmb_record
    
    def _verify_no_duplication(self, agent_record, cmb_record):
        """Ensure CMB only has summary, not full structured data"""
        # CMB should NOT have full structured fields
        cmb_details = cmb_record.details or {}
        
        # These should be in agent table, not CMB details
        prohibited_fields = [
            'data_quality_pattern',
            'triage_decision_context',
            'quality_threshold_adjustment',
            'optimization_pattern',
            'anxiety_pattern',
            'compliance_tracking'
        ]
        
        for field in prohibited_fields:
            assert field not in cmb_details, \
                f"Structured field '{field}' duplicated in CMB"
```

#### Sir Hawkington Tests
```python
# tests/dual_write/test_sir_hawkington_dual_write.py
import pytest
from app.ai_agents.sir_hawkington.database_integration import HawkingtonDatabaseIntegration
from app.ai_agents.sir_hawkington.data_types import HawkingtonDecision
from app.models.agent_memory_banks import SirHawkingtonMemoryBank
from .test_dual_write_base import DualWriteTestBase

class TestSirHawkingtonDualWrite(DualWriteTestBase):
    
    @pytest.mark.asyncio
    async def test_store_decision_dual_write(self, db_session):
        """Test dual-write for aristocratic decisions"""
        db = HawkingtonDatabaseIntegration()
        await db.initialize()
        
        decision = HawkingtonDecision(
            decision_id="test-decision-001",
            decision_type="concern",
            confidence=0.85,
            reasoning="Test decision",
            metrics={
                'cpu_usage': 75.5,
                'memory_usage': 68.2,
                'disk_usage': 45.0
            },
            timestamp=datetime.now(timezone.utc),
            user_id="test-user-001",
            system_impact="monitoring_recommended"
        )
        
        # Execute dual-write
        central_memory_id = await db.store_decision("test-user-001", decision)
        
        # Verify both tables
        agent_record, cmb_record = await self.verify_dual_write(
            SirHawkingtonMemoryBank,
            central_memory_id,
            cmb_record.agent_metadata['agent_memory_id'],
            db_session
        )
        
        # Verify Hawkington-specific fields
        assert agent_record.memory_category == "quality_analysis"
        assert agent_record.data_quality_pattern is not None
        assert agent_record.accuracy_improvement is not None
    
    @pytest.mark.asyncio
    async def test_store_triage_decision_dual_write(self, db_session):
        """Test dual-write for triage decisions"""
        # Similar structure to above
        pass
    
    @pytest.mark.asyncio
    async def test_store_monocle_yeet_dual_write(self, db_session):
        """Test dual-write for monocle yeet incidents"""
        # Similar structure to above
        pass
    
    @pytest.mark.asyncio
    async def test_validation_errors(self, db_session):
        """Test that validation errors are raised correctly"""
        db = HawkingtonDatabaseIntegration()
        await db.initialize()
        
        # Missing required field
        decision = HawkingtonDecision(
            decision_id="",  # Invalid
            decision_type="concern",
            confidence=0.85,
            reasoning="Test",
            timestamp=datetime.now(timezone.utc),
            user_id="test-user-001"
        )
        
        with pytest.raises(ValueError, match="Missing decision_id"):
            await db.store_decision("test-user-001", decision)
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, db_session):
        """Test that failed writes rollback correctly"""
        # Simulate database error during CMB write
        # Verify agent table write is also rolled back
        pass
```

### 2. Integration Tests (Cross-Agent)

```python
# tests/integration/test_dual_write_integration.py
import pytest
from app.ai_agents.agent_manager import get_agent_manager

class TestDualWriteIntegration:
    
    @pytest.mark.asyncio
    async def test_all_agents_dual_write(self, db_session):
        """Test that all 6 agents can write simultaneously"""
        manager = await get_agent_manager()
        
        # Create test data for each agent
        tasks = [
            self._test_hawkington_write(),
            self._test_stick_write(),
            self._test_snail_write(),
            self._test_hamsters_write(),
            self._test_qsp_write(),
            self._test_vic20_write()
        ]
        
        # Execute all writes concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all succeeded
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), \
                f"Agent {i} failed: {result}"
    
    @pytest.mark.asyncio
    async def test_foreign_key_integrity(self, db_session):
        """Test FK constraints are enforced"""
        # Try to delete CMB record with agent table reference
        # Should fail due to FK constraint
        pass
    
    @pytest.mark.asyncio
    async def test_concurrent_writes_same_user(self, db_session):
        """Test multiple agents writing for same user concurrently"""
        # Simulate realistic scenario: multiple agents processing
        # metrics for the same user at the same time
        pass
```

### 3. Performance Tests

```python
# tests/performance/test_dual_write_performance.py
import pytest
import time
from statistics import mean, stdev

class TestDualWritePerformance:
    
    @pytest.mark.asyncio
    async def test_write_latency(self, db_session):
        """Measure dual-write latency"""
        db = HawkingtonDatabaseIntegration()
        await db.initialize()
        
        latencies = []
        for i in range(100):
            decision = self._create_test_decision(f"test-{i}")
            
            start = time.time()
            await db.store_decision("test-user", decision)
            latency = (time.time() - start) * 1000  # ms
            
            latencies.append(latency)
        
        # Verify acceptable performance
        avg_latency = mean(latencies)
        p95_latency = sorted(latencies)[95]
        
        assert avg_latency < 50, f"Average latency too high: {avg_latency}ms"
        assert p95_latency < 100, f"P95 latency too high: {p95_latency}ms"
        
        print(f"Average latency: {avg_latency:.2f}ms")
        print(f"P95 latency: {p95_latency:.2f}ms")
        print(f"Std dev: {stdev(latencies):.2f}ms")
    
    @pytest.mark.asyncio
    async def test_query_performance_comparison(self, db_session):
        """Compare query speed: agent table vs CMB JSON parsing"""
        # Insert 1000 test records
        await self._insert_test_data(1000)
        
        # Query 1: Agent table (structured)
        start = time.time()
        result = await db_session.execute(
            select(SirHawkingtonMemoryBank)
            .where(SirHawkingtonMemoryBank.user_id == "test-user")
            .where(SirHawkingtonMemoryBank.accuracy_improvement > 0.5)
            .order_by(SirHawkingtonMemoryBank.timestamp.desc())
            .limit(100)
        )
        agent_table_time = (time.time() - start) * 1000
        
        # Query 2: CMB (JSON parsing)
        start = time.time()
        result = await db_session.execute(
            select(CentralMemoryBank)
            .where(CentralMemoryBank.agent_name == "sir_hawkington")
            .where(CentralMemoryBank.user_id == "test-user")
            # Can't filter on JSON fields efficiently
        )
        records = result.scalars().all()
        # Filter in Python (slow)
        filtered = [r for r in records if r.details.get('accuracy_improvement', 0) > 0.5]
        cmb_time = (time.time() - start) * 1000
        
        speedup = cmb_time / agent_table_time
        print(f"Agent table query: {agent_table_time:.2f}ms")
        print(f"CMB query: {cmb_time:.2f}ms")
        print(f"Speedup: {speedup:.1f}x")
        
        assert speedup >= 10, f"Expected 10x+ speedup, got {speedup:.1f}x"
    
    @pytest.mark.asyncio
    async def test_bulk_write_performance(self, db_session):
        """Test performance with bulk writes"""
        # Write 1000 records
        # Measure throughput (records/second)
        pass
```

### 4. Data Integrity Tests

```python
# tests/integrity/test_dual_write_integrity.py
class TestDualWriteIntegrity:
    
    @pytest.mark.asyncio
    async def test_no_fake_data(self, db_session):
        """Verify no fake data is written"""
        db = HawkingtonDatabaseIntegration()
        await db.initialize()
        
        # Create decision with minimal data
        decision = HawkingtonDecision(
            decision_id="test-001",
            decision_type="concern",
            confidence=0.85,
            reasoning="Test",
            timestamp=datetime.now(timezone.utc),
            user_id="test-user",
            metrics=None  # No metrics provided
        )
        
        central_memory_id = await db.store_decision("test-user", decision)
        
        # Verify agent table record
        result = await db_session.execute(
            select(SirHawkingtonMemoryBank).where(
                SirHawkingtonMemoryBank.central_memory_id == central_memory_id
            )
        )
        agent_record = result.scalar_one()
        
        # Verify None values, not fake data
        assert agent_record.data_quality_pattern is None or \
               all(v is None or v is False for v in agent_record.data_quality_pattern.values())
        assert agent_record.false_positive_reduction is None
    
    @pytest.mark.asyncio
    async def test_timestamp_consistency(self, db_session):
        """Verify timestamps are consistent across tables"""
        # Write record
        # Verify occurred_at matches timestamp
        # Verify created_at is close to occurred_at
        pass
    
    @pytest.mark.asyncio
    async def test_data_consistency_after_failure(self, db_session):
        """Verify data consistency after partial failure"""
        # Simulate failure during CMB write
        # Verify agent table is rolled back
        # Verify no orphaned records
        pass
```

### 5. Load Tests

```python
# tests/load/test_dual_write_load.py
import pytest
import asyncio
from locust import User, task, between

class DualWriteLoadTest(User):
    wait_time = between(1, 3)
    
    @task
    def write_decision(self):
        """Simulate agent writing decision"""
        # Create realistic decision
        # Write to database
        # Measure response time
        pass
    
    @task(3)  # 3x more frequent
    def query_agent_table(self):
        """Simulate querying agent table"""
        # Query structured data
        # Measure response time
        pass
```

## Test Execution Plan

### Phase 1: Unit Tests (Week 1)
```bash
# Run all unit tests
pytest tests/dual_write/ -v --cov=app/ai_agents --cov-report=html

# Expected coverage: >90%
```

### Phase 2: Integration Tests (Week 2)
```bash
# Run integration tests
pytest tests/integration/ -v --cov-append

# Test with real database
pytest tests/integration/ --db=postgresql
```

### Phase 3: Performance Tests (Week 3)
```bash
# Run performance benchmarks
pytest tests/performance/ -v --benchmark-only

# Generate performance report
pytest tests/performance/ --benchmark-json=benchmark.json
```

### Phase 4: Load Tests (Week 4)
```bash
# Run load tests
locust -f tests/load/test_dual_write_load.py --headless \
  --users 100 --spawn-rate 10 --run-time 10m

# Monitor system resources during load test
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/dual_write_tests.yml
name: Dual-Write Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run dual-write tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/dual_write/ -v --cov=app/ai_agents
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Success Criteria

### Must Pass
- ✅ All unit tests pass (100%)
- ✅ Foreign key integrity maintained
- ✅ No fake data in any field
- ✅ Transaction rollback works correctly
- ✅ Query performance 10x+ faster on agent tables

### Should Pass
- ✅ Average write latency < 50ms
- ✅ P95 write latency < 100ms
- ✅ 100 concurrent users without errors
- ✅ No memory leaks during load test
- ✅ Test coverage > 90%

### Nice to Have
- ✅ 1000 concurrent users supported
- ✅ Query performance 50x+ faster
- ✅ Average write latency < 20ms

## Monitoring in Production

### Metrics to Track
```python
# Add to agent database integrations
from prometheus_client import Counter, Histogram

dual_write_success = Counter(
    'dual_write_success_total',
    'Total successful dual writes',
    ['agent', 'event_type']
)

dual_write_failure = Counter(
    'dual_write_failure_total',
    'Total failed dual writes',
    ['agent', 'event_type', 'error_type']
)

dual_write_latency = Histogram(
    'dual_write_latency_seconds',
    'Dual write latency',
    ['agent', 'event_type']
)
```

### Alerts
```yaml
# alerts/dual_write.yml
groups:
  - name: dual_write
    rules:
      - alert: DualWriteFailureRate
        expr: rate(dual_write_failure_total[5m]) > 0.01
        annotations:
          summary: "High dual-write failure rate"
      
      - alert: DualWriteLatency
        expr: dual_write_latency_seconds{quantile="0.95"} > 0.1
        annotations:
          summary: "High dual-write latency (P95 > 100ms)"
```

---

**Status**: Ready for implementation  
**Estimated Time**: 4 weeks (1 week per phase)  
**Dependencies**: Database migrations, Redis setup
