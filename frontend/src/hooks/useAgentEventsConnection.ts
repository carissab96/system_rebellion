// hooks/useAgentEventsConnection.ts
// Hook for agent events WebSocket connection
// Modeled after useWebSocketConnection.ts

import { useEffect, useRef, useCallback, useState } from 'react';
import { useDispatch } from 'react-redux';
import { AgentEventsWebSocketService } from '../services/agentEventsWebSocket';
import { addAgentMemory } from '../store/slices/agentsSlice';
import type { AgentEventMessage, RecentEventsMessage } from '../types/websocketMessages';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

type AgentName = 'sir_hawkington' | 'the_stick' | 'meth_snail' | 'hamsters' | 'quantum_shadow_people' | 'vic20_sage';

interface LocalConnectionState {
  isConnecting: boolean;
  reconnectAttempts: number;
  lastError: string | null;
}

export const useAgentEventsConnection = () => {
  const dispatch = useDispatch();
  const wsServiceRef = useRef<AgentEventsWebSocketService | null>(null);
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
    console.log('🎭 Agent Events message received:', payload.type);
    
    if (payload.type === 'agent_event') {
      const msg = payload as AgentEventMessage;
      const event = msg.event;
      
      // Dispatch as agent memory update (personality event)
      dispatch(addAgentMemory({
        agent_name: event.agent_name as AgentName,
        memory: {
          memory_id: `event_${event.id}`,
          user_id: '',
          timestamp: event.timestamp,
          shared_with_central: true,
          central_memory_id: '',
          event_type: event.event_type,
          event_data: event.event_data,
          severity: event.severity,
          agent_state: event.agent_state,
          is_personality_event: true
        }
      }));
    } else if (payload.type === 'recent_events') {
      const msg = payload as RecentEventsMessage;
      console.log(`📜 Received ${msg.events.length} recent events`);
      
      // Dispatch all recent events
      msg.events.forEach(event => {
        dispatch(addAgentMemory({
          agent_name: event.agent_name as AgentName,
          memory: {
            memory_id: `event_${event.id}`,
            user_id: '',
            timestamp: event.timestamp,
            shared_with_central: true,
            central_memory_id: '',
            event_type: event.event_type,
            event_data: event.event_data,
            severity: event.severity,
            agent_state: event.agent_state,
            is_personality_event: true
          }
        }));
      });
    } else if (payload.type === 'connected') {
      console.log('✅ Agent events connected:', payload.message);
    } else if (payload.type === 'error') {
      console.error('❌ Agent events error:', payload.message);
    }
  }, [dispatch]);

  const connect = useCallback(async () => {
    if (isDisabled) {
      console.warn('🚨 Agent Events WebSocket disabled in dev mode');
      return;
    }

    if (!isMountedRef.current) {
      console.log('Component unmounted, skipping connection');
      return;
    }

    if (wsServiceRef.current?.isConnected()) {
      console.log('🔌 Agent Events already connected, skipping');
      return;
    }

    if (localState.isConnecting) {
      console.log('🔌 Agent Events already connecting, skipping duplicate attempt');
      return;
    }

    try {
      setLocalState(prev => ({ ...prev, isConnecting: true }));
      
      // Get singleton instance
      console.log('🎭 Agent Events: Getting instance with base URL:', WS_BASE_URL);
      wsServiceRef.current = AgentEventsWebSocketService.getInstance(WS_BASE_URL);
      
      // Check circuit breaker status
      const cbStatus = wsServiceRef.current.getCircuitBreakerStatus();
      const waitTime = cbStatus.waitTime || 0;
      
      if (waitTime > 0) {
        console.log(`⏳ Agent Events circuit breaker active, waiting ${waitTime.toFixed(1)}s`);
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
        console.error('❌ Agent Events WebSocket error:', evt);
        setLocalState(prev => ({ 
          ...prev, 
          lastError: 'Connection error',
          isConnecting: false 
        }));
      };
      
      wsServiceRef.current.onClose = () => {
        console.log('🔌 Agent Events WebSocket closed - attempting reconnection in 3s');
        setLocalState(prev => ({ ...prev, isConnecting: false }));
        
        if (isMountedRef.current) {
          connectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              console.log('🔄 Attempting to reconnect Agent Events WebSocket...');
              connect();
            }
          }, 3000);
        }
      };
      
      // Subscribe to messages BEFORE connecting
      wsServiceRef.current.subscribe(handleMessage);
      
      // Ensure connection (use default path from service)
      console.log('🎭 Agent Events: Calling ensureConnected()');
      wsServiceRef.current.ensureConnected();
      console.log('🎭 Agent Events: ensureConnected() completed');
      
      // Wait for connection (increased timeout for auth + connection)
      await wsServiceRef.current.waitUntilOpen(10000);
      
      console.log('✅ Agent Events WebSocket connected');
      setLocalState(prev => ({
        ...prev,
        isConnecting: false,
        reconnectAttempts: 0,
        lastError: null
      }));
      
    } catch (error) {
      console.error('❌ Failed to connect Agent Events WebSocket:', error);
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
    console.log('Manual Agent Events reconnect requested');
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

  // Helper to request recent events
  const requestRecentEvents = useCallback((limit: number = 20) => {
    if (wsServiceRef.current?.isConnected()) {
      wsServiceRef.current.send({ type: 'get_recent', limit });
    }
  }, []);

  return {
    isConnected: wsServiceRef.current?.isConnected() || false,
    lastError: localState.lastError,
    reconnectAttempts: localState.reconnectAttempts,
    isConnecting: localState.isConnecting,
    reconnect,
    requestRecentEvents
  };
};
