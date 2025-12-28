# WebSocket Emissions Map - Complete Backend to Frontend Communication

**Generated:** December 28, 2025  
**Purpose:** Comprehensive mapping of ALL backend-to-frontend WebSocket emissions

---

## Overview

The backend communicates with the frontend via WebSocket using two primary mechanisms:

1. **Direct WebSocket Broadcasts** - Python code directly calls `ws_manager.broadcast_json()`
2. **Redis Pub/Sub Bridge** - Messages published to Redis channels are forwarded to WebSocket clients

---

## Direct WebSocket Broadcasts

### 1. Agent Decision Pipeline (`agent_decision`)

**Source:** `/backend/app/services/agent_decision_emitter.py` → `emit_agent_decision()`

**Emitted By:** All 6 ML v2 agents after completing their decision pipeline

**Emission Points:**
- `/backend/app/ai_agents/meth_snail/distributed_meth_snail.py` (line ~340)
- `/backend/app/ai_agents/hamsters/distributed_hamsters.py` (line ~340)
- `/backend/app/ai_agents/quantum_shadow_people/distributed_qsp.py` (line ~273)
- `/backend/app/ai_agents/sir_hawkington/distributed_hawkington.py` (line ~441)
- `/backend/app/ai_agents/vic_20_sage/distributed_vic20.py` (line ~373)
- `/backend/app/ai_agents/the_stick/distributed_stick.py` (line ~280)

**Payload Structure:**
```json
{
  "type": "agent_decision",
  "agent_name": "meth_snail",
  "decision_id": "uuid",
  "timestamp": "ISO-8601",
  "user_id": "optional",
  "perception": {
    // Full context: metrics, data quality, personality state
    // Terry: shell_spin_incidents, energy_drink_system
    // Hamsters: beer_consumption, duct_tape_assessment, supply_closet
    // QSP: tequila_system, quantum_state
    // Stick: paper_bag_economy, anxiety_level
    // Hawk: monocle_yeets, data_quality_score
    // VIC-20: coordination stats, mediation stats
  },
  "reasoning": {
    // Root cause analysis, confidence, evidence
  },
  "action_selection": {
    // Chosen action, alternatives, exploration/exploitation
  },
  "execution": {
    // Metrics before/after, success, improvement
  },
  "learning": {
    // Fingerprint, stored, learning_record_id
  }
}
```

**Frequency:** Every time an agent completes a decision (varies by agent activity)

---

### 2. Agent Insights (`agent_insight`)

**Source:** `/backend/app/services/agent_insight_emitter.py`

**Functions:**
- `emit_agent_insight()` - Inter-agent communication
- `emit_coordination_insight()` - Multi-agent coordination
- `emit_resource_transfer_insight()` - Resource sharing between agents

**Emitted By:** Agents during coordination and communication

