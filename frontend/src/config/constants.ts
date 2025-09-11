// config/constants.ts

// ----- Base URLs (Vite) -----
const rawApi = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000';
export const API_BASE_URL = rawApi.replace(/\/+$/, ''); // strip trailing slash

function computeWsBase(): string {
  const envWs = import.meta.env.VITE_WS_URL as string | undefined;
  if (envWs) return envWs.replace(/\/+$/, '');

  // Derive from API_BASE_URL so HTTP and WS hit the same host:port
  try {
    const u = new URL(API_BASE_URL);
    const proto = u.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${u.host}`; // host includes port
  } catch {
    // Absolute worst-case fallback: current page origin
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${window.location.host}`;
  }
}
export const WS_BASE_URL = computeWsBase();

// ----- Storage keys -----
export const AUTH_TOKEN_KEY = 'access_token';
export const REFRESH_TOKEN_KEY = 'refresh_token';

// ----- API endpoints (align with FastAPI include_router(prefix="/api")) -----
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/token',
    REGISTER: '/api/auth/register',
    REFRESH_TOKEN: '/api/auth/refresh-token',
    PROFILE: '/api/auth/me',
    LOGOUT: '/api/auth/logout',
  },
  SYSTEM: {
    METRICS: '/api/metrics/system',
    STATUS: '/api/system/status',  // keep if you actually have it
    CONFIG: '/api/system/config',  // same here
  },
  AI_AGENTS: {
    STATUS: '/api/ai-agents/status',
    CONTROL: '/api/ai-agents/control',
  },
  WEBSOCKET: {
    SYSTEM_METRICS: '/api/ws/system-metrics',
    AGENT_UPDATES: '/api/ws/agent-updates',
  },
} as const;

// ----- Timeouts / WS backoff -----
export const DEFAULT_TIMEOUT = 10000;

export const WS_RECONNECT_INTERVAL =
  Number(import.meta.env.VITE_WS_RECONNECT_INTERVAL ?? 1000); // ms

export const WS_MAX_RECONNECT_ATTEMPTS =
  Number(import.meta.env.VITE_WS_MAX_RECONNECT_ATTEMPTS ?? 20);
