// hooks/useAgentTheater.ts
import { useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import  type { RootState } from '../store';
import { 
  updateWebSocketMessage, 
  setConnectionStatus, 
  setError,
  updateActiveAgentCount 
} from '../store/slices/agentTheaterSlice';
import { updateMetrics as updateSirHawkington, setOffline as setSirHawkingtonOffline } from '../store/slices/sirHawkingtonSlice';
import { updateMetrics as updateMethSnail, setOffline as setMethSnailOffline } from '../store/slices/methSnailSlice';
import { updateMetrics as updateHamsters, setOffline as setHamstersOffline } from '../store/slices/hamstersSlice';
import { updateMetrics as updateQuantumShadow, setOffline as setQuantumShadowOffline } from '../store/slices/quantumShadowPeopleSlice';
import { updateMetrics as updateTheStick, setOffline as setTheStickOffline } from '../store/slices/theStickSlice';
import { updateMetrics as updateVIC20, setOffline as setVIC20Offline } from '../store/slices/vic20Slice';

export const useAgentTheater = () => {
  const dispatch = useDispatch();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Get state from all slices
  const agentTheater = useSelector((state: RootState) => state.agentTheater);
  const sirHawkington = useSelector((state: RootState) => state.sirHawkington);
  const methSnail = useSelector((state: RootState) => state.methSnail);
  const hamsters = useSelector((state: RootState) => state.hamsters);
  const quantumShadow = useSelector((state: RootState) => state.quantumShadow);
  const theStick = useSelector((state: RootState) => state.theStick);
  const vic20 = useSelector((state: RootState) => state.vic20);

  useEffect(() => {
    const connectWebSocket = () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        dispatch(setError('No authentication token found'));
        dispatch(setConnectionStatus('disconnected'));
        return;
      }

      const ws = new WebSocket('ws://localhost:8000/ws/system-metrics');
      wsRef.current = ws;

      ws.onopen = () => {
        dispatch(setConnectionStatus('connected'));
        dispatch(setError(null));
        
        // Send authentication
        ws.send(JSON.stringify({ token }));
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          // Route to main theater slice
          dispatch(updateWebSocketMessage(message));
          
          // Route to individual agent slices based on real data
          if (message.type === 'metrics_update' && message.data) {
            const data = message.data;
            
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
          dispatch(setError(`Failed to parse WebSocket message: ${err}`));
        }
      };

      ws.onerror = (error) => {
        dispatch(setError(`WebSocket error: ${error}`));
        dispatch(setConnectionStatus('disconnected'));
      };

      ws.onclose = () => {
        dispatch(setConnectionStatus('disconnected'));
        // Auto-reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 5000);
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
  }, [dispatch]);

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