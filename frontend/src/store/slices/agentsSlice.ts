// store/slices/agentsSlice.ts
import { createSlice, createSelector, type PayloadAction } from '@reduxjs/toolkit';
import type {
  SirHawkingtonMemory,
  TheStickMemory,
  MethSnailMemory,
  HamstersMemory,
  QuantumShadowPeopleMemory,
  VIC20Memory
} from '../../types/agents';

// UI Display data derived from memories
export interface AgentDisplayData {
  agent_name: string;
  status: 'active' | 'idle' | 'processing' | 'error';
  last_activity: string | null;
  recent_memories: any[]; // Array of agent-specific memory types
  summary_stats: {
    total_events: number;
    recent_events_24h: number;
    avg_confidence?: number;
    effectiveness_score?: number;
  };
}

interface AgentsState {
  // Recent memories for each agent (last 10)
  sir_hawkington: {
    recent_memories: SirHawkingtonMemory[];
    display_data: AgentDisplayData | null;
  };
  the_stick: {
    recent_memories: TheStickMemory[];
    display_data: AgentDisplayData | null;
  };
  meth_snail: {
    recent_memories: MethSnailMemory[];
    display_data: AgentDisplayData | null;
  };
  hamsters: {
    recent_memories: HamstersMemory[];
    display_data: AgentDisplayData | null;
  };
  quantum_shadow_people: {
    recent_memories: QuantumShadowPeopleMemory[];
    display_data: AgentDisplayData | null;
  };
  vic_20_sage: {
    recent_memories: VIC20Memory[];
    display_data: AgentDisplayData | null;
  };
  
  // Aggregate state
  last_update: string | null;
  active_agents: string[];
}

const initialState: AgentsState = {
  sir_hawkington: { recent_memories: [], display_data: null },
  the_stick: { recent_memories: [], display_data: null },
  meth_snail: { recent_memories: [], display_data: null },
  hamsters: { recent_memories: [], display_data: null },
  quantum_shadow_people: { recent_memories: [], display_data: null },
  vic_20_sage: { recent_memories: [], display_data: null },
  last_update: null,
  active_agents: []
};

type AgentName = 'sir_hawkington' | 'the_stick' | 'meth_snail' | 'hamsters' | 'quantum_shadow_people' | 'vic_20_sage';

const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    addAgentMemory: (state, action: PayloadAction<{
      agent_name: AgentName;
      memory: any; // Type varies by agent
    }>) => {
      const { agent_name, memory } = action.payload;
      const agent = state[agent_name];
      
      // Safety check - ensure agent exists and has recent_memories array
      if (!agent) {
        console.error(`Agent ${agent_name} not found in state`);
        return;
      }
      if (!agent.recent_memories) {
        agent.recent_memories = [];
      }
      
      // Add to recent memories (keep last 10)
      agent.recent_memories = [memory, ...agent.recent_memories].slice(0, 10);
      
      // Calculate average confidence if available
      let avg_confidence: number | undefined;
      const confidenceValues = agent.recent_memories
        .map((m: any) => {
          // Extract confidence from different agent structures
          if (m.triage_decision_context?.confidence) return m.triage_decision_context.confidence;
          if (m.confidence_level) return m.confidence_level;
          if (m.quantum_confidence) return m.quantum_confidence;
          return null;
        })
        .filter((c): c is number => c !== null);
      
      if (confidenceValues.length > 0) {
        avg_confidence = confidenceValues.reduce((a, b) => a + b, 0) / confidenceValues.length;
      }
      
      // Update display data - NO MAPPING, pass backend data directly
      agent.display_data = {
        agent_name,
        status: memory.status || 'active',
        last_activity: memory.timestamp || memory.last_heartbeat || new Date().toISOString(),
        summary_stats: {
          total_events: agent.recent_memories.length,
          recent_events_24h: agent.recent_memories.filter((m: any) => {
            const memTime = new Date(m.timestamp).getTime();
            const dayAgo = Date.now() - 24 * 60 * 60 * 1000;
            return memTime > dayAgo;
          }).length,
          avg_confidence
        },
        // Pass all backend data directly - cards consume it as-is
        ...memory
      };
      
      state.last_update = new Date().toISOString();
      
      // Update active agents list
      if (!state.active_agents.includes(agent_name)) {
        state.active_agents.push(agent_name);
      }
    },
    
    clearAgentMemories: (state, action: PayloadAction<AgentName>) => {
      const agent_name = action.payload;
      state[agent_name].recent_memories = [];
      state[agent_name].display_data = null;
      state.active_agents = state.active_agents.filter(a => a !== agent_name);
    },
    
    resetAllAgents: () => {
      return initialState;
    },
    
    setAgentStatus: (state, action: PayloadAction<{
      agent_name: AgentName;
      status: 'active' | 'idle' | 'processing' | 'error';
    }>) => {
      const { agent_name, status } = action.payload;
      if (state[agent_name].display_data) {
        state[agent_name].display_data!.status = status;
      }
    }
  }
});

export const { addAgentMemory, clearAgentMemories, resetAllAgents, setAgentStatus } = agentsSlice.actions;
export default agentsSlice.reducer;

// Selectors
export const selectAgentData = (agentName: AgentName) => 
  (state: { agents: AgentsState }) => state.agents[agentName];

export const selectActiveAgentCount = (state: { agents: AgentsState }) => 
  state.agents.active_agents.length;

// Memoized selector to prevent unnecessary re-renders
const selectAgentsState = (state: { agents: AgentsState }) => state.agents;

export const selectAllAgentDisplayData = createSelector(
  [selectAgentsState],
  (agentsState) => {
    const agents: AgentName[] = ['sir_hawkington', 'the_stick', 'meth_snail', 'hamsters', 'quantum_shadow_people', 'vic_20_sage'];
    return agents
      .map(name => agentsState[name].display_data)
      .filter((data): data is AgentDisplayData => data !== null);
  }
);