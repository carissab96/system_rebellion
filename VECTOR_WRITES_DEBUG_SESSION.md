# Vector Writes & Agent Database Integration - Debug Session
**Date:** November 28, 2025  
**Status:** In Progress - Resource monitor running, but no database writes yet

## 🎯 Original Problem
- Only VIC-20 writing to database (4,271 coordination decisions)
- Other agents (Hawkington, Meth Snail, Hamsters, QSP, Stick) silent since Nov 25
- **ZERO vector writes** to pgvector tables
- Vector tables existed in PostgreSQL but not accessible by application

---

## ✅ Issues Fixed Today

### 1. **Vector Tables Missing from SQLAlchemy** ✅ FIXED
**Problem:** Alembic migration created tables in PostgreSQL, but no SQLAlchemy models existed.

**Fix:**
- Created `/backend/app/models/vector_tables.py` with 3 models:
  - `AgentDecisionVectors` (decision embeddings)
  - `AgentPatternVectors` (pattern embeddings)
  - `AgentInteractionVectors` (interaction embeddings)
- Custom `Vector(UserDefinedType)` class for pgvector columns
- Fixed reserved word conflict: `context_metadata = Column("metadata", JSON)`
- Imported in `models/__init__.py`

**Result:** Snail now sees all 3 vector tables at startup ✅

---

### 2. **Broken db_getter Function** ✅ FIXED
**Problem:** `db_session_factory` was a nested closure function that:
- Returned `AsyncSessionLocal()` directly (not a generator)
- Lost context after lifespan initialization
- Couldn't be called by agents to get database sessions

**Fix:**
- Changed from custom factory to `get_async_db` from `app.core.database`
- Proper async generator that yields sessions with context management
- No closure issues, globally accessible

**File:** `/backend/main.py` line 225
```python
await initialize_distributed_agents(redis_url, db_getter=get_async_db)
```

**Result:** db_getter is now a valid function ✅

---

### 3. **Resource Monitor Never Started** ✅ FIXED
**Problem:** ResourceMonitor initialization had wrong parameters:
- Passing `redis_client` directly
- Expected: `agent_name`, `message_bus`, `check_interval`

**Fix:**
- Created `MessageBus(redis_client, agent_name="system_monitor")`
- Initialized ResourceMonitor with correct parameters
- Set check_interval=5.0 seconds

**File:** `/backend/app/ai_agents/distributed/distributed_agent_manager.py` lines 110-120

**Result:** Resource monitor starts without errors ✅

---

### 4. **Resource Monitor Only Sent Alerts on Threshold Exceeded** ✅ FIXED
**Problem:** Monitor only published when CPU > 80%, Memory > 85%, etc.
- Your system is healthy, so no messages sent
- Agents never received metrics, never made decisions

**Fix:**
- Added metric publishing **every interval** (not just on alerts)
- Publishes to `system.metrics` channel
- Uses `AgentMessage` with `MessageType.RESOURCE_ALERT`

**File:** `/backend/app/ai_agents/distributed/resource_monitor.py` lines 254-268

**Result:** Metrics published every 5 seconds ✅

---

### 5. **AgentMessage Parameter Errors** ✅ FIXED
**Problems:**
- Used `sender` instead of `from_agent`
- Used `data` instead of `payload`
- Called `publish_message()` instead of `publish()`

**Fixes:**
- Correct parameters: `from_agent`, `payload`
- Correct method: `message_bus.publish(message, channel)`

**Result:** No more initialization errors ✅

---

## ❓ Current Status - No Database Writes

**What's Working:**
- ✅ Backend starts without errors
- ✅ All agents initialize successfully
- ✅ Resource monitor starts and runs
- ✅ Vector tables registered in SQLAlchemy
- ✅ db_getter is valid function
- ✅ Redis pub/sub messages flowing

**What's NOT Working:**
- ❌ No database writes to PostgreSQL
- ❌ No vector writes to pgvector tables
- ❌ Agents not making decisions (no VIC-20 coordination messages)
- ❌ Only seeing Redis save operations

---

## 🔍 Next Steps to Investigate

### 1. **Are Agents Subscribed to system.metrics Channel?**
Check if agents are listening to the channel where metrics are published.

**Files to check:**
- `/backend/app/ai_agents/sir_hawkington/distributed_hawkington.py`
- `/backend/app/ai_agents/meth_snail/distributed_meth_snail.py`
- Look for: `subscribe()` or `register_handler()` calls

**Expected:** Agents should subscribe to `system.metrics` or `resource.*` channels

---

### 2. **Are Metrics Actually Being Published?**
Add LOUD logging to confirm metrics are being sent.

**Add to resource_monitor.py line 268:**
```python
print(f"\n📊 METRICS PUBLISHED TO REDIS")
print(f"   Channel: system.metrics")
print(f"   CPU: {metrics.cpu_percent}%")
print(f"   Memory: {metrics.memory_percent}%")
print(f"   Message ID: {metrics_message.message_id}\n")
```

