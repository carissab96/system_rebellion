# WebSocket Infinite Loop Fix

## Problem
WebSocket connections were stuck in an infinite reconnection loop, causing system freezes.

## Root Causes Identified

### 1. **Dependency Loop in `connect()` function**
- The `connect` callback included `localState.isConnecting` in its dependencies
- This caused the function to be recreated whenever `isConnecting` changed
- State changes triggered new connection attempts, creating an infinite loop

### 2. **Missing `intentionalCloseRef` flag**
- No way to distinguish between intentional closes (component unmount, logout) and unexpected disconnects
- Every close event triggered a reconnect, even during cleanup

### 3. **Aggressive reconnection on close**
- `onClose` handler always scheduled a reconnect after 3 seconds
- No check for whether the close was intentional
- Multiple components could trigger simultaneous reconnects

### 4. **Duplicate connection management**
- Multiple `useEffect` hooks trying to manage the same connection
- Race conditions between mount/unmount and auth state changes

## Changes Made

### All Three WebSocket Hooks Fixed
- `useWebSocketConnection.ts`
- `useAgentInsightsConnection.ts`
- `useAgentEventsConnection.ts`

### Specific Fixes

#### 1. Added `intentionalCloseRef`
```typescript
const intentionalCloseRef = useRef(false);
```
- Tracks whether a close is intentional (unmount, logout, manual disconnect)
- Prevents reconnection attempts during cleanup

#### 2. Removed `localState.isConnecting` from dependencies
```typescript
// Before
}, [auth.isAuthenticated, auth.isInitializing, auth.token, handleMessage, isDisabled, dispatch, localState.isConnecting]);

// After
}, [auth.isAuthenticated, auth.isInitializing, auth.token, handleMessage, isDisabled, dispatch]);
```

#### 3. Updated `onClose` handler
```typescript
wsServiceRef.current.onClose = () => {
  console.log('🔌 WebSocket closed');
  setLocalState(prev => ({ ...prev, isConnecting: false }));
  
  // Only attempt reconnection if it wasn't an intentional close
  if (isMountedRef.current && !intentionalCloseRef.current) {
    console.log('🔄 Unexpected close - attempting reconnection in 5s');
    connectTimeoutRef.current = setTimeout(() => {
      if (isMountedRef.current && !intentionalCloseRef.current) {
        console.log('🔄 Attempting to reconnect WebSocket...');
        connect();
      }
    }, 5000);
  } else if (intentionalCloseRef.current) {
    console.log('🔌 Intentional close - not reconnecting');
    intentionalCloseRef.current = false;
  }
};
```

#### 4. Improved cleanup in useEffect
```typescript
return () => {
  isMountedRef.current = false;
  intentionalCloseRef.current = true; // Mark as intentional close
  
  if (connectTimeoutRef.current) {
    clearTimeout(connectTimeoutRef.current);
    connectTimeoutRef.current = null;
  }
  
  if (wsServiceRef.current) {
    wsServiceRef.current.unsubscribe(handleMessage);
    wsServiceRef.current.close(1000, "component_unmount");
  }
};
```

#### 5. Fixed manual reconnect
```typescript
const reconnect = useCallback(() => {
  console.log('Manual reconnect requested');
  intentionalCloseRef.current = true; // Mark current close as intentional
  if (wsServiceRef.current) {
    wsServiceRef.current.resetCircuitBreaker();
    wsServiceRef.current.close();
  }
  // ... reset state ...
  connectTimeoutRef.current = setTimeout(() => {
    if (isMountedRef.current) {
      intentionalCloseRef.current = false; // Allow reconnect
      connect();
    }
  }, 100);
}, [connect]);
```

## Testing Recommendations

1. **Normal Operation**
   - Verify connections establish successfully
   - Check that data flows correctly
   - Monitor console for connection logs

2. **Reconnection Scenarios**
   - Backend restart (should reconnect after 5s)
   - Network interruption (should reconnect)
   - Manual reconnect button (should work cleanly)

3. **Cleanup Scenarios**
   - Component unmount (should NOT reconnect)
   - User logout (should NOT reconnect)
   - Page navigation (should NOT reconnect)

4. **Circuit Breaker**
   - Verify max retries (5) are respected
   - Check that circuit breaker prevents infinite loops
   - Confirm exponential backoff works

## Monitoring

Watch for these log patterns:

### Good (Expected)
```
🔌 WebSocket connected
🔌 WebSocket closed
🔌 Intentional close - not reconnecting
```

### Bad (Indicates Loop)
```
🔄 Attempting to reconnect WebSocket...
🔄 Attempting to reconnect WebSocket...
🔄 Attempting to reconnect WebSocket...
(repeating rapidly)
```

## Additional Safety Measures Already in Place

1. **MAX_RETRIES = 5**: Prevents infinite retry attempts
2. **Circuit Breaker**: Opens after 5 failures, waits 60s before retry
3. **Backpressure Handler**: Prevents message flooding
4. **Singleton Pattern**: Prevents multiple instances

## Files Modified
- `/frontend/src/hooks/useWebSocketConnection.ts`
- `/frontend/src/hooks/useAgentInsightsConnection.ts` (REMOVED - redundant)
- `/frontend/src/hooks/useAgentEventsConnection.ts` (REMOVED - redundant)

## Files Removed (Redundant After Unification)

Since the system now uses a **unified WebSocket channel** that sends metrics, agent data, insights, and events in a single `system_update` payload, the following redundant files were removed:

### Hooks
- `/frontend/src/hooks/useAgentInsightsConnection.ts`
- `/frontend/src/hooks/useAgentEventsConnection.ts`

### Services
- `/frontend/src/services/agentInsightsWebSocket.ts`
- `/frontend/src/services/agentEventsWebSocket.ts`

### Legacy Components
- `/frontend/src/components/agent-theater/legacy-files/` (entire directory)
  - `AgentTheater.tsx`
  - `AgentTheater.css.backup`
  - `AgentTheater.module.css.backup`
  - `AgentTheaterEnhanced.css`

### Why These Were Redundant

The backend now sends everything through `/api/ws/system-metrics`:
```typescript
{
  type: "system_update",
  timestamp: "...",
  metrics: { /* system metrics */ },
  agents: { /* agent memory banks and triage */ },
  recent_insights: [ /* last 10 inter-agent communications */ ],
  recent_events: [ /* last 10 personality events */ ]
}
```

The unified `useWebSocketConnection` hook handles all of this, making separate hooks for insights and events unnecessary.
