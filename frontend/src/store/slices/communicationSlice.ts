// store/slices/communicationSlice.ts
// Tracks inter-agent communications for topology visualization
// Data source: WebSocket system_update.recent_insights + real-time Redis messages

import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../store';

// Communication between agents
export interface AgentCommunication {
  action: string;
  context: any;
  id: string;
  timestamp: string;
  from_agent: string;
  to_agent: string;
  message_type: string;
  summary?: string;
  confidence?: number;
  priority?: 'low' | 'medium' | 'high' | 'emergency';
  reasoning?: string;
}

// Active pulse animation on a connection
export interface ConnectionPulse {
  id: string;
  from_agent: string;
  to_agent: string;
  color: string;
  startTime: number;
  duration: number; // ms
  message_type: string;
}

interface CommunicationState {
  // Recent communications (last 100)
  recent_communications: AgentCommunication[];
  
  // Active pulses for animation (auto-expire after duration)
  active_pulses: ConnectionPulse[];
  
  // Communication counts per connection (for line thickness)
  connection_counts: Record<string, number>; // "from→to" => count
  
  // Last update timestamp
  last_update: string | null;
}

const initialState: CommunicationState = {
  recent_communications: [],
  active_pulses: [],
  connection_counts: {},
  last_update: null,
};

// Agent hierarchy connections (who talks to whom)
// Based on the distributed agent protocol
export const AGENT_HIERARCHY = {
  // Sir Hawkington monitors and triages to VIC-20 and The Stick
  sir_hawkington: ['vic_20_sage', 'the_stick'],
  
  // VIC-20 coordinates with all specialists
  vic_20_sage: ['hamsters', 'meth_snail', 'quantum_shadow_people', 'the_stick'],
  
  // Specialists report back to VIC-20
  hamsters: ['vic_20_sage', 'the_stick'],
  meth_snail: ['vic_20_sage', 'the_stick'],
  quantum_shadow_people: ['vic_20_sage', 'the_stick'],
  
  // The Stick receives from everyone (universal logger)
  the_stick: [], // Receives only, doesn't initiate
};

// Color mapping for message types
export const MESSAGE_TYPE_COLORS: Record<string, string> = {
  TRIAGE_ALERT: '#e6ac00',      // Hawkington gold
  RECOMMENDED_FIX: '#06b6d4',   // VIC-20 cyan
  ACTION_REPORT: '#00d084',     // Success green
  DECISION_LOG: '#f97316',      // Stick coral
  COORDINATION_REQUEST: '#a855f7', // Purple
  EMERGENCY: '#ef4444',         // Red
  AGENT_LOG: '#06b6d4',         // VIC-20 cyan
  LOG: '#f97316',               // Stick coral
  ML_DECISION: '#a855f7',       // Purple
  SYSTEM: '#06b6d4',            // VIC-20 cyan
  default: '#6480fc',           // Rebellion blue
};

// Agent colors for fallback
const AGENT_COLORS: Record<string, string> = {
  sir_hawkington: '#e6ac00',
  vic_20_sage: '#06b6d4',
  meth_snail: '#00d084',
  the_stick: '#f97316',
  hamsters: '#ff8c42',
  quantum_shadow_people: '#a855f7',
};

// Normalize agent name to canonical form
const normalizeAgentName = (name: string): string => {
  // Backend sends vic20_sage, we need vic_20_sage
  if (name === 'vic20_sage') return 'vic_20_sage';
  return name;
};

// Valid agent names for pulse creation
const VALID_AGENTS = new Set([
  'sir_hawkington',
  'vic_20_sage',
  'meth_snail',
  'the_stick',
  'hamsters',
  'quantum_shadow_people',
]);

// Check if a communication should create a pulse (valid from/to agents)
const shouldCreatePulse = (comm: AgentCommunication): boolean => {
  const from = normalizeAgentName(comm.from_agent);
  const to = normalizeAgentName(comm.to_agent);
  return VALID_AGENTS.has(from) && 
         VALID_AGENTS.has(to) &&
         from !== to;
};

// Helper to create a pulse from a communication
const createPulseFromComm = (comm: AgentCommunication): ConnectionPulse => {
  const from = normalizeAgentName(comm.from_agent);
  const to = normalizeAgentName(comm.to_agent);
  
  // Determine color - prefer message type color, fall back to sender's color
  const color = MESSAGE_TYPE_COLORS[comm.message_type] || 
                AGENT_COLORS[from] || 
                MESSAGE_TYPE_COLORS.default;
  
  return {
    id: `pulse-${comm.id}-${Date.now()}`,
    from_agent: from,
    to_agent: to,
    color,
    startTime: Date.now(),
    duration: 2000, // 2 second animation
    message_type: comm.message_type,
  };
};

