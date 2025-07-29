import { useEffect, useRef, useCallback } from 'react';
import { WebSocketService } from '@/services/websocket';

type WebSocketCallback = (data: any) => void;

interface UseWebSocketOptions {
  onMessage?: WebSocketCallback;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  enabled?: boolean;
}

export const useWebSocket = (
  path: string,
  options: UseWebSocketOptions = {}
): { send: (data: any) => void; close: () => void; connected: boolean } => {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    enabled = true,
  } = options;
  
  const wsRef = useRef<WebSocketService | null>(null);
  const callbacksRef = useRef({
    onMessage,
    onOpen,
    onClose,
    onError,
  });

  // Update callbacks without recreating the effect
  useEffect(() => {
    callbacksRef.current = { onMessage, onOpen, onClose, onError };
  }, [onMessage, onOpen, onClose, onError]);

  // Initialize WebSocket connection
  useEffect(() => {
    if (!enabled) return;

    const ws = new WebSocketService(path);
    wsRef.current = ws;

    const handleMessage = (data: any) => {
      callbacksRef.current.onMessage?.(data);
    };

    const handleOpen = () => {
      callbacksRef.current.onOpen?.();
    };

    const handleClose = () => {
      callbacksRef.current.onClose?.();
    };

    const handleError = (error: Event) => {
      callbacksRef.current.onError?.(error);
    };

    ws.subscribe(handleMessage);
    
    // Set up event listeners using the WebSocketService's internal event system
    const originalOnOpen = wsRef.current['onopen'];
    const originalOnClose = wsRef.current['onclose'];
    const originalOnError = wsRef.current['onerror'];
    
    if (wsRef.current) {
      wsRef.current['onopen'] = (event: Event) => {
        originalOnOpen?.(event);
        handleOpen();
      };
      
      wsRef.current['onclose'] = (event: CloseEvent) => {
        originalOnClose?.(event);
        handleClose();
      };
      
      wsRef.current['onerror'] = (event: Event) => {
        originalOnError?.(event);
        handleError(event);
      };
    }

    return () => {
      ws.unsubscribe(handleMessage);
      ws.close();
      wsRef.current = null;
    };
  }, [path, enabled]);

  const send = useCallback((data: any) => {
    if (wsRef.current) {
      wsRef.current.send(data);
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const close = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return {
    send,
    close,
    connected: wsRef.current?.connected || false,
  };
};

// Hook for system metrics WebSocket
export const useSystemMetricsWebSocket = (options: Omit<UseWebSocketOptions, 'enabled'>) => {
  const { onMessage, onOpen, onClose, onError } = options;
  
  const wsRef = useRef<ReturnType<typeof useWebSocket> | null>(null);
  const callbacksRef = useRef({
    onMessage,
    onOpen,
    onClose,
    onError,
  });

  // Update callbacks without recreating the effect
  useEffect(() => {
    callbacksRef.current = { onMessage, onOpen, onClose, onError };
  }, [onMessage, onOpen, onClose, onError]);

  // Initialize WebSocket connection
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const ws = new WebSocketService(`/ws/system-metrics?token=${token}`);
    wsRef.current = {
      send: (data) => ws.send(data),
      close: () => ws.close(),
      connected: ws.connected,
    };

    const handleMessage = (data: any) => {
      callbacksRef.current.onMessage?.(data);
    };

    const handleOpen = () => {
      callbacksRef.current.onOpen?.();
    };

    const handleClose = () => {
      callbacksRef.current.onClose?.();
    };

    const handleError = (error: Event) => {
      callbacksRef.current.onError?.(error);
    };

    ws.subscribe(handleMessage);
    
    // Set up event listeners using the WebSocketService's internal event system
    const originalOnOpen = ws['onopen'];
    const originalOnClose = ws['onclose'];
    const originalOnError = ws['onerror'];
    
    ws['onopen'] = (event: Event) => {
      originalOnOpen?.(event);
      handleOpen();
    };
    
    ws['onclose'] = (event: CloseEvent) => {
      originalOnClose?.(event);
      handleClose();
    };
    
    ws['onerror'] = (event: Event) => {
      originalOnError?.(event);
      handleError(event);
    };

    return () => {
      ws.unsubscribe(handleMessage);
      ws.close();
      wsRef.current = null;
    };
  }, []);

  const send = useCallback((data: any) => {
    if (wsRef.current) {
      wsRef.current.send(data);
    } else {
      console.warn('System metrics WebSocket is not connected');
    }
  }, []);

  const close = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return {
    send,
    close,
    connected: wsRef.current?.connected || false,
  };
};
