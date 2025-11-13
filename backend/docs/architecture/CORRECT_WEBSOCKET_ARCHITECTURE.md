# ✅ CORRECT WEBSOCKET ARCHITECTURE

## The Three Endpoints

### 1. `/api/ws/metrics` ✅ EXISTING
**Purpose:** System metrics  
**Pattern:** SimplifiedMetricsService  
**Status:** Working, no changes needed

---

### 2. `/api/ws/agent-insights` 🔨 TO BUILD
**Purpose:** Live agent activities/decisions  
**Pattern:** Uses **master_websocket_router_v2**  
**Integration:** Called from agent_manager

**Key Points:**
- Should NOT create its own manager
- Should leverage existing `SystemRebellionWebSocketRouter`
- Broadcasts through `broadcast_agent_notification()`
- Follows triage architecture pattern

**Implementation:**
```python
# In agent_manager.py, after agent processing:
from app.ai_agents.master_websocket_router_v2 import notify_agents_via_websocket

# Broadcast agent activity
await notify_agents_via_websocket({
    'type': 'agent_activity',
    'agent_name': 'sir_hawkington',
    'activity_type': 'triage_decision',
    'data': decision_data
})
```

---

### 3. `/api/ws/agent-events` 🔨 TO BUILD
**Purpose:** Historical personality events  
**Pattern:** Database polling (like metrics endpoint)  
**Source:** AgentEventLog table

**Key Points:**
- Independent endpoint
- Polls database every 2 seconds
- Uses circuit breaker + backpressure
- Follows simplified_websocket_routes pattern

---

## Next Steps

1. ✅ Keep `/api/ws/metrics` as-is
2. 🔨 Build `/api/ws/agent-insights` using master router
3. 🔨 Build `/api/ws/agent-events` using database polling pattern
4. 🔨 Add broadcast calls in agent_manager

The key was understanding that agent-insights should use the EXISTING router infrastructure, not create a new one!
