# 🎯 FRONTEND INTEGRATION - ACTION PLAN

## Current State

### ✅ Backend Complete
- 3 WebSocket endpoints running
- All authentication working
- Event logging system active
- Agent processing ready

### ✅ Frontend Infrastructure Built
- `multiWebSocket.ts` - Multi-endpoint manager
- `websocketMessages.ts` - TypeScript types
- `useMultiWebSocket.ts` - React hook
- Redux slices ready to receive data

### ⏳ Frontend Components Need Updates
7 files currently use the old `useWebSocketConnection` hook:
1. `AdminConsole.tsx`
2. `AgentTheater.tsx`
3. `AgentTheaterNew.tsx`
4. `AgentTestingPage.tsx`
5. `MemoryBanksPage.tsx`
6. `SystemMonitorPage.tsx`
7. `useWebSocketConnection.ts` (the old hook itself)

---

## 🚀 Implementation Steps

### Step 1: Replace WebSocket Hook in Each Component

For each file, replace:
```typescript
// OLD
import { useWebSocketConnection } from '../hooks/useWebSocketConnection';
const { isConnected, reconnect } = useWebSocketConnection();

// NEW
import { useMultiWebSocket } from '../hooks/useMultiWebSocket';
const { connectionStatus, isAllConnected, reconnectAll } = useMultiWebSocket();
```

**Files to update:**
1. ✅ `SystemMonitorPage.tsx` - PRIORITY (main metrics display)
2. ✅ `AgentTheater.tsx` - PRIORITY (personality events)
3. ✅ `MemoryBanksPage.tsx` - PRIORITY (all agent data)
4. ⏳ `AgentTestingPage.tsx`
5. ⏳ `AdminConsole.tsx`
6. ⏳ `AgentTheaterNew.tsx`

### Step 2: Update Components to Display New Data

#### SystemMonitorPage.tsx
**Changes needed:**
- Show connection status for all 3 endpoints
- Display metrics (already working via Redux)
- Add connection indicator badges

```typescript
<div className="connection-status">
  <Badge color={connectionStatus.metrics ? 'green' : 'red'}>
    Metrics: {connectionStatus.metrics ? 'Connected' : 'Disconnected'}
  </Badge>
  <Badge color={connectionStatus.agentInsights ? 'green' : 'red'}>
    Insights: {connectionStatus.agentInsights ? 'Connected' : 'Disconnected'}
  </Badge>
  <Badge color={connectionStatus.agentEvents ? 'green' : 'red'}>
    Events: {connectionStatus.agentEvents ? 'Connected' : 'Disconnected'}
  </Badge>
</div>
```

#### AgentTheater.tsx
**Changes needed:**
- Filter agent memories for personality events
- Display event cards with animations
- Show event type icons (monocle, paper bag, shell, etc.)

```typescript
// Get personality events from Redux
const personalityEvents = useSelector((state: RootState) => {
  const allAgents = Object.values(state.agents);
  return allAgents.flatMap(agent => 
    agent.recent_memories.filter((m: any) => m.is_personality_event)
  );
});

// Display events
{personalityEvents.map(event => (
  <EventCard key={event.memory_id} event={event} />
))}
```

#### MemoryBanksPage.tsx
**Changes needed:**
- Separate tabs for Activities vs Events
- Display both live activities and personality events
- Show memory type badges

```typescript
<Tabs>
  <Tab label="Live Activities">
    {memories.filter(m => m.is_live_activity).map(...)}
  </Tab>
  <Tab label="Personality Events">
    {memories.filter(m => m.is_personality_event).map(...)}
  </Tab>
  <Tab label="All Memories">
    {memories.map(...)}
  </Tab>
</Tabs>
```

### Step 3: Create Event Display Components

Create individual components for each event type:

**`src/components/agent-events/MonocleYeetCard.tsx`**
```typescript
export const MonocleYeetCard = ({ event }) => (
  <div className="event-card monocle-yeet">
    <div className="event-icon">🧐💥</div>
    <div className="event-content">
      <h4>Monocle Yeet!</h4>
      <p>Intensity: {event.yeet_intensity}</p>
      <p>Missing: {event.missing_metrics.join(', ')}</p>
      <p className="reason">{event.reason}</p>
    </div>
  </div>
);
```

**Similar components for:**
- `PaperBagCard.tsx` 📄
- `ShellSpinCard.tsx` 🐌
- `SupplyRaidCard.tsx` 🐹
- `DimensionalShiftCard.tsx` 👻
- `VIC20CoordinationCard.tsx` 🖥️

### Step 4: Add Event Animations

Use CSS animations or Framer Motion:

```typescript
import { motion, AnimatePresence } from 'framer-motion';

<AnimatePresence>
  {events.map(event => (
    <motion.div
      key={event.id}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
    >
      <EventCard event={event} />
    </motion.div>
  ))}
</AnimatePresence>
```

### Step 5: Test Each Page

**Test Checklist:**
- [ ] SystemMonitorPage shows all 3 connection statuses
- [ ] SystemMonitorPage displays metrics updating every 5s
- [ ] AgentTheater shows personality events in real-time
- [ ] AgentTheater animates new events as they arrive
- [ ] MemoryBanksPage shows both activities and events
- [ ] MemoryBanksPage can filter by type
- [ ] AgentTestingPage can trigger events
- [ ] All pages handle disconnections gracefully
- [ ] Reconnect buttons work on all pages

---

## 🎨 UI/UX Enhancements

### Connection Status Indicator
Add a global connection indicator in the header/nav:

```typescript
<div className="ws-status">
  {isAllConnected ? (
    <span className="status-connected">🟢 All Systems Connected</span>
  ) : (
    <span className="status-connecting">🟡 Connecting...</span>
  )}
</div>
```

### Event Notifications
Show toast notifications for important events:

```typescript
useEffect(() => {
  if (newEvent && newEvent.severity === 'high') {
    toast.info(`${newEvent.agent_name}: ${newEvent.event_type}`);
  }
}, [newEvent]);
```

### Event Sound Effects (Optional)
Play sounds for personality events:
- Monocle yeet: Glass breaking sound
- Paper bag: Crinkle sound
- Shell spin: Spinning sound
- Supply raid: Door opening sound

---

## 🐛 Debugging Strategy

### Check WebSocket Connections
```typescript
// In browser console
const manager = MultiWebSocketManager.getInstance();
console.log(manager.getConnectionStatus());
// Should show: { metrics: true, agentInsights: true, agentEvents: true }
```

### Check Redux State
```typescript
// In Redux DevTools
// Look for actions:
- metrics_update (every 5s)
- agent_memory_update (from insights)
- agent_memory_update (from events)

// Check state.agents
// Should see recent_memories with:
- is_live_activity: true (from insights)
- is_personality_event: true (from events)
```

### Check Backend Logs
```bash
# Backend should show:
✅ Agent insights WebSocket connected for user <id>
✅ Agent events WebSocket connected for user <id>
📤 Broadcast sir_hawkington activity: triage_decision
🎭 Agent events WebSocket connected for user <id>
```

---

## 📊 Success Criteria

✅ All 3 WebSocket endpoints connected  
✅ Metrics updating in real-time  
✅ Agent activities appearing in Memory Banks  
✅ Personality events appearing in Agent Theater  
✅ No console errors  
✅ Smooth animations  
✅ Reconnection working  
✅ All pages functional  

---

## 🚀 LET'S START!

**First task:** Update `SystemMonitorPage.tsx` to use the new hook and display connection status.

Ready to begin implementation?
