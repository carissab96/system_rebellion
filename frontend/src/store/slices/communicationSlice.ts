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
  // Recent communications (last 50)
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
  sir_hawkington: ['vic20_sage', 'the_stick'],
  
  // VIC-20 coordinates with all specialists
  vic20_sage: ['hamsters', 'meth_snail', 'quantum_shadow_people', 'the_stick'],
  
  // Specialists report back to VIC-20
  hamsters: ['vic20_sage', 'the_stick'],
  meth_snail: ['vic20_sage', 'the_stick'],
  quantum_shadow_people: ['vic20_sage', 'the_stick'],
  
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
  default: '#6480fc',           // Rebellion blue
};

const communicationSlice = createSlice({
  name: 'communication',
  initialState,
  reducers: {
    // Add a new communication event
    addCommunication: (state, action: PayloadAction<AgentCommunication>) => {
      const comm = action.payload;
      
      // Add to recent communications (keep last 50)
      state.recent_communications = [comm, ...state.recent_communications].slice(0, 50);
      
      // Update connection count
      const connectionKey = `${comm.from_agent}→${comm.to_agent}`;
      state.connection_counts[connectionKey] = (state.connection_counts[connectionKey] || 0) + 1;
      
      // Create a pulse animation
      const pulse: ConnectionPulse = {
        id: `pulse-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        from_agent: comm.from_agent,
        to_agent: comm.to_agent,
        color: MESSAGE_TYPE_COLORS[comm.message_type] || MESSAGE_TYPE_COLORS.default,
        startTime: Date.now(),
        duration: 2000, // 2 second animation
        message_type: comm.message_type,
      };
      state.active_pulses.push(pulse);
      
      state.last_update = new Date().toISOString();
    },
    
    // Bulk add communications (from system_update.recent_insights)
    setCommunications: (state, action: PayloadAction<AgentCommunication[]>) => {
      // Merge new communications with existing ones, avoiding duplicates by ID
      const existingIds = new Set(state.recent_communications.map(c => c.id));
      const newComms = action.payload.filter(c => !existingIds.has(c.id));
      
      // Prepend new communications and keep last 100
      state.recent_communications = [...newComms, ...state.recent_communications].slice(0, 100);
      
      // Update connection counts for new communications only
      newComms.forEach((comm: AgentCommunication) => {
        const connectionKey = `${comm.from_agent}→${comm.to_agent}`;
        state.connection_counts[connectionKey] = (state.connection_counts[connectionKey] || 0) + 1;
      });
      
      state.last_update = new Date().toISOString();
    },
    
    // Remove expired pulses (called by animation loop)
    cleanupPulses: (state) => {
      const now = Date.now();
      state.active_pulses = state.active_pulses.filter(
        pulse => (now - pulse.startTime) < pulse.duration
      );
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