const communicationSlice = createSlice({
  name: 'communication',
  initialState,
  reducers: {
    // Add a new communication event
    addCommunication: (state, action: PayloadAction<AgentCommunication>) => {
      const comm = action.payload;
      
      // Normalize agent names
      const normalizedComm = {
        ...comm,
        from_agent: normalizeAgentName(comm.from_agent),
        to_agent: normalizeAgentName(comm.to_agent),
      };
      
      // Add to recent communications (keep last 100)
      state.recent_communications = [normalizedComm, ...state.recent_communications].slice(0, 100);
      
      // Update connection count
      const connectionKey = `${normalizedComm.from_agent}→${normalizedComm.to_agent}`;
      state.connection_counts[connectionKey] = (state.connection_counts[connectionKey] || 0) + 1;
      
      // Create a pulse animation if valid
      if (shouldCreatePulse(comm)) {
        const pulse = createPulseFromComm(comm);
        state.active_pulses.push(pulse);
      }
      
      state.last_update = new Date().toISOString();
    },
    
    // Bulk add communications (from system_update.recent_insights)
    setCommunications: (state, action: PayloadAction<AgentCommunication[]>) => {
      
      // Normalize all incoming communications
      const normalizedPayload = action.payload.map(comm => ({
        ...comm,
        from_agent: normalizeAgentName(comm.from_agent),
        to_agent: normalizeAgentName(comm.to_agent),
      }));
      
      // Merge new communications with existing ones, avoiding duplicates by ID
      const existingIds = new Set(state.recent_communications.map(c => c.id));
      const newComms = normalizedPayload.filter(c => !existingIds.has(c.id));
      
      // Prepend new communications and keep last 100
      state.recent_communications = [...newComms, ...state.recent_communications].slice(0, 100);
      
      // Create pulses for NEW communications only (not already processed)
      // Limit to most recent 3 to avoid pulse spam
      const commsForPulses = newComms.slice(0, 3);
      
      commsForPulses.forEach((comm: AgentCommunication) => {
        // Update connection count
        const connectionKey = `${comm.from_agent}→${comm.to_agent}`;
        state.connection_counts[connectionKey] = (state.connection_counts[connectionKey] || 0) + 1;
        
        // Create pulse if valid agents (already normalized)
        if (VALID_AGENTS.has(comm.from_agent) && 
            VALID_AGENTS.has(comm.to_agent) && 
            comm.from_agent !== comm.to_agent) {
          const pulse = createPulseFromComm(comm);
          state.active_pulses.push(pulse);
          console.log(`🔵 Created pulse: ${comm.from_agent} → ${comm.to_agent} (${comm.message_type})`);
        }
      });
      
      // Also update counts for remaining comms (but no pulses)
      newComms.slice(3).forEach((comm: AgentCommunication) => {
        const connectionKey = `${comm.from_agent}→${comm.to_agent}`;
        state.connection_counts[connectionKey] = (state.connection_counts[connectionKey] || 0) + 1;
      });
      
      state.last_update = new Date().toISOString();
    },
    
    // Remove expired pulses (called by animation loop)
    cleanupPulses: (state) => {
      const now = Date.now();
      const before = state.active_pulses.length;
      state.active_pulses = state.active_pulses.filter(
        pulse => (now - pulse.startTime) < pulse.duration
      );
      const after = state.active_pulses.length;
      if (before !== after) {
        console.log(`🧹 Cleaned up ${before - after} expired pulses, ${after} remaining`);
      }
    },
    
    // Clear all pulses
    clearPulses: (state) => {
      state.active_pulses = [];
    },
  },
});

export const { 
  addCommunication, 
  setCommunications, 
  cleanupPulses, 
  clearPulses 
} = communicationSlice.actions;

// Selectors
export const selectRecentCommunications = (state: RootState) => 
  state.communication.recent_communications;

export const selectActivePulses = (state: RootState) => 
  state.communication.active_pulses;

export const selectConnectionCounts = (state: RootState) => 
  state.communication.connection_counts;

// Get communications for a specific agent
export const selectAgentCommunications = (agentName: string) => (state: RootState) =>
  state.communication.recent_communications.filter(
    comm => comm.from_agent === agentName || comm.to_agent === agentName
  );

export default communicationSlice.reducer;