**Payload Structure:**
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
  "timestamp": "ISO-8601"
}
```

**Variants:**
- **Coordination:** `insight_category: "coordination"` - VIC-20 coordinating multiple agents
- **Resource Transfer:** `insight_category: "resource_transfer"` - Red Bull, duct tape, paper bags

**Frequency:** During agent-to-agent interactions (routing, escalation, delegation)

---

### 3. Personality Behaviors (`personality_behavior`)

**Source:** `/backend/app/services/agent_decision_emitter.py` → `emit_personality_behavior()`

**Emitted By:** Agents when personality behaviors are triggered

**Payload Structure:**
```json
{
  "type": "personality_behavior",
  "agent_name": "meth_snail",
  "behavior_type": "shell_spin",
  "behavior_data": {
    "reason": "Missing CPU metrics in coordination request",
    "shell_spin_count": 5,
    "data_quality_score": 0.75,
    "incident_id": "uuid"
  },
  "timestamp": "ISO-8601"
}
```

**Behavior Types:**
- **Terry:** `shell_spin`, `energy_drink_consumed`, `hawk_veto`
- **Hamsters:** `beer_consumed`, `duct_tape_calculation`, `supply_closet_raid`
- **QSP:** `tequila_shot`, `quantum_state_change`, `paranoia_spike`
- **Stick:** `paper_bag_consumed`, `anxiety_spike`, `bob_detected`
- **Hawk:** `monocle_yeet`, `data_quality_alert`
- **VIC-20:** `mediation_event`, `drama_escalation`

**Frequency:** When personality behaviors are triggered by real system conditions

---

### 4. Agent Events (`agent_event`)

**Source:** `/backend/app/services/agent_event_logger.py` → `emit_agent_event()`

**Emitted By:** Agent lifecycle and state changes

**Payload Structure:**
```json
{
  "type": "agent_event",
  "agent_name": "meth_snail",
  "event_type": "started",
  "event_data": {
    "timestamp": "ISO-8601",
    "additional_context": {}
  },
  "timestamp": "ISO-8601"
}
```

**Event Types:**
- `started`, `stopped`, `error`, `warning`
- `state_change`, `health_check`

**Frequency:** Agent lifecycle events

---

### 5. Agent Logs (`agent_log`)

**Source:** `/backend/app/core/websocket_log_handler.py` → `WebSocketLogHandler.emit()`

**Emitted By:** Python logging system (all agent loggers)

**Payload Structure:**
```json
{
  "type": "agent_log",
  "agent_name": "sir_hawkington",
  "level": "info",
  "category": "postgres",
  "message": "Wrote triage decision to database",
  "timestamp": "ISO-8601",
  "logger": "SirHawkington.Distributed",
  "module": "distributed_hawkington",
  "function": "handle_resource_alert",
  "line": 123
}
```

**Categories:**
- `postgres` - Database operations
- `redis` - Redis/pub-sub operations
- `vector` - Vector/embedding operations
- `system` - General system logs

**Frequency:** Continuous (every log statement from agents)

---

### 6. Agent Memory Updates (`agent_memory_update`)

**Source:** `/backend/app/services/agent_insight_emitter.py` → `emit_agent_memory_update()`

**Emitted By:** Agents when updating their memory bank

**Payload Structure:**
```json
{
  "type": "agent_memory_update",
  "agent_name": "sir_hawkington",
  "memory": {
    "memory_id": "abc123",
    "timestamp": "ISO-8601",
    "shared_with_central": true,
    "central_memory_id": "xyz789",
    // ... full memory data
  },
  "timestamp": "ISO-8601"
}
```

**Frequency:** When agents store memories

---

### 7. System Heartbeat (`heartbeat`)

**Source:** `/backend/app/api/websockets.py` → `WebSocketManager._heartbeat_loop()`

**Payload Structure:**
```json
{
  "type": "heartbeat",
  "active": 3
}
```

**Frequency:** Every 30 seconds

---

### 8. Agent Roster (`agent_roster`)

**Source:** `/backend/app/api/simplified_websocket_routes.py`

**Payload Structure:**
```json
{
  "type": "agent_roster",
  "active_agents": ["sir_hawkington", "vic20_sage", "meth_snail"],
  "count": 3,
  "timestamp": "ISO-8601"
}
```

**Frequency:** On connection and periodically

---

## Redis Pub/Sub → WebSocket Bridge

**Source:** `/backend/app/api/websockets.py` → `WebSocketManager._subscribe_to_agent_messages()`

The WebSocket manager subscribes to Redis channels and forwards messages to connected clients.

### Redis Channels Monitored

1. **`agents:broadcast`** → Forwarded as `agent_message`
2. **`agents:decisions`** → Forwarded as `triage_decision`
3. **`agents:resources:alerts`** → Forwarded as `resource_alert`
4. **`agents:emergency`** → Forwarded as `emergency`
5. **`agents:heartbeats`** → Forwarded as `agent_heartbeat`
6. **`agents:learning`** → Forwarded as `learning_update`
7. **`coordination:requests`** → Forwarded as `coordination_request`
8. **`agent:actions`** → Forwarded as `agent_action`

### Legacy Channels (Backward Compatibility)

- `agent:broadcast` → `agent_message`
- `triage:decisions` → `triage_decision`
- `resource:alerts` → `resource_alert`

### Redis Message Flow

```
Agent publishes to Redis channel
         ↓
WebSocketManager subscribes to channel
         ↓
Message received and parsed
         ↓
Wrapped in WebSocket message format
         ↓
