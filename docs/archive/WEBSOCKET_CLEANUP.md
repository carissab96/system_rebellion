# WebSocket Unification Cleanup

## Summary
Removed redundant WebSocket hooks, services, and legacy components after system unification into a single WebSocket channel.

## What Was Removed

### 1. Redundant Hooks (2 files)
- ✅ `/frontend/src/hooks/useAgentInsightsConnection.ts`
- ✅ `/frontend/src/hooks/useAgentEventsConnection.ts`

**Why:** The unified `useWebSocketConnection` hook now handles insights and events through the `system_update` payload.

### 2. Redundant Services (2 files)
- ✅ `/frontend/src/services/agentInsightsWebSocket.ts`
- ✅ `/frontend/src/services/agentEventsWebSocket.ts`

**Why:** Only `websocket.ts` is needed for the unified channel.

### 3. Legacy Components (entire directory)
- ✅ `/frontend/src/components/agent-theater/legacy-files/`
  - `AgentTheater.tsx`
  - `AgentTheater.css.backup`
  - `AgentTheater.module.css.backup`
  - `AgentTheaterEnhanced.css`

**Why:** These were old implementations that were never imported or used. The current system uses `LiveAgentTheater.tsx`.

## Current Architecture

### Single Unified WebSocket
**Endpoint:** `/api/ws/system-metrics`

**Payload Structure:**
```typescript
{
  type: "system_update",
  timestamp: "2024-11-01T12:00:00Z",
  metrics: {
    cpu_usage: 45.2,
    memory_usage: 62.8,
    // ... other system metrics
  },
  agents: {
    sir_hawkington: {
      triage: { /* triage decision */ },
      memory_banks: { /* agent memories */ }
    },
    // ... other agents
  },
  recent_insights: [
    {
      type: "agent_insight",
      from_agent: "sir_hawkington",
      to_agent: "the_stick",
      message: "..."
    }
    // ... last 10 insights
  ],
  recent_events: [
    {
      type: "agent_event",
      agent_name: "hamsters",
      event_type: "personality_shift",
      data: { /* event data */ }
    }
    // ... last 10 events
  ]
}
```

### Single Hook
**Hook:** `useWebSocketConnection()`

**What It Does:**
1. Connects to `/api/ws/system-metrics`
2. Receives unified `system_update` payloads
3. Dispatches to Redux:
   - `updateMetrics()` for system metrics
   - `updateTriageData()` for triage decisions
   - `addAgentMemory()` for agent data
4. Provides access to `recent_insights` and `recent_events` (available but not yet consumed by UI)

## Benefits of Unification

### 1. **Reduced Complexity**
- **Before:** 3 separate WebSocket connections (metrics, insights, events)
- **After:** 1 unified connection
- **Result:** Fewer moving parts, easier to debug

### 2. **Better Performance**
- Single connection = less overhead
- Reduced network traffic
- Synchronized updates (all data arrives together)

### 3. **Easier Maintenance**
- Only one hook to maintain
- Only one service to debug
- Consistent error handling

### 4. **Prevented Loop Issues**
- Fewer connections = fewer potential loop sources
- Single intentionalCloseRef flag
- Unified reconnection logic

## Backend Support

The backend already supports this unified approach:

**File:** `/backend/app/api/simplified_websocket_routes.py`

```python
# Lines 682-695
recent_insights = ws_manager.get_recent_insights(limit=10)
recent_events = ws_manager.get_recent_events(limit=10)

out_msg = {
    "type": "system_update",
    "timestamp": _now_iso(),
    "metrics": metrics,
    "agents": agent_insights,
    "recent_insights": recent_insights,
    "recent_events": recent_events,
}
```

**File:** `/backend/main.py`

```python
# Lines 360-364
# Deprecated: Agent events and insights WebSocket routes
# These are now unified into the system-metrics endpoint (/api/ws/system-metrics)
# which sends a unified payload with metrics, agents, recent_insights, and recent_events
```

## Migration Notes

### For Future Development

If you need to consume insights or events in the UI:

1. **Access from Redux state** (if you add slices for insights/events)
2. **Or subscribe to the unified hook** and filter for specific message types
3. **Or use the buffered data** from `payload.recent_insights` and `payload.recent_events`

Example:
```typescript
const handleMessage = useCallback((payload: any) => {
  if (payload.type === 'system_update') {
    // Access insights
    if (payload.recent_insights) {
      payload.recent_insights.forEach(insight => {
        console.log(`${insight.from_agent} → ${insight.to_agent}: ${insight.message}`);
      });
    }
    
    // Access events
    if (payload.recent_events) {
      payload.recent_events.forEach(event => {
        console.log(`${event.agent_name}: ${event.event_type}`);
      });
    }
  }
}, []);
```

## Verification

To verify the cleanup was successful:

```bash
# Should return 0 results
grep -r "useAgentInsightsConnection" frontend/src/
grep -r "useAgentEventsConnection" frontend/src/
grep -r "agentInsightsWebSocket" frontend/src/
grep -r "agentEventsWebSocket" frontend/src/
grep -r "legacy-files/AgentTheater" frontend/src/

# Should only find the unified hook
grep -r "useWebSocketConnection" frontend/src/
```

## Impact

### Zero Breaking Changes
- No active code was using the removed hooks
- Legacy files were never imported
- All functionality preserved in unified hook

### Cleaner Codebase
- **Removed:** ~1500 lines of redundant code
- **Maintained:** All functionality
- **Improved:** Maintainability and debuggability
