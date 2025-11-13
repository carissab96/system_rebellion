# 🔧 WEBSOCKET CONNECTION FIXES

## Issues Found

### 1. ❌ Agent Insights & Events Not Connecting
**Problem:** Services were using relative paths that resulted in double `/api` in the URL

**Root Cause:**
- `.env` has `VITE_WS_URL=ws://localhost:8000/api`
- Services had `DEFAULT_PATH = "/api/ws/agent-insights"`
- Result: `ws://localhost:8000/api/api/ws/agent-insights` ❌

### 2. ❌ Metrics Processing Error
**Problem:** `HawkingtonDecision` dataclass not JSON serializable (FIXED in previous commit)

---

## Fixes Applied

### Frontend WebSocket Services

**File: `/frontend/src/services/agentInsightsWebSocket.ts`**
```typescript
// Before
const DEFAULT_PATH = "/api/ws/agent-insights";  // ❌ Relative path

// After
const DEFAULT_PATH = "ws://localhost:8000/api/ws/agent-insights";  // ✅ Full URL
```

**File: `/frontend/src/services/agentEventsWebSocket.ts`**
```typescript
// Before
const DEFAULT_PATH = "/api/ws/agent-events";  // ❌ Relative path

// After
const DEFAULT_PATH = "ws://localhost:8000/api/ws/agent-events";  // ✅ Full URL
```

### Frontend Hooks

**File: `/frontend/src/hooks/useAgentInsightsConnection.ts`**
```typescript
// Before
wsServiceRef.current.ensureConnected('/api/ws/agent-insights');  // ❌

// After
wsServiceRef.current.ensureConnected();  // ✅ Uses DEFAULT_PATH
```

**File: `/frontend/src/hooks/useAgentEventsConnection.ts`**
```typescript
// Before
wsServiceRef.current.ensureConnected('/api/ws/agent-events');  // ❌

// After
wsServiceRef.current.ensureConnected();  // ✅ Uses DEFAULT_PATH
```

---

## Backend Status

### ✅ All Endpoints Registered
- `/api/ws/metrics` - System metrics (working)
- `/api/ws/agent-insights` - Live agent activities (now fixed)
- `/api/ws/agent-events` - Historical personality events (now fixed)

### ✅ Authentication Working
Both new endpoints have proper token authentication:
```python
token = websocket.query_params.get("token")
user = await get_current_user_from_token(token)
```

### ✅ JSON Serialization Fixed
`HawkingtonDecision` dataclass now properly serialized with `_serialize_triage()` helper

---

## Testing

### 1. Restart Backend
```bash
cd backend
uvicorn main:app --reload
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Check Browser Console
Should see:
```
✅ Connected to metrics endpoint
✅ Agent Insights WebSocket connected
✅ Agent Events WebSocket connected
```

### 4. Check SystemMonitorPage
Navigate to `/dashboard/system-monitor`

**Expected:**
- 🟢 Metrics: Connected
- 🟢 Agent Insights: Connected
- 🟢 Agent Events: Connected

---

## Files Modified

### Frontend:
1. `/frontend/src/services/agentInsightsWebSocket.ts` - Fixed DEFAULT_PATH
2. `/frontend/src/services/agentEventsWebSocket.ts` - Fixed DEFAULT_PATH
3. `/frontend/src/hooks/useAgentInsightsConnection.ts` - Use default path
4. `/frontend/src/hooks/useAgentEventsConnection.ts` - Use default path

### Backend:
1. `/backend/app/ai_agents/agent_manager.py` - Fixed JSON serialization

---

## Status: ✅ READY TO TEST

All three WebSocket endpoints should now connect successfully!
