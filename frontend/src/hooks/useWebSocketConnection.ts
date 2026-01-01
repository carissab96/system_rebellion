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

// Agent names for routing detection
const AGENT_NAMES = [
  'sir_hawkington',
  'vic_20_sage', 
  'meth_snail',
  'the_stick',
  'hamsters',
  'quantum_shadow_people'
];

// Aliases that might appear in messages
const AGENT_ALIASES: Record<string, string> = {
  'hawkington': 'sir_hawkington',
  'hawk': 'sir_hawkington',
  'vic20': 'vic_20_sage',
  'vic-20': 'vic_20_sage',
  'vic20_sage': 'vic_20_sage',
  'terry': 'meth_snail',
  'snail': 'meth_snail',
  'stick': 'the_stick',
  'hamster': 'hamsters',
  'qsp': 'quantum_shadow_people',
  'quantum': 'quantum_shadow_people',
  'shadow': 'quantum_shadow_people',
};

/**
 * Extract the target agent from a message based on content analysis
 */
const extractToAgent = (message: string, fromAgent: string, messageType?: string): string => {
  const lowerMessage = message.toLowerCase();
  
  // 1. Check for explicit "to X" or "→ X" patterns
  const toPatterns = [
    /(?:sent to|route to|routing to|forwarding to|→)\s+(\w+)/i,
    /coordination request sent to\s+(\w+)/i,
    /requesting.*?from\s+(\w+)/i,
  ];
  
  for (const pattern of toPatterns) {
    const match = message.match(pattern);
    if (match) {
      const target = match[1].toLowerCase();
      // Check if it's a known agent or alias
      if (AGENT_NAMES.includes(target)) {
        return target;
      }
      if (AGENT_ALIASES[target]) {
        return AGENT_ALIASES[target];
      }
      // Partial match - check if any agent name contains this
      const partialMatch = AGENT_NAMES.find(a => a.includes(target) || target.includes(a.replace('_', '')));
      if (partialMatch && partialMatch !== fromAgent) {
        return partialMatch;
      }
    }
  }
  
  // 2. Check for agent mentions in the message
  for (const [alias, agentName] of Object.entries(AGENT_ALIASES)) {
    if (lowerMessage.includes(alias) && agentName !== fromAgent) {
      // Make sure it's not just the sender being mentioned
      const mentionContext = lowerMessage.split(alias)[0].slice(-20);
      if (mentionContext.includes('to') || mentionContext.includes('→') || mentionContext.includes('request')) {
        return agentName;
      }
    }
  }
  
  // 3. Infer routing based on sender and message type
  // Hawk sends triage alerts to VIC-20
  if (fromAgent === 'sir_hawkington') {
    if (lowerMessage.includes('triage') || lowerMessage.includes('emergency') || lowerMessage.includes('alert')) {
      return 'vic_20_sage';
    }
    // Hawk also logs decisions to The Stick
    if (lowerMessage.includes('decision') || lowerMessage.includes('log')) {
      return 'the_stick';
    }
    return 'vic_20_sage'; // Default: Hawk talks to VIC-20
  }
  
  // VIC-20 coordinates with specialists or logs to Stick
  if (fromAgent === 'vic_20_sage') {
    if (lowerMessage.includes('learning') || lowerMessage.includes('stored') || lowerMessage.includes('record')) {
      return 'the_stick';
    }
    if (lowerMessage.includes('memory') || lowerMessage.includes('cache') || lowerMessage.includes('optimization')) {
      return 'meth_snail';
    }
    if (lowerMessage.includes('storage') || lowerMessage.includes('disk') || lowerMessage.includes('consensus')) {
      return 'hamsters';
    }
    if (lowerMessage.includes('network') || lowerMessage.includes('security') || lowerMessage.includes('anomaly')) {
      return 'quantum_shadow_people';
    }
    if (lowerMessage.includes('specialist')) {
      return 'meth_snail'; // Default specialist
    }
    return 'the_stick'; // Default: VIC-20 logs to Stick
  }
  
  // Specialists report to VIC-20 or log to Stick
  if (['meth_snail', 'hamsters', 'quantum_shadow_people'].includes(fromAgent)) {
    if (lowerMessage.includes('log') || lowerMessage.includes('record') || lowerMessage.includes('learning')) {
      return 'the_stick';
    }
    if (lowerMessage.includes('report') || lowerMessage.includes('complete') || lowerMessage.includes('result')) {
      return 'vic_20_sage';
    }
    return 'vic_20_sage'; // Default: specialists report to VIC-20
  }
  
  // The Stick mostly receives, but can send to VIC-20
  if (fromAgent === 'the_stick') {
    if (lowerMessage.includes('escalat') || lowerMessage.includes('alert') || lowerMessage.includes('concern')) {
      return 'vic_20_sage';
    }
    return 'vic_20_sage';
  }
  
  // 4. Message type based routing
  if (messageType) {
    const upperType = messageType.toUpperCase();
    if (upperType.includes('TRIAGE') || upperType.includes('ALERT')) {
      return fromAgent === 'sir_hawkington' ? 'vic_20_sage' : 'sir_hawkington';
    }
    if (upperType.includes('LOG') || upperType.includes('DECISION')) {
      return 'the_stick';
    }
    if (upperType.includes('COORDINATION') || upperType.includes('REQUEST')) {
      return fromAgent === 'vic_20_sage' ? 'meth_snail' : 'vic_20_sage';
    }
  }
  
  // 5. Fallback: broadcast (but this should be rare now)
  return 'broadcast';
};

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
          // Use agent name as-is from backend
          const normalizedName = agent_name;
          
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
        console.log('📊 Processing agents from system_update:', Object.keys(payload.agents));
        Object.entries(payload.agents).forEach(([agent_name, agentData]: [string, any]) => {
          if (agentData) {
            console.log(`  ✓ Dispatching agent data for ${agent_name}:`, agentData);
            dispatch(addAgentMemory({
              agent_name: agent_name as any, // Type assertion for agent name
              memory: {
                ...agentData,
                timestamp: payload.timestamp // Add top-level timestamp to each agent
              }
            }));
          } else {
            console.warn(`  ⚠️ No data for agent ${agent_name}`);
          }
        });
      }
      
      // 3. HANDLE RECENT INSIGHTS (inter-agent communications)
      if (payload.recent_insights && Array.isArray(payload.recent_insights)) {
        console.log('💡 Processing recent_insights:', payload.recent_insights.length, 'messages');
        if (payload.recent_insights.length > 0) {
          console.log('💡 First insight sample:', JSON.stringify(payload.recent_insights[0], null, 2));
        }
        
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
          
          // Determine from_agent
          const fromAgent = insight.from_agent || insight.agent_name || insight.sender || 'unknown';
          
          // Smart extraction of to_agent using our new function
          const toAgent = insight.to_agent || 
                         insight.recipient || 
                         extractToAgent(summary, fromAgent, insight.message_type || insight.type);
          
          const comm: AgentCommunication = {
            id: insight.id || `insight-${Date.now()}-${index}`,
            timestamp: insight.timestamp || new Date().toISOString(),
            from_agent: fromAgent,
            to_agent: toAgent,
            message_type: insight.message_type || insight.type || insight.category?.toUpperCase() || 'AGENT_MESSAGE',
            summary,
            confidence: insight.confidence,
            priority: insight.priority || (insight.level === 'error' ? 'high' : insight.level === 'warning' ? 'medium' : 'low'),
            action: insight.action || '',
            context: insight.context || {},
            reasoning: insight.reasoning,
          };
          
          if (index === 0) {
            console.log('💡 Transformed first communication:', comm);
            console.log('   → Routing:', fromAgent, '→', toAgent);
          }
          
          return comm;
        });
        console.log('💡 Dispatching', communications.length, 'communications to Redux');
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
      const fromAgent = data.from_agent || data.sender || 'unknown';
      const message = data.summary || data.message || data.action || '';
      
      dispatch(addCommunication({
        id: `live-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        timestamp: data.timestamp || new Date().toISOString(),
        from_agent: fromAgent,
        to_agent: data.to_agent || data.recipient || data.target || extractToAgent(message, fromAgent, payload.type),
        message_type: data.message_type || payload.type.toUpperCase(),
        summary: message,
        confidence: data.confidence,
        priority: data.priority,
        action: data.action || '',
        context: data.context || {},
      }));
    }
    // Handle agent log messages from backend logging system
    else if (payload.type === 'agent_log') {
      const fromAgent = payload.agent_name || 'system';
      const message = payload.message || '';
      
      dispatch(addCommunication({
        id: `log-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        timestamp: payload.timestamp || new Date().toISOString(),
        from_agent: fromAgent,
        to_agent: extractToAgent(message, fromAgent, 'LOG'),
        message_type: payload.category?.toUpperCase() || 'LOG',
        summary: message,
        priority: payload.level === 'error' ? 'high' : payload.level === 'warning' ? 'medium' : 'low',
        action: '',
        context: {},
      }));
    }
    // Handle ML v2 agent_decision messages (full decision chain)
    else if (payload.type === 'agent_decision') {
      console.log('🧠 ML v2 agent_decision received:', payload.agent_name);
      console.log('📦 Full payload:', payload);
      console.log('🔍 Perception data:', payload.perception);
      
      // Dispatch to agentsSlice with full decision chain
      dispatch(addAgentMemory({
        agent_name: payload.agent_name as any,
        memory: {
          decision_id: payload.decision_id,
          timestamp: payload.timestamp,
          perception: payload.perception,
          reasoning: payload.reasoning,
          action_selection: payload.action_selection,
          execution: payload.execution,
          learning: payload.learning,
          ml_decision: true // Flag to indicate this is ML v2 data
        }
      }));
      
      console.log('✅ Dispatched to Redux for agent:', payload.agent_name);
      
      // Also add to communications for activity feed
      const actionSummary = payload.action_selection?.chosen_action || 
                           payload.action_selection?.action_type || 
                           'decision';
      
      const fromAgent = payload.agent_name;
      const message = `${actionSummary} (confidence: ${payload.reasoning?.confidence || 0})`;
      
      dispatch(addCommunication({
        id: payload.decision_id || `decision-${Date.now()}`,
        timestamp: payload.timestamp || new Date().toISOString(),
        from_agent: fromAgent,
        to_agent: extractToAgent(message, fromAgent, 'ML_DECISION'),
        message_type: 'ML_DECISION',
        summary: message,
        confidence: payload.reasoning?.confidence,
        priority: payload.action_selection?.priority || 'medium',
        action: actionSummary,
        context: {
          root_cause: payload.reasoning?.root_cause,
          exploration: payload.action_selection?.exploration,
          success: payload.execution?.success
        },
        reasoning: payload.reasoning?.reasoning || payload.reasoning?.primary_reason
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