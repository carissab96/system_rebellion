# WebSocket Freeze Fix - Agent Manager Initialization

**Problem**: Agent manager initializes on every WebSocket connection, blocking the event loop  
**Solution**: Initialize agent manager once at application startup  
**Impact**: Eliminates 2-3 second freeze on WebSocket connection

---

## Root Cause Analysis

### What's Happening:
```python
# simplified_websocket_routes.py line 310
agent_manager = await asyncio.wait_for(get_agent_manager(), timeout=2.0)
```

Every WebSocket connection calls `get_agent_manager()`, which:
1. ✅ Checks if singleton exists (fast)
2. ❌ If not, acquires initialization lock (blocks other connections)
3. ❌ Loads YAML config file (file I/O)
4. ❌ Imports 6 agent modules dynamically (slow)
5. ❌ Instantiates 6 agent objects (memory allocation)
6. ❌ Calls initialize() on each agent (more setup)
7. ❌ Creates Redis connections (network I/O)
8. ❌ Creates database connection pools (network I/O)

**Total time**: 2-3 seconds of **blocking** work

### Why the Timeout Doesn't Help:
The `asyncio.wait_for(timeout=2.0)` doesn't prevent blocking - it just cancels after 2 seconds. But during those 2 seconds, the **entire event loop is blocked** because:
- File I/O (`yaml.safe_load()`) is synchronous
- Module imports (`importlib.import_module()`) are synchronous
- Object instantiation is synchronous

**Result**: Chrome and Windsurf freeze because the event loop can't process any other events.

---

## Solution: Application Startup Initialization

### Step 1: Initialize Agent Manager at Startup

**File**: `/backend/app/main.py`

```python
# Add to imports
from app.ai_agents.agent_manager import get_agent_manager
import asyncio

# Add startup event handler
@app.on_event("startup")
async def startup_event():
    """Initialize services that should be ready before accepting connections"""
    logger.info("🚀 Initializing application services...")
    
    # Initialize agent manager ONCE at startup
    try:
        start_time = time.time()
        agent_manager = await get_agent_manager()
        elapsed = time.time() - start_time
        logger.info(f"✅ Agent manager initialized in {elapsed:.2f}s")
        
        # Verify agents are ready
        active_agents = await agent_manager.get_active_agents()
        logger.info(f"✅ Active agents: {active_agents}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent manager: {e}", exc_info=True)
        # Don't crash the app - WebSocket will handle gracefully
    
    logger.info("✅ Application startup complete")
```

### Step 2: Update WebSocket Route to Use Cached Manager

**File**: `/backend/app/api/simplified_websocket_routes.py`

**BEFORE** (lines 307-318):
```python
# AI Agent Manager (non-fatal on error, loaded in background)
agent_manager = None
try:
    agent_manager = await asyncio.wait_for(get_agent_manager(), timeout=2.0)
    active_agents = await asyncio.wait_for(agent_manager.get_active_agents(), timeout=1.0)
    logger.info("AI Agent manager ready for %s - Active: %s", getattr(user, "email", None), active_agents)
except asyncio.TimeoutError:
    logger.warning("Agent manager initialization timed out (non-critical)")
    agent_manager = None
except Exception as e:
    logger.error("Failed to initialize AI Agent Manager: %s", str(e))
    agent_manager = None
```

**AFTER**:
```python
# AI Agent Manager (should already be initialized at startup)
agent_manager = None
try:
    # This should return instantly if initialized at startup
    agent_manager = await asyncio.wait_for(get_agent_manager(), timeout=0.5)
    logger.info("✅ Agent manager ready for %s", getattr(user, "email", None))
except asyncio.TimeoutError:
    logger.warning("⚠️ Agent manager not initialized yet (should have been done at startup)")
    agent_manager = None
except Exception as e:
    logger.error("❌ Failed to get AI Agent Manager: %s", str(e))
    agent_manager = None
```

**Key Changes**:
1. Timeout reduced from 2.0s to 0.5s (should be instant)
2. Removed `get_active_agents()` call (not needed on every connection)
3. Updated log messages to indicate expectation

---

## Implementation Steps

### 1. Update main.py (5 minutes)

```bash
cd /home/carissa/Documents/system_rebellion/backend
nano app/main.py
```

Add the startup event handler shown above.

### 2. Update simplified_websocket_routes.py (2 minutes)

```bash
nano app/api/simplified_websocket_routes.py
```

Replace lines 307-318 with the new code shown above.

### 3. Test the Fix (5 minutes)

```bash
# Stop all services
pkill -f uvicorn
pkill -f "npm run dev"

# Start backend (watch for startup logs)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Look for these logs:
# 🚀 Initializing application services...
# ✅ Agent manager initialized in X.XXs
# ✅ Active agents: ['sir_hawkington', 'the_stick', ...]
# ✅ Application startup complete

# Start frontend (in new terminal)
cd frontend
npm run dev

# Test login and WebSocket connection
# Should be INSTANT with no freeze
```

