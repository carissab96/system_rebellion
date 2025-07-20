// hooks/useAgentTheater.ts
import { useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import  type { RootState, AppDispatch } from '../store/store';
import { 
  updateWebSocketMessage, 
  setConnectionStatus, 
  setError,
  updateActiveAgentCount,
} from '../store/slices/agentTheaterSlice';
import { updateMetrics as updateSirHawkington, setOffline as setSirHawkingtonOffline } from '../store/slices/sirHawkingtonSlice';
import { updateMetrics as updateMethSnail, setOffline as setMethSnailOffline } from '../store/slices/methSnailSlice';
import { updateMetrics as updateHamsters, setOffline as setHamstersOffline } from '../store/slices/hamstersSlice';
import { updateMetrics as updateQuantumShadow, setOffline as setQuantumShadowOffline } from '../store/slices/quantumShadowPeopleSlice';
import { updateMetrics as updateTheStick, setOffline as setTheStickOffline } from '../store/slices/theStickSlice';
import { updateMetrics as updateVIC20, setOffline as setVIC20Offline } from '../store/slices/vic20Slice';

export const useAgentTheater = () => {
  const { token, isAuthenticated } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch<AppDispatch>();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const connectionAttempts = useRef(0);

  // Get state from all slices
  const agentTheater = useSelector((state: RootState) => state.agentTheater);
  const sirHawkington = useSelector((state: RootState) => state.sirHawkington);
  const methSnail = useSelector((state: RootState) => state.methSnail);
  const hamsters = useSelector((state: RootState) => state.hamsters);
  const quantumShadow = useSelector((state: RootState) => state.quantumShadow);
  const theStick = useSelector((state: RootState) => state.theStick);
  const vic20 = useSelector((state: RootState) => state.vic20);

  useEffect(() => {
    console.log('useAgentTheater Auth Check:', {
      hasToken: !! token,
      isAuthenticated,
      tokenPreview: token ? `${token.substring(0, 10)}...` : 'null',
      tokenLength: token ?. length
    });

    const connectWebSocket = () => {
      if (!token || !isAuthenticated) {
        console.log('No authentication - cannot connect to WebSocket');
        dispatch(setError('authentication required for websocket connection'));
        dispatch(setConnectionStatus('disconnected'));
        return;
      }

      connectionAttempts.current += 1;
      console.log(`websocket connection attempt ${connectionAttempts.current}`);

      //create websocket url with token in query params (as backend expects)
      const wsUrl = `ws://localhost:8000/ws/system-metrics?token=${encodeURIComponent(token)}`;
      console.log('connecting to:', wsUrl.replace(token, `${token.substring(0, 10)}...`));
      
      const ws = new WebSocket(wsUrl.toString());
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connect successfully');
        connectionAttempts.current = 0; //reset on successful connection
        dispatch(setConnectionStatus('connected'));
        dispatch(setError(null));
      };

      ws.onmessage = (event) => {
        console.log('WebSocket message received:', event.data);
        console.log('event type:', event.type);
        console.log('event target:', event.target);
        console.log('event current target:', event.currentTarget);
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'error') {
            console.error('Backend error:', message.message);
            dispatch(setError(`Backend error: ${message.message}`));
            return; 
          }
          // Route to main theater slice
          dispatch(updateWebSocketMessage(message));
          
          // Route to individual agent slices based on real data
          if (message.type === 'metrics_update' && message.data) {
            const data = message.data;
            console.log('Processing metrics update:', Object.keys(data));
            console.log('data:', data);
            
            // Update each agent slice with their specific data - NO FAKE DATA
            if (data.sir_hawkington) {
              dispatch(updateSirHawkington(data.sir_hawkington));
            } else {
              dispatch(setSirHawkingtonOffline('No Sir Hawkington data in WebSocket message'));
            }
            
            if (data.meth_snail) {
              dispatch(updateMethSnail(data.meth_snail));
            } else {
              dispatch(setMethSnailOffline('No Meth Snail data in WebSocket message'));
            }
            
            if (data.hamsters) {
              dispatch(updateHamsters(data.hamsters));
            } else {
              dispatch(setHamstersOffline('No Hamsters data in WebSocket message'));
            }
            
            if (data.quantum_shadow) {
              dispatch(updateQuantumShadow(data.quantum_shadow));
            } else {
              dispatch(setQuantumShadowOffline('No Quantum Shadow data in WebSocket message'));
            }
            
            if (data.the_stick) {
              dispatch(updateTheStick(data.the_stick));
            } else {
              dispatch(setTheStickOffline('No Stick data in WebSocket message'));
            }
            
            if (data.vic20_sage) {
              dispatch(updateVIC20(data.vic20_sage));
            } else {
              dispatch(setVIC20Offline('No VIC-20 data in WebSocket message'));
            }
            
            // Update active agent count
            const activeCount = [
              data.sir_hawkington,
              data.meth_snail,
              data.hamsters,
              data.quantum_shadow,
              data.the_stick,
              data.vic20_sage
            ].filter(Boolean).length;
            
            dispatch(updateActiveAgentCount(activeCount));
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
          dispatch(setError(`Failed to parse WebSocket message: ${err}`));
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        dispatch(setError(`WebSocket error: ${error}`));
        dispatch(setConnectionStatus('disconnected'));
      };

      ws.onclose = (closeEvent: CloseEvent) => {
        console.log('🔌 WebSocket closed:', {
          code: closeEvent.code,
          reason: closeEvent.reason,
          wasClean: closeEvent.wasClean
        });

        dispatch(setConnectionStatus('disconnected'));

        // Handle specific close codes from your backend
        if (closeEvent.code === 1008) { // WS_1008_POLICY_VIOLATION
          console.error('🚫 Authentication failed - not reconnecting');
          dispatch(setError('Authentication failed - please log in again'));
          return;
        }
        // Only auto-reconnect if we have valid auth and haven't tried too many times
        if (token && isAuthenticated && connectionAttempts.current < 5) {
          const delay = Math.min(1000 * Math.pow(2, connectionAttempts.current), 30000);
          console.log(`⏰ Reconnecting in ${delay}ms... (attempt ${connectionAttempts.current + 1})`);
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, delay);
        } else {
          console.log('❌ Max reconnection attempts reached or no auth');
          dispatch(setError('Connection failed - please refresh page'));
        }
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [dispatch, token, isAuthenticated]);


  const sendMessage = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return {
    // Main theater state
    connectionStatus: agentTheater.connectionStatus,
    error: agentTheater.error,
    lastUpdate: agentTheater.lastUpdate,
    activeAgentCount: agentTheater.activeAgentCount,
    systemInfo: agentTheater.systemInfo,
    
    // Individual agent states
    agents: {
      sirHawkington,
      methSnail,
      hamsters,
      quantumShadow,
      theStick,
      vic20,
    },
    //Raw metrics data for MissingAgentsIndicator
    metricsData: {
      sir_hawkington: sirHawkington.isOnline ? sirHawkington.data : null,
      meth_snail: methSnail.isOnline ? methSnail.data : null,
      hamsters: hamsters.isOnline ? hamsters.data : null,
      quantum_shadow: quantumShadow.isOnline ? quantumShadow.data : null,
      the_stick: theStick.isOnline ? theStick.data : null,
      vic20_sage: vic20.isOnline ? vic20.data : null
    },
    // WebSocket helpers
    sendMessage,
    requestSystemInfo: () => sendMessage({ type: 'request_system_info' }),
    resetCircuitBreaker: () => sendMessage({ type: 'reset_circuit_breaker' }),
    setUpdateInterval: (interval: number) => sendMessage({ type: 'set_interval', data: { interval } }),
  };
};