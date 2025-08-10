import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useDispatch } from 'react-redux';

import { getSystemMetricsWebSocket } from '../services/websocket';
import { 
  updateWebSocketMessage, 
  setConnectionStatus,
  updateActiveAgentCount
} from '../store/slices/agentTheaterSlice';
import { 
 updateMetrics as updateSirHawkington,
 setOffline as setSirHawkingtonOffline
} from '../store/slices/sirHawkingtonSlice';
import { 
 updateMetrics as updateMethSnail,
 setOffline as setMethSnailOffline 
} from '../store/slices/methSnailSlice';
import { 
 updateMetrics as updateHamsters, 
 setOffline as setHamstersOffline 
} from '../store/slices/hamstersSlice';
import { 
 updateMetrics as updateQuantumShadow, 
 setOffline as setQuantumShadowOffline 
} from '../store/slices/quantumShadowPeopleSlice';
import { 
 updateMetrics as updateTheStick, 
 setOffline as setTheStickOffline 
} from '../store/slices/theStickSlice';
import { 
 updateMetrics as updateVIC20, 
 setOffline as setVIC20Offline 
} from '../store/slices/vic20Slice';
import type { RootState } from '../store/store';

export const useAgentTheater = () => {
  const dispatch = useDispatch();
  const { token, isAuthenticated } = useSelector((state: RootState) => state.auth);

  // Get state from all slices
  const agentTheater = useSelector((state: RootState) => state.agentTheater);
  const sirHawkington = useSelector((state: RootState) => state.sirHawkington);
  const methSnail = useSelector((state: RootState) => state.methSnail);
  const hamsters = useSelector((state: RootState) => state.hamsters);
  const quantumShadow = useSelector((state: RootState) => state.quantumShadow);
  const theStick = useSelector((state: RootState) => state.theStick);
  const vic20 = useSelector((state: RootState) => state.vic20);

  useEffect(() => {
    console.log('[useAgentTheater] Starting WebSocket connection...');
    console.log('[useAgentTheater] Auth State:', {
      hasToken: !!token,
      isAuthenticated,
      tokenLength: token?.length
    });

    if (!token || !isAuthenticated) {
      console.log('[useAgentTheater] No authentication - aborting WebSocket connection');
      dispatch(setConnectionStatus('disconnected'));
      return;
    }

    // Use the existing WebSocket singleton
    console.log('[useAgentTheater] Getting WebSocket singleton...');
    const ws = getSystemMetricsWebSocket();
    
    console.log('[useAgentTheater] WebSocket singleton obtained, connected:', ws.connected);
    dispatch(setConnectionStatus(ws.connected ? 'connected' : 'connecting'));

    // Subscribe to WebSocket messages - OPTIMIZED FOR PERFORMANCE
    const handleMessage = (data: any) => {
      // Minimal logging to reduce blocking time
      if (import.meta.env.DEV) {
        console.log('[useAgentTheater] Message:', data.type);
      }

      // Handle metrics_update messages with batched dispatches
      if (data.type === 'metrics_update' && data.data) {
        // Fast data transformation without heavy logging
        const rawData = data.data;
        const transformedData = {
          sir_hawkington: rawData.sir_hawkington || null,
          meth_snail: rawData.meth_snail || null,
          hamsters: rawData.hamsters || null,
          quantum_shadow_people: rawData.quantum_shadow_people || null,
          the_stick: rawData.the_stick || null,
          vic20_sage: rawData.vic_20_sage || rawData.vic20_sage || null,
        };

        // Batch all dispatches to reduce re-renders
        requestAnimationFrame(() => {

        // Dispatch to individual agent slices
        if (transformedData.sir_hawkington) {
          console.log('[useAgentTheater] ✅ Dispatching Sir Hawkington data');
          dispatch(updateSirHawkington(transformedData.sir_hawkington));
        } else {
          console.log('[useAgentTheater] ❌ No Sir Hawkington data');
          dispatch(setSirHawkingtonOffline('No Sir Hawkington data'));
        }

        if (transformedData.meth_snail) {
          console.log('[useAgentTheater] ✅ Dispatching Meth Snail data');
          dispatch(updateMethSnail(transformedData.meth_snail));
        } else {
          console.log('[useAgentTheater] ❌ No Meth Snail data');
          dispatch(setMethSnailOffline('No Meth Snail data'));
        }

        if (transformedData.hamsters) {
          console.log('[useAgentTheater] ✅ Dispatching Hamsters data');
          dispatch(updateHamsters(transformedData.hamsters));
        } else {
          console.log('[useAgentTheater] ❌ No Hamsters data');
          dispatch(setHamstersOffline('No Hamsters data'));
        }

        if (transformedData.quantum_shadow_people) {
          console.log('[useAgentTheater] ✅ Dispatching Quantum Shadow People data');
          dispatch(updateQuantumShadow(transformedData.quantum_shadow_people));
        } else {
          console.log('[useAgentTheater] ❌ No Quantum Shadow People data');
          dispatch(setQuantumShadowOffline('No Quantum Shadow People data'));
        }

        if (transformedData.the_stick) {
          console.log('[useAgentTheater] ✅ Dispatching The Stick data');
          dispatch(updateTheStick(transformedData.the_stick));
        } else {
          console.log('[useAgentTheater] ❌ No The Stick data');
          dispatch(setTheStickOffline('No The Stick data'));
        }

        if (transformedData.vic20_sage) {
          console.log('[useAgentTheater] ✅ Dispatching VIC-20 Sage data');
          dispatch(updateVIC20(transformedData.vic20_sage));
        } else {
          console.log('[useAgentTheater] ❌ No VIC-20 Sage data');
          dispatch(setVIC20Offline('No VIC-20 Sage data'));
        }

        // Update active agent count
        const activeCount = Object.values(transformedData).filter(Boolean).length;
        console.log('[useAgentTheater] Active agent count:', activeCount);
        dispatch(updateActiveAgentCount(activeCount));
        
        // Route to main theater slice
        dispatch(updateWebSocketMessage(data));
        }); // Close requestAnimationFrame callback
      } else {
        console.log('[useAgentTheater] Unhandled message type:', data.type);
      }
    };

    console.log('[useAgentTheater] Subscribing to WebSocket messages...');
    const unsubscribe = ws.subscribe(handleMessage);

    // Update connection status based on WebSocket state
    if (ws.connected) {
      console.log('[useAgentTheater] WebSocket already connected');
      dispatch(setConnectionStatus('connected'));
    }

    // Cleanup function
    return () => {
      console.log('[useAgentTheater] Cleaning up WebSocket subscription...');
      unsubscribe();
    };
  }, [token, isAuthenticated]);

  // WebSocket helper functions using the singleton
  const sendMessage = (message: any) => {
    const ws = getSystemMetricsWebSocket();
    if (ws.connected) {
      ws.send(message);
    } else {
      console.log('[useAgentTheater] Cannot send message - WebSocket not connected');
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
    
    // Raw metrics data for MissingAgentsIndicator
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
