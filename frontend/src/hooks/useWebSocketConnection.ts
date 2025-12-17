// hooks/useWebSocketConnection.ts
import { useEffect, useRef, useCallback, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { WebSocketService } from '../services/websocket';
import { updateMetrics, setConnectionStatus, setError } from '../store/slices/metricSlice';
import { updateTriageData } from '../store/slices/triageSlice';
import { addAgentMemory } from '../store/slices/agentsSlice';
import { addCommunication, setCommunications, type AgentCommunication } from '../store/slices/communicationSlice';
import type { RootState } from '../store/store';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

interface LocalConnectionState {
  isConnecting: boolean;
  reconnectAttempts: number;
  lastError: string | null;
  backpressure: {
    bufferSize: number;
    pressure: number;
    droppedMessages: number;
  };
  circuitBreaker: {
    state: string;
    failures: number;
    waitTime: number;
  };
}

const MAX_RETRIES = 5;

export const useWebSocketConnection = () => {
  const dispatch = useDispatch();
  const auth = useSelector((state: RootState) => state.auth);
  const wsServiceRef = useRef<WebSocketService | null>(null);
  const isMountedRef = useRef(true);
  const connectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const intentionalCloseRef = useRef(false);
  
  const [localState, setLocalState] = useState<LocalConnectionState>({
    isConnecting: false,
    reconnectAttempts: 0,
    lastError: null,
    backpressure: {
      bufferSize: 0,
      pressure: 0,
      droppedMessages: 0
    },
    circuitBreaker: {
      state: 'CLOSED',
      failures: 0,
      waitTime: 0
    }
  });

  // Dev mode kill switch
  const isDisabled = import.meta.env.DEV && import.meta.env.VITE_DISABLE_WEBSOCKET === 'true';

  const handleMessage = useCallback((payload: any) => {
    // Check backpressure before processing
    if (wsServiceRef.current) {
      const backpressureStatus = wsServiceRef.current.getBackpressureStatus();
      
      // Update local state with backpressure info
      setLocalState(prev => ({
        ...prev,
        backpressure: {
          bufferSize: backpressureStatus.bufferSize,
          pressure: backpressureStatus.pressure,
          droppedMessages: backpressureStatus.droppedMessages
        }
      }));
      
      // If pressure is too high, we might skip non-critical updates
      if (backpressureStatus.pressure > 0.9 && payload.type !== 'error' && payload.type !== 'critical_update') {
        console.warn('🚨 High backpressure, skipping non-critical update');
        return;
      }
    }

    console.log('🔌 WebSocket message received:', payload.type);
    
    // Handle agent roster (initial message with active agents list)
    if (payload.type === 'agent_roster') {
      console.log('📋 Agent roster received:', payload.active_agents);
      if (payload.active_agents && Array.isArray(payload.active_agents)) {
        // Mark all agents as active
        payload.active_agents.forEach((agent_name: string) => {
          // Normalize agent name: vic_20_sage -> vic_20_sage
          const normalizedName = agent_name.replace('vic_20_sage', 'vic_20_sage');
          
          dispatch(addAgentMemory({
            agent_name: normalizedName as any,
            memory: { status: 'active', initialized: true }
          }));
        });
      }
    }
    // Handle unified system_update payload (new format)
    else if (payload.type === 'system_update') {
      // 1. UPDATE SYSTEM METRICS
      if (payload.metrics) {
        dispatch(updateMetrics({
          timestamp: payload.metrics.timestamp,
          cpu_usage: payload.metrics.cpu_usage,
          memory_usage: payload.metrics.memory_usage,
          disk_usage: payload.metrics.disk_usage,
          network_recv_rate: payload.metrics.network_recv_rate,
          network_sent_rate: payload.metrics.network_sent_rate,
          process_count: payload.metrics.process_count,
          cpu: payload.metrics.cpu,
          memory: payload.metrics.memory,
          disk: payload.metrics.disk,
          network: payload.metrics.network,
          system_info: payload.metrics.system_info
        }));
      }
      
      // 2. UPDATE AGENT DATA (includes triage, memory banks, etc.)
      if (payload.agents) {
        // Extract triage data from Sir Hawkington
        const hawkington = payload.agents.sir_hawkington;
        if (hawkington?.triage) {
          dispatch(updateTriageData({
            triage_decision: hawkington.triage
          }));
        }
        
        // Update agent memories for all agents
        Object.entries(payload.agents).forEach(([agent_name, agentData]: [string, any]) => {
          if (agentData) {
            dispatch(addAgentMemory({
              agent_name: agent_name as any, // Type assertion for agent name
              memory: {
                ...agentData,
                timestamp: payload.timestamp // Add top-level timestamp to each agent
              }
            }));
          }
        });
      }
      
      // 3. HANDLE RECENT INSIGHTS (inter-agent communications)
      if (payload.recent_insights && Array.isArray(payload.recent_insights)) {
        // Helper to recursively extract meaningful text from nested objects
        const extractMessage = (obj: any, depth: number = 0): string | null => {
          if (depth > 5 || !obj || typeof obj !== 'object') return null;
          
          // Check common message fields
          const messageFields = ['message', 'reasoning', 'action', 'content', 'summary', 'disposition', 'description', 'details'];
          for (const field of messageFields) {
            if (typeof obj[field] === 'string' && obj[field].length > 0) {
              return obj[field];
            }
          }
          
          // Check nested objects
          const nestedFields = ['payload', 'data', 'recommendation', 'triage', 'result'];
          for (const field of nestedFields) {
            if (obj[field]) {
              const nested = extractMessage(obj[field], depth + 1);
              if (nested) return nested;
            }
          }
          
          return null;
        };
        
        // Transform insights to AgentCommunication format
        const communications: AgentCommunication[] = payload.recent_insights.map((insight: any, index: number) => {
          // Aggressively extract summary from nested structure
          const summary = extractMessage(insight) || `${insight.type || insight.message_type || 'activity'}`;
          
          return {
            id: insight.id || `insight-${Date.now()}-${index}`,
            timestamp: insight.timestamp || new Date().toISOString(),
            from_agent: insight.from_agent || insight.agent_name || insight.sender || 'unknown',
            to_agent: insight.to_agent || insight.recipient || 'broadcast',
            message_type: insight.message_type || insight.type || insight.category?.toUpperCase() || 'AGENT_MESSAGE',
            summary,
            confidence: insight.confidence,
            priority: insight.priority || (insight.level === 'error' ? 'high' : insight.level === 'warning' ? 'medium' : 'low'),
          };
        });
        dispatch(setCommunications(communications));
      }
      
      // 4. HANDLE RECENT EVENTS (personality events - future use)
      // payload.recent_events is available for future use
      
    } 
    // Legacy format support (metrics_update)
    else if (payload.type === 'metrics_update' && payload.data) {
      const data = payload.data;
      
      dispatch(updateMetrics({
        timestamp: data.timestamp,
        cpu_usage: data.cpu_usage,
        memory_usage: data.memory_usage,
        disk_usage: data.disk_usage,
        network_recv_rate: data.network_recv_rate,
        network_sent_rate: data.network_sent_rate,
        process_count: data.process_count,
        cpu: data.cpu,
        memory: data.memory,
        disk: data.disk,
        network: data.network,
        system_info: data.system_info
      }));
      
      if (data.triage_decision || data.triage_stats || data.triage_processing) {
        dispatch(updateTriageData({
          triage_decision: data.triage_decision,
          triage_stats: data.triage_stats,
          triage_processing: data.triage_processing
        }));
      }
    } 
    else if (payload.type === 'connection_established') {
      dispatch(setConnectionStatus('connected'));
    } else if (payload.type === 'error') {
      dispatch(setError(payload.message || 'Unknown error'));
      setLocalState(prev => ({ ...prev, lastError: payload.message }));
    }
    // Handle real-time agent messages (for live pulse animations)
    else if (payload.type === 'agent_message' || payload.type === 'coordination_request' || 
             payload.type === 'triage_decision' || payload.type === 'agent_action') {
      const data = payload.data || payload;
      if (data.from_agent || data.sender) {
        dispatch(addCommunication({
          id: `live-${Date.now()}-${Math.random().toString(36).slice(2)}`,
          timestamp: data.timestamp || new Date().toISOString(),
          from_agent: data.from_agent || data.sender || 'unknown',
          to_agent: data.to_agent || data.recipient || data.target || 'broadcast',
          message_type: data.message_type || payload.type.toUpperCase(),
          summary: data.summary || data.message || data.action,
          confidence: data.confidence,
          priority: data.priority,
          action: data.action,
          context: data.context || {},
        }));
      }
    }
    // Handle agent log messages from backend logging system
    else if (payload.type === 'agent_log') {
      dispatch(addCommunication({
        id: `log-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        timestamp: payload.timestamp || new Date().toISOString(),
        from_agent: payload.agent_name || 'system',
        to_agent: 'system',
        message_type: payload.category?.toUpperCase() || 'LOG',
        summary: payload.message,
        priority: payload.level === 'error' ? 'high' : payload.level === 'warning' ? 'medium' : 'low',
        action: '',
        context: {},
      }));
    }
    // Ignore heartbeat messages - they're just keepalive pings
    else if (payload.type === 'heartbeat') {
      // Do nothing - heartbeats are not agent activity
    }
  }, [dispatch]);

  const connect = useCallback(async () => {
    if (isDisabled) {
      console.warn('🚨 WebSocket disabled in dev mode');
      return;
    }

    if (auth.isInitializing) {
      console.log('🔒 Auth still initializing, skipping websocket connect attempt');
      return;
    }

    // Check if component is still mounted
    if (!isMountedRef.current) {
      console.log('Component unmounted, skipping connection');
      return;
    }

    if (!auth.isAuthenticated || !auth.token) {
      console.log('🔒 No authenticated user/token available, skipping websocket connect');
      return;
    }

    // Check if we already have an active connection
    if (wsServiceRef.current?.isConnected()) {
      console.log('🔌 Already connected, skipping');
      return;
    }

    // Skip the getConnectionState check since it doesn't exist yet
    // Just check isConnecting from our local state
    if (localState.isConnecting) {
      console.log('🔌 Already connecting, skipping duplicate attempt');
      return;
    }

    // Prevent infinite retry loops
    if (localState.reconnectAttempts >= MAX_RETRIES) {
      console.error('Max WebSocket retries exceeded, giving up');
      dispatch(setError('Connection failed after multiple attempts'));
      return;
    }

    try {
      setLocalState(prev => ({ ...prev, isConnecting: true }));
      dispatch(setConnectionStatus('connecting'));
      
      // Get singleton instance
      wsServiceRef.current = WebSocketService.getInstance(WS_BASE_URL);
      
      // Check circuit breaker status
      const cbStatus = wsServiceRef.current.getCircuitBreakerStatus();
      setLocalState(prev => ({
        ...prev,
        circuitBreaker: cbStatus
      }));
      
      // If circuit is open, wait before attempting
      if (cbStatus.waitTime > 0) {
        console.log(`⏳ Circuit breaker active, waiting ${cbStatus.waitTime.toFixed(1)}s`);
        dispatch(setError(`Circuit breaker open - wait ${cbStatus.waitTime.toFixed(1)}s`));
        setLocalState(prev => ({ 
          ...prev, 
          isConnecting: false,
          lastError: `Circuit breaker open - wait ${cbStatus.waitTime.toFixed(1)}s`
        }));
        
        // Schedule retry after wait time
        connectTimeoutRef.current = setTimeout(() => {
          if (isMountedRef.current) {
            connect();
          }
        }, cbStatus.waitTime * 1000);
        return;
      }
      
      // Set up error handlers
      wsServiceRef.current.onError = (evt) => {
        console.error('❌ WebSocket error:', evt);
        const errorMsg = 'Connection error';
        dispatch(setError(errorMsg));
        setLocalState(prev => ({ 
          ...prev, 
          lastError: errorMsg,
          isConnecting: false 
        }));
      };
      
      wsServiceRef.current.onClose = (event?: CloseEvent) => {
        const closeCode = event?.code;
        const closeReason = event?.reason || 'unknown';
        console.log(`🔌 WebSocket closed (code: ${closeCode}, reason: ${closeReason})`);
        dispatch(setConnectionStatus('disconnected'));
        setLocalState(prev => ({ ...prev, isConnecting: false }));
        
        // Don't reconnect on auth failures (code 1008 = WS_1008_POLICY_VIOLATION)
        if (closeCode === 1008) {
          console.error('🔒 WebSocket closed due to auth failure - token may be expired');
          dispatch(setError('Authentication failed - please refresh your session'));
          setLocalState(prev => ({ 
            ...prev, 
            lastError: 'Authentication failed - token expired or invalid',
            reconnectAttempts: MAX_RETRIES // Prevent further reconnect attempts
          }));
          return;
        }
        
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
      
      // Subscribe to messages BEFORE connecting
      wsServiceRef.current.subscribe(handleMessage);
      
      // Ensure connection to the system-metrics endpoint
      wsServiceRef.current.ensureConnected('/api/ws/system-metrics');
      
      // Wait for connection with circuit breaker protection
      // Backend auth can take ~30s, so allow 45s timeout
      await wsServiceRef.current.waitUntilOpen(45000, 3, 2000);
      
      console.log('✅ WebSocket connected to system-metrics');
      dispatch(setConnectionStatus('connected'));
      setLocalState(prev => ({
        ...prev,
        isConnecting: false,
        reconnectAttempts: 0,
        lastError: null,
        backpressure: wsServiceRef.current?.getBackpressureStatus() || prev.backpressure,
        circuitBreaker: wsServiceRef.current?.getCircuitBreakerStatus() || prev.circuitBreaker
      }));
      
    } catch (error) {
      console.error('❌ Failed to connect WebSocket:', error);
      const errorMsg = error instanceof Error ? error.message : 'Connection failed';
      
      dispatch(setError(errorMsg));
      setLocalState(prev => ({
        ...prev,
        isConnecting: false,
        reconnectAttempts: prev.reconnectAttempts + 1,
        lastError: errorMsg,
        circuitBreaker: wsServiceRef.current?.getCircuitBreakerStatus() || prev.circuitBreaker,
        backpressure: wsServiceRef.current?.getBackpressureStatus() || prev.backpressure
      }));
    }
  }, [auth.isAuthenticated, auth.isInitializing, auth.token, handleMessage, isDisabled, dispatch]);

  // Initial connection
  useEffect(() => {
    isMountedRef.current = true;

    if (!isDisabled && !auth.isInitializing && auth.isAuthenticated && auth.token) {
      // Small delay to avoid React StrictMode double-mount race
      connectTimeoutRef.current = setTimeout(() => {
        if (isMountedRef.current && !localState.isConnecting) {
          connect();
        }
      }, 100);
    }

    // Cleanup function
    return () => {
      isMountedRef.current = false;
      
      // Clear any pending connection attempts
      if (connectTimeoutRef.current) {
        clearTimeout(connectTimeoutRef.current);
        connectTimeoutRef.current = null;
      }
      
      // Unsubscribe from messages but DON'T close the WebSocket
      // The WebSocket is a singleton that should persist across component mounts
      // This is especially important in React StrictMode which double-mounts components
      if (wsServiceRef.current) {
        wsServiceRef.current.unsubscribe(handleMessage);
        // Don't close or null out the service - let it persist
      }
    };
  }, []); // Empty deps - only run on mount/unmount!

  useEffect(() => {
    if (isDisabled) {
      return;
    }

    if (auth.isInitializing) {
      return;
    }

    if (!auth.isAuthenticated || !auth.token) {
      intentionalCloseRef.current = true;
      if (connectTimeoutRef.current) {
        clearTimeout(connectTimeoutRef.current);
        connectTimeoutRef.current = null;
      }
      if (wsServiceRef.current) {
        wsServiceRef.current.unsubscribe(handleMessage);
        wsServiceRef.current.close();
        wsServiceRef.current = null;
      }
      setLocalState(prev => {
        if (!prev.isConnecting && prev.reconnectAttempts === 0 && prev.lastError === null) {
          return prev;
        }
        return {
          ...prev,
          isConnecting: false,
          reconnectAttempts: 0,
          lastError: null,
        };
      });
      dispatch(setConnectionStatus('disconnected'));
      return;
    }
  }, [auth.isAuthenticated, auth.isInitializing, auth.token, dispatch, isDisabled, handleMessage]);

  // Manual reconnect with circuit breaker reset
  const reconnect = useCallback(() => {
    console.log('Manual reconnect requested');
    intentionalCloseRef.current = true;
    if (wsServiceRef.current) {
      wsServiceRef.current.resetCircuitBreaker();
      wsServiceRef.current.close();
    }
    setLocalState(prev => ({
      ...prev,
      isConnecting: false,
      reconnectAttempts: 0,  // Reset retry count on manual reconnect
      lastError: null,
      circuitBreaker: {
        state: 'CLOSED',
        failures: 0,
        waitTime: 0
      }
    }));
    connectTimeoutRef.current = setTimeout(() => {
      if (isMountedRef.current) {
        intentionalCloseRef.current = false;
        connect();
      }
    }, 100);
  }, [connect]);

  // Get resilience stats
  const getResilienceStats = useCallback(() => {
    if (!wsServiceRef.current) {
      return null;
    }
    
    return {
      circuitBreaker: wsServiceRef.current.getCircuitBreakerStatus(),
      backpressure: wsServiceRef.current.getBackpressureStatus()
    };
  }, []);

  return {
    connectionStatus: localState.isConnecting ? 'connecting' : 
                     wsServiceRef.current?.isConnected() ? 'connected' : 'disconnected',
    isConnected: wsServiceRef.current?.isConnected() || false,
    lastError: localState.lastError,
    reconnectAttempts: localState.reconnectAttempts,
    isConnecting: localState.isConnecting,
    reconnect,
    resilienceStats: localState,
    getResilienceStats
  };
};