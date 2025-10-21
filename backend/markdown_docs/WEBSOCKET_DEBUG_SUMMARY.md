# 🔍 WEBSOCKET CONNECTION DEBUG SUMMARY

## Issues Fixed So Far

### 1. ✅ JSON Serialization (Backend)
- **Fixed:** `HawkingtonDecision` dataclass not JSON serializable
- **Location:** `agent_manager.py` - Added `_serialize_triage()` helper
- **Location:** `simplified_websocket_routes.py` - Convert dataclass + datetime to JSON

### 2. ✅ Double WebSocket Accept (Backend)
- **Fixed:** `websocket.accept()` called twice causing ASGI error
- **Location:** `simplified_websocket_routes.py` line 274
- **Solution:** Directly add to `ws_manager.active_connections` instead of calling `connect()`

### 3. ✅ Frontend URL Paths
- **Fixed:** Services using relative paths causing double `/api`
- **Location:** `agentInsightsWebSocket.ts` and `agentEventsWebSocket.ts`
- **Solution:** Changed `DEFAULT_PATH` to full URLs

---

## Current Status

### Metrics Endpoint: ✅ WORKING
- URL: `ws://localhost:8000/api/ws/metrics`
- Status: Connected and sending data

### Agent Insights Endpoint: ❓ DEBUGGING
- URL: `ws://localhost:8000/api/ws/agent-insights`
- Status: Disconnected
- **Added debug logging to track connection attempts**

### Agent Events Endpoint: ❓ DEBUGGING  
- URL: `ws://localhost:8000/api/ws/agent-events`
- Status: Disconnected
- **Added debug logging to track connection attempts**

---

## Debug Logs Added

### Frontend Hooks
Added console.log statements to track:
1. `useAgentInsightsConnection.ts`:
   - Line 88: Instance creation with base URL
   - Line 139-141: ensureConnected() call

2. `useAgentEventsConnection.ts`:
   - Line 113: Instance creation with base URL
   - Line 164-166: ensureConnected() call

### What to Check in Browser Console

**Expected logs when page loads:**
```
🔌 Agent Insights: Getting instance with base URL: ws://localhost:8000
🔌 Agent Insights: Calling ensureConnected()
🔌 Agent Insights: ensureConnected() completed
✅ Agent Insights WebSocket connected

🎭 Agent Events: Getting instance with base URL: ws://localhost:8000
🎭 Agent Events: Calling ensureConnected()
🎭 Agent Events: ensureConnected() completed
✅ Agent Events WebSocket connected
```

**If you see errors:**
- Circuit breaker messages: `⏳ circuit breaker active`
- Connection errors: Check token, backend status
- Timeout errors: Check if backend endpoints are registered

---

## Backend Endpoints Status

### Check if endpoints are registered:
```bash
# In backend terminal, look for these on startup:
✅ Agent Events WebSocket route registered
✅ Agent Insights WebSocket route registered
```

### Check if routes respond:
```bash
curl -s http://localhost:8000/openapi.json | grep -o '"\/api\/ws\/agent-[^"]*"'
```

Should show:
```
"/api/ws/agent-insights"
"/api/ws/agent-events"
```

---

## Agent Activity Issue

**Problem:** High CPU/RAM but agents not showing analysis

**Possible causes:**
1. Agent insights endpoint not connected (being debugged)
2. Triage engine not broadcasting to insights endpoint
3. Frontend not displaying received data

**Check:**
1. Browser console for agent_memory_update messages
2. Backend logs for triage processing
3. Redux store for agent data

---

## Next Steps

1. **Restart both servers** with all fixes applied
2. **Open browser console** and navigate to System Monitor
3. **Check debug logs** to see where connections fail
4. **Check backend logs** for authentication or routing errors
5. **Report back** with console output

---

## Files Modified (This Session)

### Backend:
1. `/backend/app/ai_agents/agent_manager.py` - JSON serialization
2. `/backend/app/api/simplified_websocket_routes.py` - Double accept + datetime serialization

### Frontend:
1. `/frontend/src/services/agentInsightsWebSocket.ts` - Full URL path
2. `/frontend/src/services/agentEventsWebSocket.ts` - Full URL path
3. `/frontend/src/hooks/useAgentInsightsConnection.ts` - Debug logging
4. `/frontend/src/hooks/useAgentEventsConnection.ts` - Debug logging

---

## 🚀 Ready to Test!

**Restart both servers and check browser console for debug output!**
