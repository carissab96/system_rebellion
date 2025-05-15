import { useEffect, useCallback, useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { updateMetrics, setWebSocketError, setConnectionStatus } from '../store/slices/metricsSlice';
import { useToast } from '../components/common/Toast';
import webSocketService from '../utils/websocketService';

type WebSocketMessage = {
  type: string;
  data?: any;
  error?: string;
  timestamp?: number;
};

// Hook to manage WebSocket connection for metrics
export const useMetricsWebSocket = () => {
  const dispatch = useAppDispatch();
  const { useWebSocket, error } = useAppSelector((state) => state.metrics);
  const toast = useToast();
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  // Store the timeout ID for reconnection attempts (compatible with both browser and Node.js)
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((message: WebSocketMessage | string) => {
    try {
      // If message is a string, parse it as JSON
      const parsedMessage = typeof message === 'string' ? JSON.parse(message) : message;
      if (parsedMessage && parsedMessage.type === 'system_metrics' && parsedMessage.data) {
        dispatch(updateMetrics(parsedMessage.data));
      }
    } catch (error) {
      console.error('Error processing WebSocket message:', error);
    }
  }, [dispatch]);

  // Handle reconnection logic
  const attemptReconnect = useCallback(() => {
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      toast.error('Connection Error: Failed to connect to real-time updates after multiple attempts');
      return;
    }

    reconnectAttempts.current += 1;
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current}/${maxReconnectAttempts})...`);
    
    // Clear any existing timeout to prevent memory leaks
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }
    
    // Set a new timeout
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.host;
    const wsUrl = `${wsProtocol}//${wsHost}/ws/system-metrics`;
    
    const timeoutId = setTimeout(() => {
      console.log('Reconnecting...');
      webSocketService.connect(wsUrl);
    }, delay);
    reconnectTimeout.current = timeoutId;
  }, [toast]);

  // Helper function to get WebSocket URL
  const getWebSocketUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/ws/system-metrics/`;  // Note the trailing slash
  }, []);

  // Initialize WebSocket connection
  useEffect(() => {
    if (!useWebSocket) {
      console.log('🚫 WebSocket connection disabled via useWebSocket flag');
      return;
    }
    
    const wsUrl = getWebSocketUrl();
    console.log('🚀 Initializing WebSocket connection to:', wsUrl);
    dispatch(setConnectionStatus('connecting'));
    
    // Log connection details
    console.log('🌐 WebSocket connection details:', {
      url: wsUrl,
      protocol: window.location.protocol,
      host: window.location.host,
      environment: import.meta.env.MODE,
      isSecure: window.location.protocol === 'https:'
    });

    // Set up event listeners
    const onOpen = () => {
      console.log('✅ WebSocket connected');
      reconnectAttempts.current = 0;
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      dispatch(setConnectionStatus('connected'));
      dispatch(setWebSocketError(null));
      toast.success('Connected', 'Real-time updates enabled');
    };

    const onClose = () => {
      console.log('WebSocket disconnected');
      dispatch(setConnectionStatus('disconnected'));

      // Only attempt to reconnect if we're still supposed to be connected
      if (useWebSocket) {
        attemptReconnect();
      }
    };

    const onError = (event: Event) => {
      let errorMessage = 'Unknown WebSocket error';

      if (event instanceof ErrorEvent) {
        errorMessage = event.message || 'WebSocket error occurred';
      } else if (event instanceof CloseEvent) {
        errorMessage = `WebSocket closed: ${event.code} ${event.reason || 'No reason provided'}`;
      } else if (event.type) {
        errorMessage = `WebSocket error: ${event.type}`;
      }

      
      console.error('WebSocket error:', errorMessage, event);
      dispatch(setWebSocketError(errorMessage));
      dispatch(setConnectionStatus('error'));
      toast.error(`Connection Error: ${errorMessage}`);
    };

    // Connect to WebSocket with the configured URL
    webSocketService.connect(wsUrl);
    
    // Log WebSocket service state for debugging
    console.log('🔌 WebSocket service state after connect:', {
      url: (webSocketService as any).url,
      isConnecting: (webSocketService as any).isConnecting,
      connectionStatus: (webSocketService as any).connectionStatus
    });
    
    // Add event listeners
    webSocketService.on('open', onOpen);
    webSocketService.on('close', onClose);
    webSocketService.on('error', onError);
    webSocketService.on('message', handleMessage);

    // Clean up on unmount or when dependencies change
    return () => {
      console.log('🧹 Cleaning up WebSocket connection...');
      webSocketService.off('open', onOpen);
      webSocketService.off('close', onClose);
      webSocketService.off('error', onError);
      webSocketService.off('message', handleMessage);
      
      // Clear any pending reconnect timeout
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
      
      // Only disconnect if explicitly told to
      if (!useWebSocket) {
        webSocketService.disconnect();
      }
    };
  }, [useWebSocket, dispatch, toast, handleMessage, attemptReconnect]);

  // Get connection status from Redux store
  const isConnected = useAppSelector(state => state.metrics.connectionStatus === 'connected');
  const connectionError = useAppSelector(state => state.metrics.error);

  return {
    isConnected,
    error: connectionError || error,
    reconnect: () => {
      reconnectAttempts.current = 0;
      webSocketService.connect();
    },
    disconnect: webSocketService.disconnect
  };
};

export default useMetricsWebSocket;
