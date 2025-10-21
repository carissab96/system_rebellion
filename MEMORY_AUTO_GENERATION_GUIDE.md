# Memory Auto-Generation Guide

**Date:** October 20, 2025  
**Purpose:** How memories are automatically generated in System Rebellion

---

## 🎯 TL;DR - Memories ARE Auto-Generated

**Good news:** Memories are already being auto-generated! The system has multiple layers of automatic memory creation running in the background.

---

## 🔄 Auto-Generation Layers

### Layer 1: Real-Time Agent Processing (Immediate)

**Triggered by:** Incoming metrics via WebSocket  
**Frequency:** Every time metrics are received  
**What gets stored:**

1. **Sir Hawkington** (`triage_engine.py`)
   - ✅ Triage decisions (every metrics batch)
   - ✅ Monocle yeet incidents (when data quality fails)
   - ✅ Hawkington decisions (confidence, reasoning, system impact)
   - **Storage:** `SirHawkingtonMemoryBank` + `CentralMemoryBank` (dual-write)

2. **All Agents** (personality events)
   - ✅ Monocle yeets (Sir Hawkington)
   - ✅ Paper bag consumption (The Stick)
   - ✅ Beer consumption (Hamsters)
   - ✅ Shell spinning (Meth Snail)
   - ✅ Dimensional shifts (QSP)
   - ✅ Wisdom dispensing (VIC-20)
   - **Storage:** `AgentEventLog` table + WebSocket broadcast

**Code Location:**
```python
# backend/app/ai_agents/sir_hawkington/triage_engine.py
async def _store_triage_decision(self, user_id, triage_result):
    # Automatically stores triage decision
    await self.db.store_triage_decision(user_id, triage_data)

# backend/app/services/agent_event_logger.py
async def log_agent_event(..., broadcast: bool = True):
    # Automatically logs AND broadcasts personality events
```

---

### Layer 2: Background Tasks (Periodic)

**Started automatically on server startup** (`main.py` line 211-223)

#### Task 1: Metrics Aggregation (Hourly)
```python
# backend/app/core/background_tasks.py
async def run_metrics_aggregation():
    # Runs every hour
    # Aggregates raw metrics into hourly summaries
    # Cleans up old data (keeps 7 days)
    # Creates daily rollups at midnight
```

**What it does:**
- Aggregates metrics for all users
- Creates hourly summaries
- Performs daily rollups
- Cleans up old raw metrics

#### Task 2: Real-Time Optimization (Every 30 seconds)
```python
async def run_realtime_optimization():
    # Checks every 30 seconds
    # Processes recent metrics through agent manager
    # Triggers Meth Snail's optimization decisions
```

**What it does:**
- Monitors active users
- Gets last 5 minutes of metrics
- Processes through agent manager
- Executes urgent optimizations

#### Task 3: System Health Monitor (Every 60 seconds)
```python
async def run_system_health_monitor():
    # Checks every minute
    # Monitors overall system health
    # Coordinates between agents
```

#### Task 4: Memory Bank Metadata Scheduler (Every 5 minutes)
```python
# backend/app/core/learning_helpers.py
async def run_metadata_scheduler(engine, every_seconds=300):
    # Runs every 5 minutes (300 seconds)
    # Creates memory bank metadata rollups
    # Tracks learning effectiveness
```

**What it does:**
- Counts memories per agent
- Calculates learning transfer success rates
- Tracks The Stick's anxiety levels
- Creates health scores

---

## 📊 What Gets Auto-Generated

### Agent-Specific Memory Banks

Each agent has their own memory bank table that auto-populates:

1. **`sir_hawkington_memory_bank`**
   - Triage decisions
   - Data quality patterns
   - Monocle yeet incidents
   - Accuracy improvements
   - False positive reductions

2. **`the_stick_memory_bank`**
   - Eidetic memory storage
   - Anxiety levels
   - Paper bag consumption
   - Pattern storage events

3. **`hamsters_memory_bank`**
   - Infrastructure interventions
   - Beer consumption
   - Duct tape usage
   - Supply closet raids

