// hooks/useWebSocketMessages.ts
// Subscribe to raw WebSocket messages for real-time consciousness visualization
// NO FAKE DATA - Only real WebSocket events
// REBUILT FROM SCRATCH - November 13, 2025

import { useEffect, useRef } from 'react';
import { WebSocketService } from '../services/websocket';
import type { WebSocketMessage } from '../types/agents';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

/**
 * Hook to subscribe to real-time WebSocket messages
 * NO FAKE DATA - Only real events from the backend
 */
export const useWebSocketMessages = (
  handler: (message: WebSocketMessage) => void,
  enabled: boolean = true
) => {
  // Use ref to avoid re-subscribing on every render
  const handlerRef = useRef(handler);
  
  // Update ref when handler changes
  useEffect(() => {
    handlerRef.current = handler;
  }, [handler]);

  useEffect(() => {
    if (!enabled) return;

    // Get the singleton WebSocket service
    const wsService = WebSocketService.getInstance(WS_BASE_URL);
    
    // Wrapper that uses the ref
    const wrappedHandler = (message: any) => {
      handlerRef.current(message);
    };
    
    // Subscribe to ALL messages
    const unsubscribe = wsService.subscribe(wrappedHandler);
    
    console.log('🎭 Consciousness Theater subscribed to WebSocket');
    
    // Cleanup on unmount
    return () => {
      console.log('🎭 Consciousness Theater unsubscribed from WebSocket');
      unsubscribe();
    };
  }, [enabled]); // Only re-subscribe if enabled changes
};