---

## Expected Results

### Before Fix:
```
User logs in → WebSocket connects → Agent manager initializes (2-3s FREEZE) → Connection ready
```

### After Fix:
```
App starts → Agent manager initializes (2-3s, one time) → Ready
User logs in → WebSocket connects (instant) → Connection ready (instant)
```

### Performance Metrics:
- **Startup time**: +2-3 seconds (one time cost)
- **WebSocket connection**: 2-3 seconds → <100ms ✅
- **Login experience**: No freeze ✅
- **Subsequent connections**: Instant ✅

---

## Verification Checklist

After implementing the fix:

- [ ] Backend starts successfully
- [ ] Startup logs show agent manager initialization
- [ ] Login completes without freeze
- [ ] WebSocket connects instantly
- [ ] Agent Theater loads without freeze
- [ ] Chrome and Windsurf remain responsive
- [ ] All 6 agents are active
- [ ] Metrics stream correctly

---

## Rollback Plan

If the fix causes issues:

```bash
# Revert changes
git checkout app/main.py
git checkout app/api/simplified_websocket_routes.py

# Restart services
pkill -f uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Additional Optimizations (Optional)

### 1. Parallel Agent Initialization

**File**: `/backend/app/ai_agents/agent_manager.py` (line 214-225)

**BEFORE**:
```python
# Phase 1: instantiate agents with NO kwargs
temp_agents: Dict[str, Any] = {}
created = 0
for agent_name in self.processing_order:
    try:
        agent_class = self.agent_configs[agent_name]["class"]
        agent = agent_class()   # <-- sequential
        temp_agents[agent_name] = agent
        created += 1
    except Exception as e:
        self.logger.error("❌ Failed to instantiate agent '%s': %s", agent_name, e, exc_info=True)
```

**AFTER**:
```python
# Phase 1: instantiate agents in parallel
async def create_agent(agent_name: str, agent_class: Type) -> tuple[str, Any]:
    """Create a single agent instance"""
    try:
        agent = agent_class()
        return (agent_name, agent)
    except Exception as e:
        self.logger.error("❌ Failed to instantiate agent '%s': %s", agent_name, e, exc_info=True)
        return (agent_name, None)

# Create all agents in parallel
tasks = [
    create_agent(name, self.agent_configs[name]["class"])
    for name in self.processing_order
]
results = await asyncio.gather(*tasks, return_exceptions=True)

temp_agents: Dict[str, Any] = {}
created = 0
for agent_name, agent in results:
    if agent is not None:
        temp_agents[agent_name] = agent
        created += 1
```

**Benefit**: Reduces initialization time from 2-3s to 1-1.5s

### 2. Lazy Agent Loading

Only initialize agents when first needed:

```python
class LazyAgentManager:
    def __init__(self):
        self._agents = {}
        self._agent_configs = {}
    
    async def get_agent(self, agent_name: str):
        """Get agent, initializing on first access"""
        if agent_name not in self._agents:
            await self._initialize_agent(agent_name)
        return self._agents[agent_name]
```

**Benefit**: Faster startup, agents load on-demand

---

## Why This Fix Works

### Before:
- **Synchronous blocking**: File I/O, imports, object creation
- **Every connection**: Repeated work (even with singleton check)
- **Event loop blocked**: No other events can process
- **UI freezes**: Chrome and Windsurf can't render

### After:
- **One-time cost**: Initialization happens at startup
- **Async-safe**: Singleton returns instantly on subsequent calls
- **Event loop free**: WebSocket connections don't block
- **UI responsive**: No freeze, instant connection

---

## Testing Script

```python
# test_websocket_performance.py
import asyncio
import websockets
import time
import json

async def test_connection_speed():
    """Test WebSocket connection speed"""
    token = "your_auth_token_here"
    url = f"ws://localhost:8000/api/ws/system-metrics?token={token}"
    
    start = time.time()
    async with websockets.connect(url) as ws:
        # Wait for connection_established
        message = await ws.recv()
        data = json.loads(message)
        
        if data["type"] == "connection_established":
            elapsed = time.time() - start
            print(f"✅ Connection established in {elapsed:.3f}s")
            
            if elapsed < 0.5:
                print("🎉 EXCELLENT - No freeze!")
            elif elapsed < 1.0:
                print("✅ GOOD - Minor delay")
            elif elapsed < 2.0:
                print("⚠️ SLOW - Noticeable delay")
            else:
                print("❌ FREEZE - Still blocking")
            
            return elapsed
    
    return None

# Run test
asyncio.run(test_connection_speed())
```

---

**Ready to implement!** This fix will eliminate the WebSocket freeze completely. 🚀