Broadcast to all connected WebSocket clients
```

---

## Complete Message Type Reference

| Message Type | Source | Frequency | Purpose |
|--------------|--------|-----------|---------|
| `agent_decision` | agent_decision_emitter.py | Per decision | Full ML pipeline transparency |
| `agent_insight` | agent_insight_emitter.py | Per interaction | Inter-agent communication |
| `personality_behavior` | agent_decision_emitter.py | Per behavior | Personality reactions |
| `agent_event` | agent_event_logger.py | Lifecycle events | Agent state changes |
| `agent_log` | websocket_log_handler.py | Continuous | Backend logging |
| `agent_memory_update` | agent_insight_emitter.py | Per memory write | Memory bank updates |
| `heartbeat` | websockets.py | Every 30s | WebSocket keepalive |
| `agent_roster` | simplified_websocket_routes.py | On connect + periodic | Active agents |
| `triage_decision` | Redis → websockets.py | Per triage | Hawk triage decisions |
| `resource_alert` | Redis → websockets.py | Per alert | Resource threshold violations |
| `emergency` | Redis → websockets.py | Emergency only | Critical system events |
| `agent_heartbeat` | Redis → websockets.py | Per agent heartbeat | Agent liveness |
| `learning_update` | Redis → websockets.py | Per learning event | Shared learning |
| `coordination_request` | Redis → websockets.py | Per coordination | VIC-20 routing |
| `agent_action` | Redis → websockets.py | Per action | Agent actions/overrides |
| `agent_message` | Redis → websockets.py | General broadcasts | Agent-to-agent messages |

---

## Frontend Integration

**WebSocket Connection:** `ws://localhost:8000/api/ws/system-metrics`

**Frontend Handler:** `/frontend/src/hooks/useWebSocketConnection.ts`

**Redux Slices:**
- `agentsSlice.ts` - Handles `agent_decision` messages
- `communicationSlice.ts` - Handles insights, events, coordination

**Components:**
- `DecisionChainView.tsx` - Displays ML decision pipeline
- `PersonalityBehaviors.tsx` - Displays personality behaviors
- `AgentMonitorDashboard.tsx` - Displays agent logs
- `DistributedAgentDashboard.tsx` - Agent Theater

---

## Testing

Use the audit script to capture all emissions:

```bash
cd /home/carissa/Documents/system_rebellion/backend/scripts
./websocket_emission_audit.py 300  # Monitor for 5 minutes
```

Output saved to: `/backend/logs/websocket_audit_YYYYMMDD_HHMMSS.log`

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND SOURCES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Agent Decision Pipeline                                        │
│  ├─ distributed_meth_snail.py ──┐                              │
│  ├─ distributed_hamsters.py ────┤                              │
│  ├─ distributed_qsp.py ─────────┤                              │
│  ├─ distributed_hawkington.py ──┼─→ agent_decision_emitter.py  │
│  ├─ distributed_vic20.py ───────┤                              │
│  └─ distributed_stick.py ────────┘                              │
│                                                                 │
│  Agent Communication                                            │
│  └─ All agents ──────────────────→ agent_insight_emitter.py    │
│                                                                 │
│  Agent Logging                                                  │
│  └─ Python logging ──────────────→ websocket_log_handler.py    │
│                                                                 │
│  Redis Pub/Sub                                                  │
│  └─ All agents ──────────────────→ Redis channels              │
│                                     │                           │
└─────────────────────────────────────┼───────────────────────────┘
                                      │
                                      ↓
                        ┌─────────────────────────┐
                        │   WebSocketManager      │
                        │   (websockets.py)       │
                        ├─────────────────────────┤
                        │ • Direct broadcasts     │
                        │ • Redis subscription    │
                        │ • Message buffering     │
                        │ • Heartbeat loop        │
                        └─────────────────────────┘
                                      │
                                      ↓
                        ┌─────────────────────────┐
                        │   WebSocket Clients     │
                        │   (Frontend)            │
                        ├─────────────────────────┤
                        │ • Redux state           │
                        │ • React components      │
                        │ • Real-time updates     │
                        └─────────────────────────┘
```

---

## Key Principles

1. **NO FAKE DATA** - All emissions contain real data from actual agent operations
2. **Backend is Source of Truth** - Frontend adapts to backend message formats
3. **Personality Behaviors are Functional** - Triggered by real system conditions
4. **ML Transparency** - Full decision pipeline visible to frontend
5. **Real-time Coordination** - Live agent-to-agent communication visible

---

## Notes

- All timestamps are ISO-8601 format in UTC
- Message payloads vary by agent and context
- Some fields are optional and only included when available
- Redis channels are monitored continuously while WebSocket is connected
- Frontend should handle missing/optional fields gracefully