---

### 3. **Are Agents Receiving Messages?**
Add logging in agent message handlers.

**Add to each agent's distributed file:**
```python
async def _handle_resource_alert(self, message: AgentMessage):
    print(f"\n🎯 {self.agent_name} RECEIVED METRICS!")
    print(f"   From: {message.from_agent}")
    print(f"   CPU: {message.payload.get('metrics', {}).get('cpu_percent')}%\n")
    # ... rest of handler
```

---

### 4. **Does VIC-20 Decision Engine Get Called?**
The loud logging we added should show:
```
================================================================================
🖥️ VIC-20 store_coordination_decision() CALLED for user <uuid>
================================================================================
```

**If you DON'T see this:** VIC-20's decision engine isn't being triggered at all.

**If you DO see this but no database writes:** The db_getter check is failing.

---

### 5. **Check Agent Decision Triggers**
Agents might need specific conditions to make decisions.

**Check:**
- Do agents need metrics above certain thresholds to decide?
- Do they need multiple metrics over time?
- Do they need user context?

**Files to check:**
- `/backend/app/ai_agents/vic_20_sage/decision_engine.py` - coordination logic
- `/backend/app/ai_agents/sir_hawkington/distributed_hawkington.py` - triage logic

---

## 📊 Diagnostic Commands

### Check if metrics are in Redis:
```bash
redis-cli
KEYS system.metrics*
GET <key_from_above>
```

### Check database for recent writes:
```bash
psql -U carissab -d system_rebellion
SELECT COUNT(*) FROM central_memory_bank WHERE created_at > NOW() - INTERVAL '10 minutes';
SELECT agent_name, COUNT(*) FROM central_memory_bank GROUP BY agent_name;
SELECT COUNT(*) FROM agent_decision_vectors;
```

### Watch backend logs for specific patterns:
```bash
# Watch for metrics publishing
tail -f backend.log | grep "Published metrics"

# Watch for agent message handling
tail -f backend.log | grep "RECEIVED METRICS"

# Watch for VIC-20 decisions
tail -f backend.log | grep "store_coordination_decision"

# Watch for database operations
tail -f backend.log | grep -i "insert\|update\|database"
```

---

## 🧪 Test Scripts Available

1. **`/backend/test_vector_system.py`** - Tests embedding generation and vector storage
2. **`/backend/test_db_writes.py`** - Queries database for recent writes
3. **`/backend/quick_db_check.py`** - Quick database health check
4. **`/backend/filter_logs.sh`** - Filters logs for important events
5. **`/backend/watch_db.sh`** - Real-time watch for DB operations

---

## 💡 Hypothesis for Next Session

**Most Likely Issue:** Agents are not subscribed to the `system.metrics` channel.

The resource monitor is publishing metrics, but if agents aren't listening to that specific channel, they'll never receive the messages and never make decisions.

**Quick Fix to Try:**
1. Check what channels agents are subscribed to
2. Either:
   - Change resource monitor to publish to agent-specific channels (e.g., `resource.cpu`, `resource.memory`)
   - OR ensure agents subscribe to `system.metrics`

---

## 📝 Files Modified Today

1. `/backend/app/models/vector_tables.py` - NEW
2. `/backend/app/models/__init__.py` - Import vector tables
3. `/backend/main.py` - Use get_async_db instead of factory
4. `/backend/app/ai_agents/distributed/distributed_agent_manager.py` - ResourceMonitor init
5. `/backend/app/ai_agents/distributed/resource_monitor.py` - Publish metrics every interval
6. `/backend/app/ai_agents/vic_20_sage/database_integration.py` - Debug logging

---

## 🎯 Success Criteria

When everything works, you should see:

1. **Every 5 seconds:**
   ```
   📊 Published metrics: CPU=25.3%, MEM=42.1%
   ```

2. **Agents responding:**
   ```
   🧐 Sir Hawkington analyzing CPU metrics...
   🐌 Meth Snail analyzing memory metrics...
   ```

3. **VIC-20 coordinating:**
   ```
   🖥️ VIC-20 store_coordination_decision() CALLED
   ✅ db_getter exists
   ✅ About to write to database...
   ```

4. **Database writes:**
   ```
   INSERT INTO central_memory_bank...
   INSERT INTO vic20_memory_bank...
   ```

5. **Vector writes:**
   ```
   🔮 Step 1: Creating decision text...
   🔮 Step 2: Getting embedding service...
   🔮 Step 3: Generating embedding...
   🔮 Step 4: Storing in vector DB...
   ✅✅✅ VECTOR WRITE SUCCESS!
   ```

---

## 🔧 Quick Restart Commands

```bash
cd /home/carissa/Documents/system_rebellion
git pull origin distributed-mixin-implementation

# Restart backend (adjust command as needed)
# pkill -f "uvicorn main:app"
# uvicorn main:app --reload
```

---

**Good luck! We're very close - the infrastructure is all in place, just need to connect the message routing.**
