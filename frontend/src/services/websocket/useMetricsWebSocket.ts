import { useEffect, useRef, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { WebSocketService, CPUMetricsMessage, CircuitBreakerState } from './WebSocketService1';
import { RootState } from '../../store/store';
import { updateMetrics as updateCPUMetrics, setError as setCPUError, setLoading as setCPULoading } from '../../store/slices/metrics/CPUSlice';
import { setConnectionStatus, setWebSocketError } from '../../store/slices/metricsSlice';

export const useMetricsWebSocket = () => {
  const dispatch = useAppDispatch();
  const { isAuthenticated } = useAppSelector((state: RootState) => state.auth);
  const wsRef = useRef<WebSocketService | null>(null);
  const [circuitBreakerState, setCircuitBreakerState] = useState<CircuitBreakerState | null>(null);
  
  // Track connection attempts for fallback strategies
  const connectionAttemptsRef = useRef<number>(0);
  const maxConnectionAttempts = 3;

  useEffect(() => {
    if (isAuthenticated && !wsRef.current) {
      console.log('🦔 Creating WebSocket service with resilience strategies');
      wsRef.current = new WebSocketService(dispatch);

      // Handle WebSocket messages
      wsRef.current.onMessage = (message: CPUMetricsMessage) => {
        console.log('🦔 Received message in hook:', message.type);
        
        // Check if message and message.data exist before processing
        if (!message || !message.data) {
          console.error('🚨 Invalid WebSocket message format:', message);
          return;
        }
        
        // Only process CPU messages
        if (message.type !== 'cpu') {
          console.log('🦔 Ignoring non-CPU message:', message.type);
          return;
        }
        
        // Reset connection attempts on successful message
        connectionAttemptsRef.current = 0;
        
        console.log('🦔 Processing CPU metrics:', message.data.usage_percent);
        dispatch(updateCPUMetrics({
          usage_percent: message.data.usage_percent,
          temperature: message.data.temperature,
          cores: Array.isArray(message.data.cores) ? message.data.cores.map((usage, index) => ({
            id: index,
            usage: usage
          })) : [],
          physical_cores: message.data.physical_cores,
          logical_cores: message.data.logical_cores,
          frequency_mhz: message.data.frequency_mhz,
          top_processes: Array.isArray(message.data.top_processes) ? message.data.top_processes : []
        }));
      };

      // Handle WebSocket errors with resilience
      wsRef.current.onError = (error: Error) => {
        console.error('🚨 WebSocket error:', error);
        dispatch(setCPUError(error.message));
        dispatch(setWebSocketError(error.message));
        
        // Update circuit breaker state
        if (wsRef.current) {
          setCircuitBreakerState(wsRef.current.getCircuitBreakerState());
        }
        
        // Track connection attempts for fallback strategies
        connectionAttemptsRef.current++;
        if (connectionAttemptsRef.current >= maxConnectionAttempts) {
          console.log('⚠️ Maximum WebSocket connection attempts reached, switching to polling fallback');
          dispatch(setConnectionStatus('fallback'));
        }
      };
      
      // Handle connection status changes
      wsRef.current.onConnectionStatusChange = (status) => {
        console.log(`🔄 WebSocket connection status changed to: ${status}`);
        
        // Map WebSocket status to Redux connection status
        switch (status) {
          case 'connecting':
            dispatch(setConnectionStatus('connecting'));
            dispatch(setCPULoading(true));
            break;
          case 'connected':
            dispatch(setConnectionStatus('connected'));
            dispatch(setCPULoading(false));
            dispatch(setWebSocketError(null));
            break;
          case 'disconnected':
            dispatch(setConnectionStatus('disconnected'));
            break;
          case 'error':
            dispatch(setConnectionStatus('error'));
            break;
          case 'circuit-open':
            dispatch(setConnectionStatus('error'));
            dispatch(setWebSocketError('Circuit breaker is open due to multiple connection failures'));
            break;
        }
        
        // Update circuit breaker state
        if (wsRef.current) {
          setCircuitBreakerState(wsRef.current.getCircuitBreakerState());
        }
      };

      // Start with loading state
      dispatch(setCPULoading(true));
      wsRef.current.connect();
    }

    // Cleanup function
    return () => {
      if (wsRef.current) {
        console.log('🦔 Disconnecting WebSocket service');
        wsRef.current.disconnect();
        wsRef.current = null;
      }
    };
  }, [dispatch, isAuthenticated]);
  
  // Effect to monitor circuit breaker state changes
  useEffect(() => {
    if (circuitBreakerState && circuitBreakerState.status === 'open') {
      const waitTime = Math.ceil((circuitBreakerState.nextAttemptTime - Date.now()) / 1000);
      console.log(`⚠️ Circuit breaker is open, will retry in ${waitTime}s`);
      
      // If circuit breaker is open, switch to fallback mode
      dispatch(setConnectionStatus('fallback'));
    }
  }, [circuitBreakerState, dispatch]);

  return {
    reconnect: () => {
      console.log('🦔 Manually reconnecting WebSocket');
      if (wsRef.current) {
        wsRef.current.connect();
      }
    },
    disconnect: () => {
      console.log('🦔 Manually disconnecting WebSocket');
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    },
    resetCircuitBreaker: () => {
      console.log('🔄 Manually resetting WebSocket circuit breaker');
      if (wsRef.current) {
        wsRef.current.resetCircuitBreaker();
        wsRef.current.connect();
      }
    },
    getCircuitBreakerState: () => circuitBreakerState
  };
};

export default useMetricsWebSocket;