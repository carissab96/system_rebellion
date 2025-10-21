📋 AGENT INSIGHTS WEBSOCKET ENDPOINT - IMPLEMENTATION PLAN
Executive Summary
Create a dedicated WebSocket endpoint (/api/ws/agent-insights) to broadcast real-time agent activity (monocle yeets, paper bag consumption, beer raids, triage decisions, etc.) from backend to frontend using existing field mappings and architecture.

Current State Analysis
✅ What Already Exists
Backend field mappings for all 6 agents with structured data formats
Agent triage engine in 
agent_manager.py
 that processes metrics
Frontend Redux store with agentsSlice ready to receive agent memories
Frontend types in 
agents.ts
 matching backend field mappings
WebSocket authentication system in websocket_auth.py
Existing agent data flow through main metrics WebSocket (throttled to 10s intervals)
❌ What's Missing
Dedicated agent insights WebSocket endpoint for real-time agent activity
Broadcast mechanism from agent_manager to WebSocket clients
Frontend service to connect and handle agent insights messages
Real-time agent activity capture (currently only sent with metrics updates)
📐 IMPLEMENTATION PLAN - BACKEND TO FRONTEND
PHASE 1: Backend WebSocket Endpoint (1-2 hours)
Step 1.1: Create Agent Insights WebSocket Manager
File: 
/backend/app/api/agent_insights_websocket.py

Purpose: Manage WebSocket connections and broadcast agent activity

Implementation:

python
# Core functionality needed:
1. Connection manager (similar to WebSocketManager in websockets.py)
2. User-specific connection tracking (Dict[user_id, WebSocket])
3. Broadcast methods for each agent type:
   - broadcast_hawkington_decision(decision: HawkingtonDecision, user_id)
   - broadcast_stick_anxiety(anxiety_event: dict, user_id)
   - broadcast_snail_optimization(optimization: dict, user_id)
   - broadcast_hamster_raid(raid_event: dict, user_id)
4. Generic broadcast_agent_activity(agent_name, activity_data, user_id)
5. Connection/disconnection handlers with async locks
6. Heartbeat/ping-pong for connection health
Key Design Decisions:

Use asyncio.Lock() for thread-safe connection management
Store connections by user_id (one connection per user)
Include reconnection support with exponential backoff
Add throttling (max 1 message per agent per second) to prevent spam
Step 1.2: Register WebSocket Endpoint
File: 
/backend/main.py

Changes:

python
from app.api.agent_insights_websocket import agent_insights_websocket

# In lifespan startup:
app.websocket("/api/ws/agent-insights")(agent_insights_websocket)
logger.info("🤖 Agent insights WebSocket endpoint registered")
Step 1.3: Add Broadcast Calls in Agent Manager
File: 
/backend/app/ai_agents/agent_manager.py

Integration Points:

After Hawkington triage decision (line ~371):
python
# After: triage = await self.agents["sir_hawkington"].process_metrics(...)
await self._broadcast_agent_activity(
    "sir_hawkington",
    {
        "type": "triage_decision",
        "decision": asdict(triage),  # Convert dataclass to dict
        "severity": triage_severity,
        "confidence": triage.confidence
    },
    user_id
)
After monocle yeet (when data quality fails):
python
await self._broadcast_agent_activity(
    "sir_hawkington",
    {
        "type": "monocle_yeet",
        "missing_metrics": [...],
        "yeet_intensity": "utterly_appalled"
    },
    user_id
)
After Stick anxiety trigger:
python
await self._broadcast_agent_activity(
    "the_stick",
    {
        "type": "paper_bag_consumed",
        "anxiety_level": anxiety_data.anxiety_impact,
        "paper_bags_triggered": count
    },
    user_id
)
After Hamster infrastructure intervention:
python
await self._broadcast_agent_activity(
    "hamsters",
    {
        "type": "supply_cupboard_raid",
        "beer_consumed": intervention.beer_consumed,
        "contributing_hamster": "bob",  # or steve/carl
        "duct_tape_used": len(intervention.duct_tape_used)
    },
    user_id
)
After Meth Snail optimization:
python
await self._broadcast_agent_activity(
    "meth_snail",
    {
        "type": "energy_drink_consumed",
        "caffeine_level_mg": decision.caffeine_level_mg,
        "jitter_level": decision.current_jitter_level,
        "shell_spins": decision.shell_spin_count
    },
    user_id
)
Helper Method to Add:

python
async def _broadcast_agent_activity(self, agent_name: str, activity_data: dict, user_id: str):
    """Broadcast agent activity to connected WebSocket clients"""
    try:
        from app.api.agent_insights_websocket import get_agent_insights_manager
        insights_manager = get_agent_insights_manager()
        await insights_manager.broadcast_agent_activity(agent_name, activity_data, user_id)
    except Exception as e:
        logger.error(f"Failed to broadcast {agent_name} activity: {e}")
        # Non-fatal - don't break agent processing
PHASE 2: Backend Message Format Standardization (30 minutes)
Step 2.1: Define Message Schema
File: 
/backend/app/api/agent_insights_websocket.py

Standard Message Format:

python
{
    "type": "agent_activity",
    "agent_name": "sir_hawkington" | "the_stick" | "meth_snail" | "hamsters" | "quantum_shadow_people" | "vic20_sage",
    "activity_type": "triage_decision" | "monocle_yeet" | "paper_bag_consumed" | "supply_cupboard_raid" | "energy_drink_consumed" | "optimization_applied",
    "timestamp": "2025-01-14T16:00:00.000Z",
    "user_id": "uuid",
    "data": {
        # Agent-specific activity data matching field mappings
    }
}
Step 2.2: Map Backend Field Names to Frontend
Use existing field mappings - NO NEW MAPPINGS NEEDED

