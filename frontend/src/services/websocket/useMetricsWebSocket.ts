// useMetricsWebSocket.ts
import { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { initWebSocket } from './WebSocketService';
import { 
  setConnectionStatus, 
  setError 
} from '../../store/slices/metricsSlice';
import {
  updateCPUMetrics,
  setCPULoading,
  setCPUError
} from '../../store/slices/metrics/CPUSlice';
import {
  updateMemoryMetrics,
  setMemoryLoading,
  setMemoryError
} from '../../store/slices/metrics/MemorySlice';
import {
  updateDiskMetrics,
  setDiskLoading,
  setDiskError
} from '../../store/slices/metrics/DiskSlice';
import {
  updateNetworkMetrics,
  setNetworkLoading,
  setNetworkError
} from '../../store/slices/metrics/NetworkSlice';
import { WebSocketMessage, ConnectionStatus } from './websocket_types';

export const useMetricsWebSocket = () => {
  const dispatch = useDispatch();
  const wsRef = useRef<ReturnType<typeof initWebSocket> | null>(null);
  const [circuitBreakerState, setCircuitBreakerState] = useState<any>(null);
  const isAuthenticated = useSelector((state: RootState) => state.auth?.isAuthenticated);

  useEffect(() => {
    const initializeWebSocket = async () => {
      if (!isAuthenticated) {
        console.log('Not authenticated, skipping WebSocket connection');
        return;
      }

      try {
        console.log('✅ User authenticated, initializing WebSocket...');
        
        // Initialize or get existing WebSocket service
        if (!wsRef.current) {
          wsRef.current = initWebSocket(dispatchEvent); // No dispatch needed anymore!
          
          // Set up event handlers
          if (wsRef.current) {
            // Handle incoming messages
            wsRef.current.onMessage = (message: WebSocketMessage) => {
              try {
                switch (message.type) {
                  case 'cpu_metrics':
                    dispatch(updateCPUMetrics(message.data));
                    dispatch(setCPULoading(false));
                    dispatch(setCPUError(null));
                    break;
                  case 'memory_metrics':
                    dispatch(updateMemoryMetrics(message.data));
                    dispatch(setMemoryLoading(false));
                    dispatch(setMemoryError(null));
                    break;
                  case 'disk_metrics':
                    dispatch(updateDiskMetrics(message.data));
                    dispatch(setDiskLoading(false));
                    dispatch(setDiskError(null));
                    break;
                  case 'network_metrics':
                    dispatch(updateNetworkMetrics(message.data));
                    dispatch(setNetworkLoading(false));
                    dispatch(setNetworkError(null));
                    break;
                }
              } catch (error) {
                console.error('Error processing message:', error);
              }
            };

            // Handle errors
            wsRef.current.onError = (error: Error) => {
              console.error('🚨 WebSocket error:', error);
              const errorMessage = error.message || 'WebSocket connection error';
              
              // Update all error states
              dispatch(setCPUError(errorMessage));
              dispatch(setMemoryError(errorMessage));
              dispatch(setDiskError(errorMessage));
              dispatch(setNetworkError(errorMessage));
              dispatch(setConnectionStatus('error'));
              dispatch(setError(errorMessage));
              
              // Update circuit breaker state
              setCircuitBreakerState(wsRef.current?.getCircuitBreakerState());
            };

            // Handle connection status changes
            wsRef.current.onConnectionStatusChange = (status: ConnectionStatus) => {
              console.log(`🔄 WebSocket status: ${status}`);
              dispatch(setConnectionStatus(status));
              
              // Update loading states based on connection status
              const isLoading = status === 'connecting';
              dispatch(setCPULoading(isLoading));
              dispatch(setMemoryLoading(isLoading));
              dispatch(setDiskLoading(isLoading));
              dispatch(setNetworkLoading(isLoading));
              
              // Clear errors on successful connection
              if (status === 'connected') {
                dispatch(setCPUError(null));
                dispatch(setMemoryError(null));
                dispatch(setDiskError(null));
                dispatch(setNetworkError(null));
                dispatch(setError(null));
              }
              
              // Update circuit breaker state
              setCircuitBreakerState(wsRef.current?.getCircuitBreakerState());
            };
          }
        }
        
        // Set initial loading state
        dispatch(setCPULoading(true));
        dispatch(setMemoryLoading(true));
        dispatch(setDiskLoading(true));
        dispatch(setNetworkLoading(true));
        
        // Connect if not already connected
        if (wsRef.current && !wsRef.current.isConnected()) {
          await wsRef.current.connect();
        }
      } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
        dispatch(setConnectionStatus('error'));
        dispatch(setError(error instanceof Error ? error.message : 'Unknown error'));
      }
    };

    initializeWebSocket();
    
    // Cleanup on unmount or auth change
    return () => {
      if (!isAuthenticated && wsRef.current) {
        wsRef.current.disconnect();
        wsRef.current = null;
      }
    };
  }, [dispatch, isAuthenticated]);

  // Public API
  return {
    reconnect: () => wsRef.current?.connect(),
    disconnect: () => wsRef.current?.disconnect(),
    resetCircuitBreaker: () => {
      if (wsRef.current) {
        wsRef.current.resetCircuitBreaker();
        wsRef.current.connect();
      }
    },
    getCircuitBreakerState: () => circuitBreakerState,
    isConnected: () => wsRef.current?.isConnected() || false,
    requestIntervalChange: (seconds: number) => wsRef.current?.requestIntervalChange(seconds),
    requestSystemInfo: () => wsRef.current?.requestSystemInfo()
  };
};

export default useMetricsWebSocket;