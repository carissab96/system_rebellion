# Agent Monitor Debug Analysis

## What Agent Monitor Shows

The frontend AgentMonitorDashboard.tsx expects to see backend logs categorized by:
1. **Redis** - pub/sub, broadcast, message operations
2. **PostgreSQL** - database writes, commits, queries
3. **Vector** - embedding, semantic operations
4. **System** - everything else

## Backend Logging System

### WebSocketLogHandler (websocket_log_handler.py)
- Intercepts Python logging output from agent loggers
- Categorizes logs into redis/postgres/vector/system
- Broadcasts via WebSocket as `type: 'agent_log'`
- Attached to these logger names:
  - `TheStick.Distributed`
  - `VIC20Sage.Distributed`
  - `MethSnail.Distributed`
  - `SirHawkington.Distributed`
  - `Hamsters.Distributed`
  - `QuantumShadowPeople.Distributed`

### Agent Logger Names (ACTUAL)
- Terry: `logger = logging.getLogger("MethSnail.Distributed")` ✅
- Hamsters: `logger = logging.getLogger("Hamsters.Distributed")` ✅
- QSP: `logger = logging.getLogger("QuantumShadowPeople.Distributed")` ✅
- VIC-20: `logger = logging.getLogger("VIC20Sage.Distributed")` ✅
- Hawk: `logger = logging.getLogger("SirHawkington.Distributed")` ✅
- Stick: `logger = logging.getLogger("TheStick.Distributed")` ✅

**Logger names match! ✅**

### Setup (main.py line 260)
```python
setup_websocket_logging(ws_manager.broadcast_json, event_loop, level=logging.INFO)
```

This should be working!

## Possible Issues

1. **WebSocket not connected** - Frontend not receiving broadcasts
2. **Agents not logging** - No log output being generated
3. **Event loop issue** - Broadcast function not executing
4. **WebSocket endpoint mismatch** - Frontend listening to wrong endpoint

## Frontend WebSocket Connection

AgentMonitorDashboard.tsx line 222-226:
```typescript
const wsService = WebSocketService.getInstance(
  import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
);
wsService.subscribe(handleAgentMessage);
```

This uses the MAIN WebSocket endpoint, not a separate agent_logs endpoint.

## The Real Issue

The WebSocketLogHandler broadcasts messages with:
```python
message = {
    'type': 'agent_log',
    'agent_name': agent_name,
    'level': record.levelname.lower(),
    'category': category,
    'message': log_entry,
    ...
}
```

Frontend AgentMonitorDashboard.tsx line 126 checks for:
```typescript
if (msgType === 'agent_log') {
  // Handle it
}
```

**This should work!**

## What to Check on Dell

1. Is backend actually running and agents logging?
2. Is WebSocket connection established?
3. Are logs being broadcast (check backend console for "🔊 Broadcasting log")?
4. Is frontend receiving ANY WebSocket messages?
5. Check browser console for WebSocket connection status
