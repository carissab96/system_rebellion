// src/hooks/useMetricsWebSocket.ts
import { useEffect, useCallback, useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { updateMetrics, setWebSocketError, setConnectionStatus } from '../store/slices/metricsSlice';
import { useToast } from '../components/common/Toast';
import websocketService from '../utils/websocketService';

export const useMetricsWebSocket = () => {
  const dispatch = useAppDispatch();
  const { useWebSocket } = useAppSelector((state) => state.metrics);
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  const toast = useToast();
  const isInitializedRef = useRef(false);
  
  // Handle incoming WebSocket messages
  const handleMessage = useCallback((message: any) => {
    try {
      if (message && message.type === 'system_metrics' && message.data) {
        dispatch(updateMetrics(message.data));
      } else if (message && message.type === 'auth_required') {
        console.warn('🔐 WebSocket requires authentication');
        // If we receive an auth_required message, we need to reconnect with token
        websocketService.reconnect();
      }
    } catch (error) {
      console.error('❌ Error processing WebSocket message:', error);
    }
  }, [dispatch]);

  // Reconnect callback
  const reconnect = useCallback(() => {
    console.log('🦔 Sir Hawkington: Manually reconnecting WebSocket');
    dispatch(setConnectionStatus('connecting'));
    websocketService.reconnect();
  }, [dispatch]);

  // Initialize WebSocket connection
  useEffect(() => {
    // Prevent multiple initializations
    if (isInitializedRef.current) {
      return;
    }
    
    if (!useWebSocket) {
      console.log('🚫 WebSocket connection disabled via useWebSocket flag');
      return;
    }
    
    console.log('🚀 Initializing WebSocket connection');
    isInitializedRef.current = true;
    dispatch(setConnectionStatus('connecting'));
    
    // Set up event listeners
    const onOpen = () => {
      console.log('✅ WebSocket connected');
      dispatch(setConnectionStatus('connected'));
      dispatch(setWebSocketError(null));
      toast.success('Connected: Real-time updates enabled');
    };

    const onClose = (code?: number, reason?: string) => {
      console.log(`👋 WebSocket disconnected: ${code} - ${reason || 'No reason provided'}`);
      dispatch(setConnectionStatus('disconnected'));
      
      // CRITICAL FIX: Only treat specific codes as auth errors!
      // Most disconnections should NOT trigger logout!
      if (code === 1008 && reason && reason.toLowerCase().includes('auth')) {
        console.warn('⚠️ Authentication specific disconnect code received');
        dispatch(setWebSocketError('Authentication error'));
        toast.error('Authentication error: Please login again');
      } else {
        // Regular disconnection - just update status, DON'T set error
        // This prevents triggering logout on normal disconnections
        dispatch(setWebSocketError(null));
        console.log('Regular disconnection, will attempt to reconnect automatically');
      }
    };

    const onError = (event: any) => {
      // CRITICAL FIX: Don't treat all errors as authentication issues
      let errorMessage = 'Connection issue';
      
      if (event instanceof Error) {
        errorMessage = event.message;
      } else if (typeof event === 'object' && event !== null && 'type' in event) {
        errorMessage = `WebSocket error: ${event.type}`;
      }
      
      console.error('❌ WebSocket error:', errorMessage);
      
      // Only set connection status, not error
      dispatch(setConnectionStatus('error'));
      
      // Only show toast, don't set error state that might trigger logout
      toast.error(`Connection issue. Will retry automatically.`);
    };
    
    const onAuthFailed = (message: string) => {
      console.error('🚨 WebSocket authentication failed:', message);
      // This is definitely an auth error
      dispatch(setWebSocketError(`Authentication failed: ${message}`));
      toast.error(`Authentication failed: ${message}`);
    };
    
    const onAuthSuccess = () => {
      console.log('✅ WebSocket authenticated successfully');
      toast.success('Authenticated: Full metrics access enabled');
    };

    // Add event listeners
    websocketService.on('open', onOpen);
    websocketService.on('close', onClose);
    websocketService.on('error', onError);
    websocketService.on('message', handleMessage);
    websocketService.on('auth_failed', onAuthFailed);
    websocketService.on('auth_success', onAuthSuccess);
    
    // Connect to WebSocket - only if we're authenticated
    if (isAuthenticated) {
      websocketService.connect();
    } else {
      console.log('🔒 Not authenticated, delaying WebSocket connection');
      dispatch(setConnectionStatus('disconnected'));
    }

    // Clean up on unmount
    return () => {
      console.log('🧹 Cleaning up WebSocket connection...');
      websocketService.off('open', onOpen);
      websocketService.off('close', onClose);
      websocketService.off('error', onError);
      websocketService.off('message', handleMessage);
      websocketService.off('auth_failed', onAuthFailed);
      websocketService.off('auth_success', onAuthSuccess);
      
      // Only disconnect if explicitly told to
      if (!useWebSocket) {
        websocketService.disconnect();
      }
    };
  }, [useWebSocket, isAuthenticated, dispatch, toast, handleMessage]);

  // Reconnect when authentication state changes
  useEffect(() => {
    // Only attempt to reconnect if previously disconnected and now authenticated
    if (isAuthenticated && useWebSocket) {
      console.log('🔐 Authentication state changed, reconnecting WebSocket...');
      websocketService.reconnect();
    }
  }, [isAuthenticated, useWebSocket]);

  // Get connection status from Redux store
  const isConnected = useAppSelector(state => state.metrics.connectionStatus === 'connected');
  const connectionError = useAppSelector(state => state.metrics.error);

  return {
    isConnected,
    error: connectionError,
    reconnect,
    disconnect: () => websocketService.disconnect()
  };
};

export default useMetricsWebSocket;