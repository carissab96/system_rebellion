import { useEffect, useRef, useState, useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { WebSocketService, CircuitBreakerState } from './WebSocketService';
import type { 
  CPUMetricsMessage, 
  MemoryMetricsMessage, 
  DiskMetricsMessage, 
  NetworkMetricsMessage 
} from './WebSocketService';
import { RootState } from '../../store/store';
import { 
  updateMetrics as updateCPUMetrics, 
  setError as setCPUError, 
  setLoading as setCPULoading 
} from '../../store/slices/metrics/CPUSlice';
import { 
  updateMetrics as updateMemoryMetrics, 
  setError as setMemoryError, 
  setLoading as setMemoryLoading 
} from '../../store/slices/metrics/MemorySlice';
import { 
  updateMetrics as updateDiskMetrics, 
  setError as setDiskError, 
  setLoading as setDiskLoading 
} from '../../store/slices/metrics/DiskSlice';
import { 
  updateMetrics as updateNetworkMetrics, 
  setError as setNetworkError, 
  setLoading as setNetworkLoading 
} from '../../store/slices/metrics/NetworkSlice';
import { setConnectionStatus } from '../../store/slices/metricsSlice';
import { useToast } from '../../components/common/Toast';

// Helper function to safely parse JSON with error handling
const safeJsonParse = <T>(data: string): T | null => {
  try {
    return JSON.parse(data) as T;
  } catch (error) {
    console.error('Failed to parse message data:', error);
    return null;
  }
};

export const useMetricsWebSocket = () => {
  const dispatch = useAppDispatch();
  const { isAuthenticated } = useAppSelector((state: RootState) => state.auth);
  const wsRef = useRef<WebSocketService | null>(null);
  const [circuitBreakerState, setCircuitBreakerState] = useState<CircuitBreakerState | null>(null);
  
  // Track connection attempts for fallback strategies
  const connectionAttemptsRef = useRef<number>(0);
  const maxConnectionAttempts = 3;

  // Reset all loading states
  const resetLoadingStates = useCallback(() => {
    dispatch(setCPULoading(false));
    dispatch(setMemoryLoading(false));
    dispatch(setDiskLoading(false));
    dispatch(setNetworkLoading(false));
  }, [dispatch]);

  // Reset all error states
  const resetErrorStates = useCallback(() => {
    dispatch(setCPUError(null));
    dispatch(setMemoryError(null));
    dispatch(setDiskError(null));
    dispatch(setNetworkError(null));
  }, [dispatch]);

  // Handle WebSocket messages
  const handleMessage = useCallback((message: string) => {
    try {
      const parsed = safeJsonParse<CPUMetricsMessage | MemoryMetricsMessage | DiskMetricsMessage | NetworkMetricsMessage>(message);
      if (!parsed) return;

      // Reset connection attempts on successful message
      connectionAttemptsRef.current = 0;

      switch (parsed.type) {
        case 'cpu_metrics':
          dispatch(updateCPUMetrics(parsed.data));
          break;
          
        case 'memory_metrics':
          dispatch(updateMemoryMetrics({
            usage_percent: parsed.data.usage_percent,
            total: parsed.data.total,
            available: parsed.data.available,
            used: parsed.data.used,
            free: parsed.data.free,
            swap_total: parsed.data.swap_total,
            swap_used: parsed.data.swap_used,
            swap_free: parsed.data.swap_free,
            swap_usage_percent: parsed.data.swap_usage_percent
          }));
          break;
          
        case 'disk_metrics':
          dispatch(updateDiskMetrics({
            usage_percent: parsed.data.usage_percent,
            total: parsed.data.total,
            used: parsed.data.used,
            free: parsed.data.free,
            read_bytes: parsed.data.read_bytes,
            write_bytes: parsed.data.write_bytes,
            read_count: parsed.data.read_count,
            write_count: parsed.data.write_count,
            read_time: parsed.data.read_time,
            write_time: parsed.data.write_time
          }));
          break;
          
        case 'network_metrics':
          dispatch(updateNetworkMetrics({
            usage_percent: parsed.data.usage_percent,
            bytes_sent: parsed.data.bytes_sent,
            bytes_recv: parsed.data.bytes_recv,
            packets_sent: parsed.data.packets_sent,
            packets_recv: parsed.data.packets_recv,
            err_in: parsed.data.err_in,
            err_out: parsed.data.err_out,
            drop_in: parsed.data.drop_in,
            drop_out: parsed.data.drop_out
          }));
          break;
          
        default:
          console.warn('Unhandled message type:', parsed.type);
      }
    } catch (error) {
      console.error('Error processing message:', error);
    }
  }, [dispatch]);

  // Handle WebSocket errors
  const handleError = useCallback((error: Error) => {
    console.error('🚨 WebSocket error:', error);
    
    // Set error states for all metrics
    dispatch(setCPUError(error.message));
    dispatch(setMemoryError(error.message));
    dispatch(setDiskError(error.message));
    dispatch(setNetworkError(error.message));
    
    dispatch(setConnectionStatus('error'));
    
    // Update circuit breaker state
    if (wsRef.current) {
      setCircuitBreakerState(wsRef.current.getCircuitBreakerState());
    }
    
    // Track connection attempts for fallback strategies
    connectionAttemptsRef.current++;
    if (connectionAttemptsRef.current >= maxConnectionAttempts) {
      const errorMsg = 'Maximum WebSocket connection attempts reached, switching to polling fallback';
      console.log(`⚠️ ${errorMsg}`);
      useToast(errorMsg, 'error');
      dispatch(setConnectionStatus('error'));
    }
  }, [dispatch]);

  // Handle connection status changes
  const handleStatusChange = useCallback((status: string) => {
    console.log(`🔄 WebSocket connection status changed to: ${status}`);
    
    switch (status) {
      case 'connecting':
        dispatch(setConnectionStatus('connecting'));
        // Set loading states for all metrics
        dispatch(setCPULoading(true));
        dispatch(setMemoryLoading(true));
        dispatch(setDiskLoading(true));
        dispatch(setNetworkLoading(true));
        break;
        
      case 'connected':
        dispatch(setConnectionStatus('connected'));
        resetLoadingStates();
        resetErrorStates();
        useToast('Connected to real-time metrics', 'success');
        break;
        
      case 'disconnected':
        dispatch(setConnectionStatus('disconnected'));
        useToast('Disconnected from real-time metrics', 'warning');
        break;
        
      case 'error':
        dispatch(setConnectionStatus('error'));
        useToast('Error connecting to real-time metrics', 'error');
        break;
        
      case 'circuit-open':
        dispatch(setConnectionStatus('error'));
        useToast('Connection temporarily suspended due to errors', 'error');
        break;
    }
    
    // Update circuit breaker state
    if (wsRef.current) {
      setCircuitBreakerState(wsRef.current.getCircuitBreakerState());
    }
  }, [dispatch, resetLoadingStates, resetErrorStates]);

  // Initialize WebSocket connection
  useEffect(() => {
    if (isAuthenticated && !wsRef.current) {
      console.log('🦔 Creating WebSocket service with resilience strategies');
      wsRef.current = new WebSocketService(dispatch);

      // Set up event handlers
      wsRef.current.onMessage = handleMessage;
      wsRef.current.onError = handleError;
      wsRef.current.onConnectionStatusChange = handleStatusChange;

      // Start with loading state
      dispatch(setCPULoading(true));
      dispatch(setMemoryLoading(true));
      dispatch(setDiskLoading(true));
      dispatch(setNetworkLoading(true));
      
      // Connect to WebSocket
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
  }, [dispatch, isAuthenticated, handleMessage, handleError, handleStatusChange]);
  
  // Effect to monitor circuit breaker state changes
  useEffect(() => {
    if (circuitBreakerState?.status === 'open') {
      const waitTime = Math.ceil((circuitBreakerState.nextAttemptTime - Date.now()) / 1000);
      const message = `Connection temporarily suspended. Retrying in ${waitTime} seconds...`;
      console.log(`⚠️ ${message}`);
      useToast(message, 'warning');
    }
  }, [circuitBreakerState]);

  // Public API
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
    getCircuitBreakerState: () => circuitBreakerState,
    isConnected: circuitBreakerState?.status === 'closed'
  };
};

export default useMetricsWebSocket;