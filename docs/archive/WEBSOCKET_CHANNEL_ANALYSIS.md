# WebSocket Channel Architecture Analysis

## Current State: Three Separate Channels

### 1. System Metrics Channel (`/ws/system-metrics`)
**File**: `backend/app/api/simplified_websocket_routes.py`

**Payload Structure**:
```json
{
  "type": "metrics_update",
  "timestamp": "2024-11-01T10:30:00Z",
  "data": {
    "cpu_usage": 45.2,
    "memory_usage": 62.1,
    "disk_usage": 38.5,
    "process_count": 142,
    "network_data": {...}
  },
  "agents": {
    "sir_hawkington": {
      "status": "active",
      "triage": {...},
      "disposition": "normal",
      "confidence": 0.85
    },
    "the_stick": {...},
    "meth_snail": {...},
    // ... other agents
  }
}
```

**Key Features**:
- Sends metrics every 5 seconds
- **ALREADY INCLUDES agent insights embedded in the payload** (line 688)
- Runs AI triage every 10 seconds (throttled)
- Fetches agent memory banks every 30 seconds
- Persists metrics to database
- Handles backpressure and circuit breaking

### 2. Agent Insights Channel (`/ws/agent-insights`)
**File**: `backend/app/api/agent_insights_websocket.py`

**Payload Structure**:
```json
{
  "type": "agent_insight",
  "from_agent": "sir_hawkington",
  "to_agent": "the_stick",
  "action": "route_normal_operations",
  "reasoning": "System stress 0.25 - routing to baseline learning",
  "context": {
    "severity": "normal",
    "stress_score": 0.25,
    "confidence": 0.85
  },
  "user_id": "user-123",
  "timestamp": "2024-11-01T10:30:00Z"
}
```

**Key Features**:
- Broadcast-only (no polling)
- Receives broadcasts from `emit_agent_insight()` function
- Tracks inter-agent communications
- Uses same WebSocketManager as system-metrics

### 3. Agent Events Channel (`/ws/agent-events`)
**File**: `backend/app/api/agent_events_websocket.py`

**Payload Structure**:
```json
{
  "type": "agent_event",
  "agent_name": "sir_hawkington",
  "event_type": "monocle_adjustment",
  "event_data": {
    "action": "polished_monocle",
    "reason": "preparing_for_inspection"
  },
  "severity": "info",
  "agent_state": "active",
  "user_id": "user-123",
  "timestamp": "2024-11-01T10:30:00Z"
}
```

**Key Features**:
- Broadcast-only (no polling)
- Receives broadcasts from `log_agent_event()` function
- Tracks personality events and agent activities
- Uses same WebSocketManager as system-metrics

## Critical Discovery

**The system-metrics channel ALREADY includes agent insights!**

Looking at line 688 in `simplified_websocket_routes.py`:
```python
out_msg = {
    "type": "metrics_update",
    "timestamp": _now_iso(),
    "data": metrics,
    "agents": agent_insights,  # ← Agent data is ALREADY embedded!
}
```

## Recommendation: Unified Single Channel

### Option A: Keep System-Metrics as Primary Channel ✅ RECOMMENDED

**Rationale**:
1. System-metrics already contains agent insights
2. It's the most robust channel (has persistence, backpressure, circuit breaking)
3. Reduces connection overhead (3 WebSockets → 1 WebSocket)
4. Simplifies frontend state management

**Proposed Unified Payload**:
```json
{
  "type": "system_update",
  "timestamp": "2024-11-01T10:30:00Z",
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 62.1,
    "disk_usage": 38.5,
    "process_count": 142,
    "network_data": {...}
  },
  "agents": {
    "sir_hawkington": {
      "status": "active",
      "triage": {...},
      "latest_memory": {...},
      "latest_event": {...},
      "latest_insight": {...}
    }
  },
  "recent_insights": [
    {
      "from_agent": "sir_hawkington",
      "to_agent": "the_stick",
      "action": "route_normal_operations",
      "timestamp": "..."
    }
  ],
  "recent_events": [
    {
      "agent_name": "sir_hawkington",
      "event_type": "monocle_adjustment",
      "timestamp": "..."
    }
  ]
}
```

**Implementation Changes Required**:

1. **Backend**: Modify `simplified_websocket_routes.py` to include:
   - Recent insights buffer (last 10 insights)
   - Recent events buffer (last 10 events)
   - Aggregate all agent data into single payload

2. **Frontend**: Update Redux slices to handle unified payload:
   - `metricsSlice` - extract metrics
   - `agentsSlice` - extract agent data
   - `insightsSlice` - extract insights
   - `eventsSlice` - extract events

3. **Remove**:
   - `/ws/agent-insights` endpoint
   - `/ws/agent-events` endpoint
   - `useAgentInsightsConnection` hook
   - `useAgentEventsConnection` hook

### Option B: Keep Separate Channels (Current State)

**Rationale**:
- Separation of concerns
- Different update frequencies
- Easier to debug individual streams

**Drawbacks**:
- 3x connection overhead
- More complex frontend state management
- Redundant data (agent insights sent twice)
- SystemReadyPage needs to check 3 connections

## Performance Impact

### Current (3 Channels):
- 3 WebSocket connections per user
- 3 authentication checks
- 3 heartbeat loops
- Redundant agent data transmission

### Proposed (1 Channel):
- 1 WebSocket connection per user
- 1 authentication check
- 1 heartbeat loop
- Single unified payload (slightly larger, but sent once)

## Frontend State Management

### Current Approach:
```typescript
// Three separate hooks
const metricsConnection = useWebSocketConnection();
const insightsConnection = useAgentInsightsConnection();
const eventsConnection = useAgentEventsConnection();

// Three separate Redux slices
dispatch(updateMetrics(metricsData));
dispatch(addInsight(insightData));
dispatch(addEvent(eventData));
```

### Proposed Unified Approach:
```typescript
// Single hook
const systemConnection = useSystemConnection();

// Single message handler that routes to appropriate slices
const handleSystemUpdate = (payload) => {
  dispatch(updateMetrics(payload.metrics));
  dispatch(updateAgents(payload.agents));
  dispatch(addInsights(payload.recent_insights));
  dispatch(addEvents(payload.recent_events));
};
```

## Recommendation

**Consolidate to a single `/ws/system-updates` channel** that includes:
- System metrics (current)
- Agent insights (current + broadcast insights)
- Agent events (broadcast events)
- Agent memory banks (current)

This will:
1. ✅ Reduce connection overhead by 66%
2. ✅ Simplify SystemReadyPage (1 connection check instead of 3)
3. ✅ Eliminate redundant agent data transmission
4. ✅ Maintain all current functionality
5. ✅ Improve frontend state management
6. ✅ Reduce backend resource usage

The frontend slices can still handle data separately - they just receive it from a single source instead of three.
