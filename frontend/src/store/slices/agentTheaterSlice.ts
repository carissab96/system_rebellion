// store/slices/agentTheaterSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface AgentTheaterState {
  sirHawkington: any;
  methSnail: any;
  hamsters: any;
  quantumShadow: any;
  theStick: any;
  vic20: any;
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
  lastUpdate: Date | null;
  error: string | null;
  activeAgentCount: number;
  totalAgents: number;
  systemInfo: any;
  circuitBreakerStatus: 'closed' | 'open' | 'half_open';
}

const initialState: AgentTheaterState = {
  connectionStatus: 'connecting',
  lastUpdate: null,
  error: null,
  activeAgentCount: 0,
  totalAgents: 6,
  systemInfo: null,
  circuitBreakerStatus: 'closed',
};

export const agentTheaterSlice = createSlice({
  name: 'agentTheater',
  initialState,
  reducers: {
    setConnectionStatus: (state, action: PayloadAction<'connecting' | 'connected' | 'disconnected'>) => {
      state.connectionStatus = action.payload;
      if (action.payload === 'connected') {
        state.error = null;
      }
    },
    
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    
    clearError: (state) => {
      state.error = null;
    },
    
    updateLastUpdate: (state) => {
      state.lastUpdate = new Date();
    },
    
    updateActiveAgentCount: (state, action: PayloadAction<number>) => {
      state.activeAgentCount = action.payload;
    },
    
    setSystemInfo: (state, action: PayloadAction<any>) => {
      state.systemInfo = action.payload;
    },
    
    setCircuitBreakerStatus: (state, action: PayloadAction<'closed' | 'open' | 'half_open'>) => {
      state.circuitBreakerStatus = action.payload;
    },
    
    // Handle WebSocket messages and route to appropriate agents
    updateWebSocketMessage: (state: AgentTheaterState, action: PayloadAction<any>) => {
      const message = action.payload;
      
      switch (message.type) {
        case 'connection_established':
          state.connectionStatus = 'connected';
          state.error = null;
          break;
          
        case 'system_info':
          state.systemInfo = message.data;
          break;
          
        case 'metrics_update':
          state.lastUpdate = new Date();
          // Individual agent slices will handle their own data
          break;
          
        case 'circuit_breaker':
          state.circuitBreakerStatus = message.status === 'open' ? 'open' : 'closed';
          break;
          
        case 'connection_error':
          state.error = message.message;
          break;
      }
    },
  },
});

export const { 
  setConnectionStatus, 
  setError, 
  clearError, 
  updateLastUpdate, 
  updateActiveAgentCount,
  setSystemInfo,
  setCircuitBreakerStatus,
  updateWebSocketMessage 
} = agentTheaterSlice.actions;

export default agentTheaterSlice.reducer;
