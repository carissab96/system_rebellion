// src/hooks/useMetricsWebsocket.ts
import { useEffect, useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { updateMetrics, setWebSocketError, setConnectionStatus } from '../store/slices/metricsSlice';
import { useToast } from '../components/common/Toast';
import websocketService from '../utils/websocketService';

// Hook to manage WebSocket connection for metrics
export const useMetricsWebSocket = () => {
  const dispatch = useAppDispatch();
  const { useWebSocket } = useAppSelector((state) => state.metrics);
  const toast = useToast();
  
  // Handle incoming WebSocket messages
  const handleMessage = useCallback((message: any) => {
    try {
      if (message && message.type === 'system_metrics' && message.data) {
        dispatch(updateMetrics(message.data));
      }
    } catch (error) {
      console.error('❌ Error processing WebSocket message:', error);
    }
  }, [dispatch]);

  // Initialize WebSocket connection
  useEffect(() => {
    if (!useWebSocket) {
      console.log('🚫 WebSocket connection disabled via useWebSocket flag');
      return;
    }
    
    console.log('🚀 Initializing WebSocket connection');
    dispatch(setConnectionStatus('connecting'));
    
    // Set up event listeners
    const onOpen = () => {
      console.log('✅ WebSocket connected');
      dispatch(setConnectionStatus('connected'));
      dispatch(setWebSocketError(null));
      // Fixed: Combine the messages into one string
      toast.success('Connected: Real-time updates enabled');
    };

    const onClose = () => {
      console.log('👋 WebSocket disconnected');
      dispatch(setConnectionStatus('disconnected'));
    };

    const onError = (event: any) => {
      let errorMessage = 'Unknown WebSocket error';
      
      if (event instanceof Error) {
        errorMessage = event.message;
      } else if (event.type) {
        errorMessage = `WebSocket error: ${event.type}`;
      }
      
      console.error('❌ WebSocket error:', errorMessage);
      dispatch(setWebSocketError(errorMessage));
      dispatch(setConnectionStatus('error'));
      // Fixed: This should be one string message, not two parameters
      toast.error(`Connection Error: ${errorMessage}`);
    };

    // Add event listeners
    websocketService.on('open', onOpen);
    websocketService.on('close', onClose);
    websocketService.on('error', onError);
    websocketService.on('message', handleMessage);
    
    // Connect to WebSocket
    websocketService.connect();

    // Clean up on unmount
    return () => {
      console.log('🧹 Cleaning up WebSocket connection...');
      websocketService.off('open', onOpen);
      websocketService.off('close', onClose);
      websocketService.off('error', onError);
      websocketService.off('message', handleMessage);
      
      // Only disconnect if explicitly told to
      if (!useWebSocket) {
        websocketService.disconnect();
      }
    };
  }, [useWebSocket, dispatch, toast, handleMessage]);

  // Get connection status from Redux store
  const isConnected = useAppSelector(state => state.metrics.connectionStatus === 'connected');
  const connectionError = useAppSelector(state => state.metrics.error);

  return {
    isConnected,
    error: connectionError,
    reconnect: () => websocketService.connect(),
    disconnect: () => websocketService.disconnect()
  };
};

export default useMetricsWebSocket;