4. **`meth_snail_memory_bank`**
   - RAM optimization decisions
   - Shell spinning events
   - Red Bull consumption
   - Jitter levels

5. **`quantum_shadow_people_memory_bank`**
   - Network anomaly detection
   - Dimensional shifts
   - Tequila jello shot consumption
   - Packet analysis

6. **`vic20_sage_memory_bank`**
   - Coordination decisions
   - Auto-tuner suggestions
   - Wisdom dispensing
   - Conflict mediation

### Central Memory Bank

**All agent memories are also written to:**
- `central_memory_bank` - Unified memory storage with cross-references

### Learning Tables (Auto-Populated)

1. **`agent_learning_interactions`**
   - When one agent learns from another
   - Transfer success tracking
   - Effectiveness scores

2. **`user_learning_patterns`**
   - User behavior patterns
   - Interaction preferences
   - Most effective agents

3. **`agent_global_patterns`**
   - System-wide patterns
   - Cross-user learnings
   - Promoted patterns

4. **`memory_bank_metadata`**
   - Rollup statistics
   - Health scores
   - Learning effectiveness

---

## ✅ How to Verify Auto-Generation is Working

### 1. Check Background Tasks are Running

**Look for these log messages on server startup:**
```
🚀 Starting up System Rebellion application...
✅ Database initialization successful
🔴 Redis connection established
🤖 AI Agents initialized
🔄 Background tasks started:
  🐌 Metrics aggregation engine running
  🐌💨 Real-time optimization engine engaged
  🏥 System health monitor active
  💾 Memory bank metadata scheduler running
```

### 2. Check Database for New Memories

**Query the database:**
```sql
-- Check Sir Hawkington's memories
SELECT COUNT(*), MAX(timestamp) 
FROM sir_hawkington_memory_bank 
WHERE user_id = 'YOUR_USER_ID';

-- Check central memory bank
SELECT agent_name, COUNT(*), MAX(occurred_at)
FROM central_memory_bank
WHERE user_id = 'YOUR_USER_ID'
GROUP BY agent_name;

-- Check agent events
SELECT agent_name, event_type, COUNT(*)
FROM agent_event_log
WHERE user_id = 'YOUR_USER_ID'
GROUP BY agent_name, event_type;
```

### 3. Check WebSocket Broadcasts

**Open browser console and watch for:**
- `agent_memory_update` - Memory bank updates (every 60s)
- `agent_event` - Personality moments (sporadic)
- `agent_insight` - Inter-agent communication (moderate)

### 4. Check Logs

**Backend logs should show:**
```
🧐✨ DUAL-WRITE SUCCESS: Triage normal stored
🧐💥 Monocle yeet stored - Missing: ['cpu_usage']
🐌 Meth Snail aggregated metrics for 1 users
📏 The Stick stored pattern in eidetic memory
```

---

## 🛠️ How to Trigger More Memory Generation

### Option 1: Send More Metrics (Immediate)

**Via WebSocket:**
```javascript
// Frontend sends metrics every few seconds
socket.emit('metrics', {
  cpu_usage: 45.2,
  memory_usage: 62.1,
  disk_usage: 78.5,
  timestamp: new Date().toISOString()
});
```

**Result:** Sir Hawkington processes immediately, stores triage decision

### Option 2: Adjust Background Task Frequency

**Edit `backend/app/core/background_tasks.py`:**

```python
# Change from hourly to every 5 minutes (for testing)
async def run_metrics_aggregation():
    # ...
    wait_seconds = 300  # 5 minutes instead of 1 hour
```

**Edit `backend/app/core/learning_helpers.py`:**

```python
# Change metadata scheduler from 5 minutes to 1 minute
async def run_metadata_scheduler(engine, every_seconds=60):  # Was 300
```

### Option 3: Manually Trigger Memory Storage

**Create a test script:**

