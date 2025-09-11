// hooks/useSystemMetricsWebSocket.ts
import { useEffect, useRef, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { WebSocketService } from '../services/websocket';
import type { UseWebSocketOptions } from '../hooks/useWebSocket';
import {
  setConnectionStatus,
  setSystemInfo,
  setAllAgents,
  setError,
} from '../store/slices/metricsSlice';
import { API_ENDPOINTS } from '../config/constants';

// keep all app semantics out of the service; do it here
function normalizeAgents(src: any) {
  const s = src?.agents ?? src ?? {};
  return {
    sir_hawkington: s.sir_hawkington ?? null,
    meth_snail: s.meth_snail ?? null,
    hamsters: s.hamsters ?? null,
    quantum_shadow: s.quantum_shadow ?? s.quantum_shadow_people ?? null,
    the_stick: s.the_stick ?? null,
    vic20_sage: s.vic20_sage ?? s.vic_20_sage ?? null,
  };
}

export const useSystemMetricsWebSocket = (
  options: Omit<UseWebSocketOptions, 'enabled'>
) => {
  const { onMessage, onOpen, onClose, onError } = options;

  const dispatch = useDispatch();
  const svcRef = useRef<WebSocketService | null>(null);
  const callbacksRef = useRef({ onMessage, onOpen, onClose, onError });

  useEffect(() => {
    callbacksRef.current = { onMessage, onOpen, onClose, onError };
  }, [onMessage, onOpen, onClose, onError]);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    console.log('[useSystemMetricsWebSocket] Token check:', { hasToken: !!token, tokenLength: token?.length });

    if (!token) {
      console.log('[useSystemMetricsWebSocket] No token - aborting connection');
      return;
    }

    console.log('[useSystemMetricsWebSocket] Initializing WebSocket connection...');
    const ws = new WebSocketService(API_ENDPOINTS.WEBSOCKET.SYSTEM_METRICS); // no token here;
    svcRef.current = ws;

    // single subscriber with the app-level switch(msg.type)
    const handleMessage = (msg: any) => {
      try {
        switch (msg?.type) {
          case 'connection_established':
            dispatch(setConnectionStatus('connecting'));
            break;

          case 'registration_error':
            dispatch(setConnectionStatus('error'));
            dispatch(setError(msg.message || 'registration_failed'));
            break;

          case 'system_info':
            dispatch(setConnectionStatus('connected'));
            dispatch(setSystemInfo(msg.data || {}));
            break;

          case 'metrics_update':
            dispatch(setConnectionStatus('connected'));
            dispatch(setAllAgents(normalizeAgents(msg.data)));
            break;

          case 'persist_result':
            if (!msg.ok) {
              dispatch(setError(`persist_error: ${String(msg.error || 'unknown')}`));
            }
            // success is fine to ignore here
            break;

          case 'error':
            dispatch(setError(msg.message || 'websocket_error'));
            break;

          default:
            // not our circus; quietly ignore
            break;
        }
      } finally {
        // still fan out to any optional external callback the caller provided
        callbacksRef.current.onMessage?.(msg);
      }
    };

    ws.subscribe(handleMessage);

    // bring the pipe up
    ws.ensureConnected();
    ws.waitUntilOpen(4000).then(ok => {
      if (ok) {
        callbacksRef.current.onOpen?.();
        // optional nudge: ask server for a fresh snapshot
        ws.send({ type: 'request_system_info' });
      }
    });

    // wire error/close into optional callbacks
    ws.onerror = (evt: Event) => callbacksRef.current.onError?.(evt);
    ws.onclose = () => callbacksRef.current.onClose?.();

    return () => {
      ws.unsubscribe(handleMessage);
      ws.close();
      svcRef.current = null;
    };
  }, [dispatch]);

  const send = useCallback(async (data: any) => {
    const ws = svcRef.current;
    if (!ws) {
      console.warn('System metrics WebSocket is not initialized');
      return;
    }
    const ok = await ws.waitUntilOpen(4000);
    if (!ok) {
      console.warn('System metrics WebSocket did not open in time; skipping send');
      return;
    }
    ws.send(data);
  }, []);

  const close = useCallback(() => {
    if (svcRef.current) {
      svcRef.current.close();
      svcRef.current = null;
    }
  }, []);

  return {
    send,
    close,
    connected: !!svcRef.current?.connected,
  };
};
