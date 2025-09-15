import { useEffect, useRef, useCallback } from 'react';
import { WebSocketService } from '../services/websocket';

type WebSocketCallback = (data: any) => void;

export interface UseWebSocketOptions {
  onMessage?: WebSocketCallback;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  enabled?: boolean;
}

export const useWebSocket = (
  path: string,
  options: UseWebSocketOptions = {}
): { send: (data: any) => Promise<void>; close: () => void; connected: boolean } => {
  const { onMessage, onOpen, onClose, onError, enabled = true } = options;

  const wsRef = useRef<WebSocketService | null>(null);
  const callbacksRef = useRef({ onMessage, onOpen, onClose, onError });

  useEffect(() => {
    callbacksRef.current = { onMessage, onOpen, onClose, onError };
  }, [onMessage, onOpen, onClose, onError]);

  useEffect(() => {
    if (!enabled) return;

    const ws = new WebSocketService(path);
    wsRef.current = ws;

    const handleMessage = (data: any) => callbacksRef.current.onMessage?.(data);
    ws.subscribe(handleMessage);

    // Ensure a connection now, and notify on open
    ws.ensureConnected(path);
    ws.waitUntilOpen(4000).then(() => {
      callbacksRef.current.onOpen?.();
    });

    // Wire error/close callbacks
    ws.onError = (evt: Event) => callbacksRef.current.onError?.(evt);
    ws.onClose = () => callbacksRef.current.onClose?.();

    return () => {
      ws.unsubscribe(handleMessage);
      ws.close();
      wsRef.current = null;
    };
  }, [path, enabled]);

  const send = useCallback(async (data: any) => {
    const ws = wsRef.current;
    if (!ws) {
      console.warn('WebSocket is not initialized');
      return;
    }
    await ws.waitUntilOpen(4000);
    ws.send(data);
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
    connected: wsRef.current?.isConnected() || false,
  };
};