```python
# backend/scripts/test_memory_generation.py
import asyncio
from app.core.database import AsyncSessionLocal
from app.ai_agents.sir_hawkington.database_integration import HawkingtonDatabaseIntegration
from datetime import datetime, timezone

async def test_memory_generation():
    db_integration = HawkingtonDatabaseIntegration()
    await db_integration.initialize()
    
    # Store a test triage decision
    triage_data = {
        'triage_severity': 'medium',
        'routing_decision': 'specialist',
        'target_agents': ['meth_snail'],
        'reasoning': 'Test memory generation',
        'confidence': 0.85,
        'timestamp': datetime.now(timezone.utc),
        'monocle_yeeted': False
    }
    
    memory_id = await db_integration.store_triage_decision(
        user_id='YOUR_USER_ID',
        triage_data=triage_data
    )
    
    print(f"✅ Test memory created: {memory_id}")

if __name__ == "__main__":
    asyncio.run(test_memory_generation())
```

**Run it:**
```bash
cd backend
python scripts/test_memory_generation.py
```

---

## 🔍 Troubleshooting

### Problem: No memories being generated

**Check:**
1. ✅ Backend server is running
2. ✅ Background tasks started (check logs)
3. ✅ Database tables exist (run migrations)
4. ✅ Metrics are being sent to WebSocket
5. ✅ User ID is valid

**Solution:**
```bash
# Check if background tasks are running
grep "Background tasks started" backend_logs.txt

# Check database
sqlite3 system_rebellion.db "SELECT COUNT(*) FROM central_memory_bank;"

# Restart server to reinitialize background tasks
cd backend
uvicorn main:app --reload
```

### Problem: Memories not showing in frontend

**Check:**
1. ✅ WebSocket connection established
2. ✅ `agent_memory_update` messages received
3. ✅ Redux state updated (check DevTools)
4. ✅ Agent cards consuming `display_data`

**Solution:**
```javascript
// Browser console
window.__REDUX_DEVTOOLS_EXTENSION__
// Check: state.agents.sir_hawkington.display_data
```

### Problem: Background tasks not running

**Check `main.py` lifespan function:**
```python
# Line 211-223 should have:
agent_tasks = await start_all_background_tasks()
background_tasks.extend(agent_tasks)

metadata_task = asyncio.create_task(
    run_metadata_scheduler(engine, every_seconds=300)
)
background_tasks.append(metadata_task)
```

**If missing, add it back!**

---

## 📈 Memory Generation Frequency

| Memory Type | Frequency | Trigger |
|------------|-----------|---------|
| Triage decisions | Every metrics batch | Metrics received |
| Personality events | Sporadic | When personality activates |
| Hourly aggregations | Every hour | Background task |
| Metadata rollups | Every 5 minutes | Background task |
| Real-time optimization | Every 30 seconds | Background task |
| Health monitoring | Every 60 seconds | Background task |

---

## 🎯 Expected Memory Volume

**For a typical user with metrics every 5 seconds:**

- **Per hour:** ~720 triage decisions
- **Per day:** ~17,280 triage decisions
- **Per week:** ~120,960 triage decisions

**Plus:**
- Hourly aggregations: 24/day
- Metadata rollups: 288/day (every 5 min)
- Personality events: Variable (depends on system state)

**Database growth:** ~1-2 MB per day per active user

---

## 🚀 Quick Start Checklist

To ensure auto-generation is working:

- [ ] Backend server running
- [ ] Check logs for "Background tasks started"
- [ ] Send test metrics via WebSocket
- [ ] Query database for new memories
- [ ] Watch browser console for `agent_memory_update`
- [ ] Verify agent cards display data

---

## 💡 Key Insight

**Memories are ALREADY auto-generating!** You don't need to set anything up. The system has been designed from the ground up to automatically:

1. Store every triage decision
2. Log every personality event
3. Track every learning interaction
4. Aggregate metrics periodically
5. Create metadata rollups
6. Monitor system health

**The agents are learning, storing, and evolving automatically.** You just need to send metrics and watch them work! 🧐✨

---

**Questions?** Check the logs, query the database, or watch the WebSocket messages to see the memories flowing in real-time.
