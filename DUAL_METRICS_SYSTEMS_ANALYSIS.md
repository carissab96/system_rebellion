# Dual Metrics Systems Analysis
**Date:** November 30, 2025  
**Issue:** Two separate metrics systems running simultaneously

---

## 🔍 The Two Systems

### System 1: WebSocket Metrics (Original)
**File:** `/backend/app/api/simplified_websocket_routes.py`  
**Endpoint:** `/ws/system-metrics`  
**Purpose:** Send system metrics to **frontend** for Observatory visualization

**What it does:**
- Collects system metrics (CPU, memory, disk, network) using `psutil`
- Sends to frontend via WebSocket every 5 seconds
- Also sends agent roster and agent memory bank data from database
- **Target:** Frontend Observatory UI

**Flow:**
```
SimplifiedMetricsService → WebSocket → Frontend Observatory
```

**Does NOT:**
- Send metrics to AI agents
- Trigger agent decision-making
- Write to database (only reads agent memories)

---

### System 2: Distributed Agent Metrics (Dell's System)
**File:** `/backend/app/ai_agents/distributed/resource_monitor.py`  
**Channel:** `agents:resources:alerts` (Redis pub/sub)  
**Purpose:** Send system metrics to **AI agents** for decision-making

**What it does:**
- Collects system metrics (CPU, memory, disk, network) using `psutil`
- Publishes to Redis channel `agents:resources:alerts` every 5 seconds
- **Target:** AI agents (Sir Hawkington, Meth Snail, VIC-20, etc.)

**Flow:**
```
ResourceMonitor → Redis pub/sub → AI Agents → Decisions → Database
```

**Does:**
- Trigger agent decision-making
- Cause agents to write to database
- Enable agent coordination

---

## 🤔 Are They Conflicting?

**NO - They serve different purposes!**

| Aspect | WebSocket System | Distributed System |
|--------|------------------|-------------------|
| **Target** | Frontend UI | AI Agents |
| **Transport** | WebSocket | Redis pub/sub |
| **Purpose** | Visualization | Decision-making |
| **Writes DB** | No (reads only) | Yes (via agents) |
| **Frequency** | 5 seconds | 5 seconds |

**They're complementary:**
- WebSocket shows you what's happening (Observatory)
- Distributed system makes agents act on what's happening

---

## 🐛 Current Problem

**Agents are receiving metrics but NOT making decisions or writing to database.**

**Evidence:**
- ✅ Resource monitor publishing metrics every 5 seconds
- ✅ Agents subscribed to `agents:resources:alerts`
- ❌ No agent decision messages
- ❌ No database writes
- ❌ No VIC-20 coordination

**Hypothesis:** Agents receive metrics but their decision logic isn't triggered by regular metrics - only by threshold violations or specific conditions.

---

## 🔍 Next Steps to Debug

### 1. Check if Agents Are Actually Receiving Messages

**Look for in logs:**
```
🎯 SIR_HAWKINGTON RECEIVED RESOURCE ALERT!
🎯 METH_SNAIL RECEIVED RESOURCE ALERT!
🎯 VIC_20_SAGE RECEIVED RESOURCE ALERT!
```

**If you see these:** Agents are receiving, but not acting.  
**If you don't see these:** Subscription still broken.

---

### 2. Check Agent Decision Logic

Agents might only make decisions when:
- Metrics exceed thresholds (CPU > 80%, Memory > 85%)
- Specific patterns detected
- User activity present
- Multiple metrics over time

**Files to check:**
- `/backend/app/ai_agents/sir_hawkington/distributed_hawkington.py`
- `/backend/app/ai_agents/vic_20_sage/decision_engine.py`
- `/backend/app/ai_agents/meth_snail/distributed_meth_snail.py`

Look for conditions like:
```python
if metrics.cpu_percent > self.threshold:
    # Make decision
```

---

### 3. Force a Decision Test

**Option A: Lower thresholds**
Make agents respond to normal metrics:
```python
# In resource_monitor.py
self.thresholds = {
    ResourceType.CPU: 10.0,      # Was 80.0
    ResourceType.MEMORY: 10.0,   # Was 85.0
    ResourceType.DISK: 10.0,     # Was 90.0
}
```

