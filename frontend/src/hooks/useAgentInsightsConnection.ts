// hooks/useAgentInsightsConnection.ts
// Hook for agent insights WebSocket connection
// Modeled after useWebSocketConnection.ts

import { useEffect, useRef, useCallback, useState } from 'react';
import { useDispatch } from 'react-redux';
import { AgentInsightsWebSocketService } from '../services/agentInsightsWebSocket';
import { addAgentMemory } from '../store/slices/agentsSlice';
import type { AgentActivityMessage } from '../types/websocketMessages';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

type AgentName = 'sir_hawkington' | 'the_stick' | 'meth_snail' | 'hamsters' | 'quantum_shadow_people' | 'vic20_sage';

interface LocalConnectionState {
  isConnecting: boolean;
  reconnectAttempts: number;
  lastError: string | null;
}

const MAX_RETRIES = 5;

export const useAgentInsightsConnection = () => {
  const dispatch = useDispatch();
  const wsServiceRef = useRef<AgentInsightsWebSocketService | null>(null);
  const isMountedRef = useRef(true);
  const connectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const [localState, setLocalState] = useState<LocalConnectionState>({
    isConnecting: false,
    reconnectAttempts: 0,
    lastError: null
  });

  // Dev mode kill switch
  const isDisabled = import.meta.env.DEV && import.meta.env.VITE_DISABLE_WEBSOCKET === 'true';

  const handleMessage = useCallback((payload: any) => {
    console.log('🤖 Agent Insights message received:', payload.type, payload);
    
    if (payload.type === 'agent_insight') {
      // Real-time agent method execution event
      const { agent_name, event_type, method_name, timestamp } = payload;
      
      // Dispatch as agent memory update (live activity)
      dispatch(addAgentMemory({
        agent_name: agent_name as AgentName,
        memory: {
          memory_id: `${event_type}_${agent_name}_${Date.now()}`,
          user_id: '',
          timestamp: timestamp,
          shared_with_central: true,
          central_memory_id: '',
          activity_type: event_type,
          activity_data: {
            method_name,
            event_type,
            ...payload
          },
          is_live_activity: true
        }
      }));
    } else if (payload.type === 'agent_activity') {
      const msg = payload as AgentActivityMessage;
      
      // Dispatch as agent memory update (live activity)
      dispatch(addAgentMemory({
        agent_name: msg.agent_name as AgentName,
        memory: {
          memory_id: `activity_${msg.agent_name}_${Date.now()}`,
          user_id: '',
          timestamp: msg.timestamp,
          shared_with_central: true,
          central_memory_id: '',
          activity_type: msg.activity_type,
          activity_data: msg.data,
          is_live_activity: true
        }
      }));
    } else if (payload.type === 'connected') {
      console.log('✅ Agent insights connected:', payload.message);
    } else if (payload.type === 'error') {
      console.error('❌ Agent insights error:', payload.message);
    }
  }, [dispatch]);

  const connect = useCallback(async () => {
    if (isDisabled) {
      console.warn('🚨 Agent Insights WebSocket disabled in dev mode');
      return;
    }

    if (!isMountedRef.current) {
      console.log('Component unmounted, skipping connection');
      return;
    }

    if (wsServiceRef.current?.isConnected()) {
      console.log('🔌 Agent Insights already connected, skipping');
      return;
    }

    if (localState.isConnecting) {
      console.log('🔌 Agent Insights already connecting, skipping duplicate attempt');
      return;
    }

    // Prevent infinite retry loops
    if (localState.reconnectAttempts >= MAX_RETRIES) {
      console.error('Max Agent Insights retries exceeded, giving up');
      return;
    }

    try {
      setLocalState(prev => ({ ...prev, isConnecting: true }));
      
      // Get singleton instance
      console.log('🔌 Agent Insights: Getting instance with base URL:', WS_BASE_URL);
      wsServiceRef.current = AgentInsightsWebSocketService.getInstance(WS_BASE_URL);
      
      // Check circuit breaker status
      const cbStatus = wsServiceRef.current.getCircuitBreakerStatus();
      const waitTime = cbStatus.waitTime || 0;
      
      if (waitTime > 0) {
        console.log(`⏳ Agent Insights circuit breaker active, waiting ${waitTime.toFixed(1)}s`);
        setLocalState(prev => ({ 
          ...prev, 
          isConnecting: false,
          lastError: `Circuit breaker open - wait ${waitTime.toFixed(1)}s`
        }));
        
        connectTimeoutRef.current = setTimeout(() => {
          if (isMountedRef.current) {
            connect();
          }
        }, waitTime * 1000);
        return;
      }
      
      // Set up error handlers
      wsServiceRef.current.onError = (evt) => {
        console.error('❌ Agent Insights WebSocket error:', evt);
        setLocalState(prev => ({ 
          ...prev, 
          lastError: 'Connection error',
          isConnecting: false 
        }));
      };
      
      wsServiceRef.current.onClose = () => {
        console.log('🔌 Agent Insights WebSocket closed - attempting reconnection in 3s');
        setLocalState(prev => ({ ...prev, isConnecting: false }));
        
        if (isMountedRef.current) {
          connectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              console.log('🔄 Attempting to reconnect Agent Insights WebSocket...');
              connect();
            }
          }, 3000);
        }
      };
      
      // Subscribe to messages BEFORE connecting
      wsServiceRef.current.subscribe(handleMessage);
      
      // Ensure connection (use default path from service)
      console.log('🔌 Agent Insights: Calling ensureConnected()');
      wsServiceRef.current.ensureConnected();
      console.log('🔌 Agent Insights: ensureConnected() completed');
      
      // Wait for connection (increased timeout for auth + connection)
      await wsServiceRef.current.waitUntilOpen(10000);
      
      console.log('✅ Agent Insights WebSocket connected');
      setLocalState(prev => ({
        ...prev,
        isConnecting: false,
        reconnectAttempts: 0,
        lastError: null
      }));
      
    } catch (error) {
      console.error('❌ Failed to connect Agent Insights WebSocket:', error);
      const errorMsg = error instanceof Error ? error.message : 'Connection failed';
      
      setLocalState(prev => ({
        ...prev,
        isConnecting: false,
        reconnectAttempts: prev.reconnectAttempts + 1,
        lastError: errorMsg
      }));
    }
  }, [handleMessage, isDisabled, localState.isConnecting]);

  // Initial connection
  useEffect(() => {
    isMountedRef.current = true;
    
    if (!isDisabled) {
      connectTimeoutRef.current = setTimeout(() => {
        if (isMountedRef.current && !localState.isConnecting) {
          connect();
        }
      }, 100);
    }

    return () => {
      isMountedRef.current = false;
      
      if (connectTimeoutRef.current) {
        clearTimeout(connectTimeoutRef.current);
      }
      
      if (wsServiceRef.current) {
        wsServiceRef.current.unsubscribe(handleMessage);
      }
    };
  }, []);

  // Manual reconnect
  const reconnect = useCallback(() => {
    console.log('Manual Agent Insights reconnect requested');
    if (wsServiceRef.current) {
      wsServiceRef.current.resetCircuitBreaker();
      wsServiceRef.current.close();
    }
    setLocalState(prev => ({
      ...prev,
      isConnecting: false,
      reconnectAttempts: 0,
      lastError: null
    }));
    connectTimeoutRef.current = setTimeout(() => {
      if (isMountedRef.current) {
        connect();
      }
    }, 100);
  }, [connect]);

  return {
    isConnected: wsServiceRef.current?.isConnected() || false,
    lastError: localState.lastError,
    reconnectAttempts: localState.reconnectAttempts,
    isConnecting: localState.isConnecting,
    reconnect
  };
};