Example for Hawkington:

python
# Backend sends (from hawk_field_mapping.md):
{
    "decision_type": "alert",
    "confidence": 0.92,
    "reasoning": "System stress 0.87...",
    "system_impact": "significant_concern"
}

# Frontend receives (agents.ts already has types):
SirHawkingtonMemory.triage_decision_context
PHASE 3: Frontend WebSocket Service (1 hour)
Step 3.1: Create Agent Insights WebSocket Service
File: 
/frontend/src/services/agentInsightsWebSocket.ts

Implementation:

typescript
class AgentInsightsWebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;

  connect(token: string) {
    const wsUrl = `ws://localhost:8000/api/ws/agent-insights?token=${token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('✅ Agent insights WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onerror = (error) => {
      console.error('🤖 Agent insights WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('🔌 Agent insights WebSocket closed');
      this.attemptReconnect(token);
    };
  }

  private handleMessage(data: any) {
    const { type, agent_name, activity_type, data: activityData } = data;

    if (type === 'agent_activity') {
      // Dispatch to Redux store
      store.dispatch(addAgentActivity({
        agent_name,
        activity_type,
        data: activityData,
        timestamp: data.timestamp
      }));

      // Log for debugging
      console.log(`🤖 ${agent_name} activity: ${activity_type}`, activityData);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private attemptReconnect(token: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(token), this.reconnectDelay);
    }
  }
}

export const agentInsightsWebSocket = new AgentInsightsWebSocketService();
Step 3.2: Connect Service in useWebSocketConnection Hook
File: 
/frontend/src/hooks/useWebSocketConnection.ts

Add after main WebSocket connection:

typescript
// Connect to agent insights WebSocket
if (auth.token) {
  import('../services/agentInsightsWebSocket').then(({ agentInsightsWebSocket }) => {
    agentInsightsWebSocket.connect(auth.token!);
  });
}
PHASE 4: Frontend Redux Integration (30 minutes)
Step 4.1: Add Agent Activity Action to Redux
File: /frontend/src/store/slices/agentsSlice.ts

Add new action:

typescript
addAgentActivity: (state, action: PayloadAction<{
  agent_name: string;
  activity_type: string;
  data: any;
  timestamp: string;
}>) => {
  const { agent_name, activity_type, data, timestamp } = action.payload;
  
  // Add to agent's recent activity
  if (!state.recentActivity[agent_name]) {
    state.recentActivity[agent_name] = [];
  }
  
  state.recentActivity[agent_name].unshift({
    activity_type,
    data,
    timestamp
  });
  
  // Keep only last 50 activities per agent
  if (state.recentActivity[agent_name].length > 50) {
    state.recentActivity[agent_name] = state.recentActivity[agent_name].slice(0, 50);
  }
  
  // Update agent status
  state.agents[agent_name].lastActivity = timestamp;
  state.agents[agent_name].status = 'active';
}
PHASE 5: Testing & Validation (1 hour)
Step 5.1: Backend Testing
File: /backend/app/tests/test_agent_insights_websocket.py

Test Cases:

WebSocket connection with valid token
WebSocket connection with invalid token (should reject)
Broadcast to specific user
Broadcast to multiple users
Connection cleanup on disconnect
Message throttling (max 1/second per agent)
Step 5.2: Frontend Testing
File: /frontend/src/services/__tests__/agentInsightsWebSocket.test.ts

Test Cases:

Connection establishment
Message parsing
Redux dispatch on message
Reconnection logic
Disconnect cleanup
Step 5.3: Integration Testing
Manual Test Plan:

Start backend, start frontend
Login and navigate to Agent Theater
Trigger metrics collection (should see Hawkington triage)
Check browser console for 🤖 sir_hawkington activity: triage_decision
Check Redux DevTools for agents/addAgentActivity actions
Verify Agent Theater updates in real-time
📊 EFFORT ESTIMATION
Phase	Task	Time	Risk
1	Backend WebSocket Endpoint	1-2h	Low
2	Message Format Standardization	30m	Low
3	Frontend WebSocket Service	1h	Low
4	Frontend Redux Integration	30m	Low
5	Testing & Validation	1h	Medium
TOTAL	4-5 hours	LOW RISK	
🎯 SUCCESS CRITERIA
✅ Dedicated WebSocket endpoint at /api/ws/agent-insights
✅ Real-time agent activity broadcasts (< 100ms latency)
✅ Frontend receives and displays agent activities in Agent Theater
✅ All 6 agents broadcasting their signature activities:
Hawkington: Triage decisions, monocle yeets
Stick: Paper bag consumption, anxiety spikes
Meth Snail: Energy drink consumption, shell spins
Hamsters: Beer raids, duct tape usage
QSP: Phase shifts, dimensional observations
VIC-20: Emergency plans, coordination
✅ No performance degradation (throttled broadcasts)
✅ Graceful reconnection on disconnect
✅ User-specific broadcasts (no cross-user leakage)
🚨 CRITICAL CONSIDERATIONS
Use Existing Field Mappings - Don't create new data structures
Non-Blocking Broadcasts - Agent processing must not wait for WebSocket
User Privacy - Only broadcast to the specific user's connection
Throttling - Prevent WebSocket spam (max 1 msg/agent/second)
Error Handling - WebSocket failures must not crash agent processing
Memory Management - Limit stored activities (50 per agent max)