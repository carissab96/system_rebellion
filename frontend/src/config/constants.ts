// API Configuration - Using Vite environment variables
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// WebSocket URL - automatically use wss:// for HTTPS sites, ws:// for HTTP
const getWebSocketBaseUrl = () => {
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }
  
  // Auto-detect protocol based on current page protocol
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.hostname;
  const port = import.meta.env.DEV ? ':8000' : '';
  
  return `${protocol}//${host}${port}`;
};

export const WS_BASE_URL = getWebSocketBaseUrl();

// Local Storage Keys
export const AUTH_TOKEN_KEY = 'access_token';
export const REFRESH_TOKEN_KEY = 'refresh_token';

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/token',
    REGISTER: '/auth/register',
    REFRESH_TOKEN: '/auth/refresh-token',
    PROFILE: '/auth/me',
    LOGOUT: '/auth/logout',
  },
  SYSTEM: {
    METRICS: '/system/metrics',
    STATUS: '/system/status',
    CONFIG: '/system/config',
  },
  AI_AGENTS: {
    STATUS: '/ai-agents/status',
    CONTROL: '/ai-agents/control',
  },
  WEBSOCKET: {
    SYSTEM_METRICS: '/api/ws/system-metrics',
    AGENT_UPDATES: '/api/ws/agent-updates',
  },
} as const;

// Default request timeout (in milliseconds)
export const DEFAULT_TIMEOUT = 10000;

// WebSocket configuration
export const WS_RECONNECT_INTERVAL = 3000; // 3 seconds
export const WS_MAX_RECONNECT_ATTEMPTS = 5;