**Option B: Manually trigger VIC-20**
Call VIC-20's coordination directly to test database writes:
```python
# Test script
from app.ai_agents.vic_20_sage.database_integration import VIC20DatabaseIntegration

db_integration = VIC20DatabaseIntegration(db_getter=get_async_db)
await db_integration.store_coordination_decision(
    user_id="test-user",
    decision={
        "decision_type": "test",
        "reasoning": "Manual test",
        "priority": 5
    }
)
```

---

### 4. Check for Silent Failures

Add more logging to agent decision handlers:

```python
async def _handle_resource_alert(self, message: AgentMessage):
    print(f"🎯 {self.agent_name} RECEIVED METRICS")
    
    # Check if we should make a decision
    metrics = message.payload.get('metrics', {})
    cpu = metrics.get('cpu_percent', 0)
    
    print(f"   CPU: {cpu}%")
    print(f"   Should I act? {self._should_make_decision(metrics)}")
    
    if self._should_make_decision(metrics):
        print(f"   ✅ Making decision!")
        await self.make_decision(metrics)
    else:
        print(f"   ⏸️ Not acting - conditions not met")
```

---

## 📊 How to Check Logs on Dell

Since backend runs on Dell server, you need to SSH in and check logs:

```bash
# SSH to Dell
ssh carissab@dell-server

# Find the backend process
ps aux | grep uvicorn

# Check recent logs (if using systemd)
journalctl -u system-rebellion-backend -n 100 --no-pager

# Or if running in tmux/screen
tmux attach -t backend
# or
screen -r backend

# Grep for specific patterns
# (assuming logs go to stdout/stderr)
tail -f /path/to/backend.log | grep -E "RECEIVED|PUBLISHING|store_coordination"
```

---

## 🎯 Expected Behavior When Working

### Every 5 seconds:
```
📊 RESOURCE MONITOR PUBLISHING METRICS
   CPU: 25.3%
   Memory: 42.1%
✅ Publish result: True
```

### Agents receive:
```
🎯 SIR_HAWKINGTON RECEIVED RESOURCE ALERT!
   CPU: 25.3%
   Memory: 42.1%

🎯 METH_SNAIL RECEIVED RESOURCE ALERT!
   CPU: 25.3%
   Memory: 42.1%
```

### Agents decide (when conditions met):
```
🧐 Sir Hawkington: CPU within normal range, no action needed
🐌 Meth Snail: Memory usage acceptable, continuing optimization
```

### OR when thresholds exceeded:
```
🧐 Sir Hawkington: CPU at 85%! Analyzing workload...
🖥️ VIC-20: Coordinating response to high CPU...
🖥️ VIC-20 store_coordination_decision() CALLED
✅ db_getter exists
✅ About to write to database...
INSERT INTO central_memory_bank...
🔮 ATTEMPTING VECTOR WRITE...
✅ VECTOR WRITE SUCCESS!
```

---

## 💡 Recommendation

**Keep both systems** - they serve different purposes:

1. **WebSocket system** → Frontend visualization (Observatory)
2. **Distributed system** → Agent decision-making and coordination

**But we need to:**
1. Confirm agents are receiving messages
2. Understand why they're not making decisions
3. Either lower thresholds OR add logic to respond to normal metrics
4. Verify database writes work when decisions are made

---

## 🔧 Quick Test Commands

### Check if Redis is receiving messages:
```bash
redis-cli
SUBSCRIBE agents:resources:alerts
# Should see messages every 5 seconds
```

### Check database for recent writes:
```bash
psql -U carissab -d system_rebellion
SELECT COUNT(*) FROM central_memory_bank WHERE created_at > NOW() - INTERVAL '10 minutes';
SELECT agent_name, COUNT(*) FROM central_memory_bank GROUP BY agent_name;
```

### Check if agents are active:
```bash
redis-cli
KEYS agents:*
GET agents:sir_hawkington:state
GET agents:vic_20_sage:state
```

---

**Next:** Confirm agents are receiving messages, then investigate why they're not acting on them.
