// Generated API Types for System Rebellion Frontend
// Auto-generated from backend endpoints

export interface ApiEndpoint {
  method: string;
  path: string;
  handler: string;
  file: string;
  line: number;
}

export interface WebSocketEndpoint {
  path: string;
  handler: string;
  file: string;
  line: number;
}

export interface ApiConfig {
  API_BASE_URL: string;
  WS_BASE_URL: string;
  endpoints: {
    auth: ApiEndpoint[];
    users: ApiEndpoint[];
    agents: ApiEndpoint[];
    metrics: ApiEndpoint[];
    websockets: WebSocketEndpoint[];
  };
}

// API Endpoint Constants
export const API_ENDPOINTS = {
  API_DEBUG_PING: "/api/debug/ping",
  HEALTH_CHECK: "/health-check/",
  API_HEALTH_CHECK: "/api/health-check/",
  API_AI_AGENTS_STATUS: "/api/ai-agents/status",
  API_AUTH_CSRF_TOKEN: "/api/auth/csrf_token",
  SYSTEM: "/system",
  METRIC_ID: "/{metric_id}",
  REGISTER: "/register",
  TOKEN: "/token",
  STATUS: "/status",
  PROFILE: "/profile",
  CSRF_TOKEN: "/csrf_token",
  REFRESH_TOKEN: "/refresh-token",
  LOGIN: "/login",
  VALIDATE_TOKEN: "/validate-token",
  REFRESH: "/refresh",
  LOGOUT: "/logout",
  PROFILE_ID: "/{profile_id}",
  PROFILE_ID__ACTIVATE: "/{profile_id}/activate",
  CONFIG_ID: "/{config_id}",
  CONFIG_ID__ACTIVATE: "/{config_id}/activate",
  ALERT_ID: "/{alert_id}",
  ALERT_ID__MARK_AS_READ: "/{alert_id}/mark-as-read",
  MARK_ALL_AS_READ: "/mark-all-as-read",
  CREATE_TEST_USER: "/create-test-user",
  DEBUG_USER_MODEL: "/debug/user-model",
  DEBUG_DB_TEST: "/debug/db-test",
  DEBUG_DB_CONFIG: "/debug/db-config",
  USERS_COMPLETE_ONBOARDING: "/users/complete-onboarding",
  DIRECT_PROFILE_UPDATE__email: "/direct-profile-update/{email}",
  UPDATE_PROFILE: "/update-profile",
  METRICS_CURRENT: "/metrics/current",
  RECOMMENDATIONS: "/recommendations",
  PROFILES__PROFILE_ID__APPLY: "/profiles/{profile_id}/apply",
  RECOMMENDATIONS_APPLY: "/recommendations/apply",
  PATTERNS: "/patterns",
  HISTORY: "/history",
  HAMSTERS_RECOMMENDATIONS: "/hamsters/recommendations",
  HAMSTERS_APPLY_ENGINEERING: "/hamsters/apply-engineering",
  HAMSTERS_HISTORY: "/hamsters/history",
  HAMSTERS_PATTERNS: "/hamsters/patterns",
  HAMSTERS_STATS: "/hamsters/stats",
  HAMSTERS_RESTOCK: "/hamsters/restock",
  HAMSTERS_RESET: "/hamsters/reset",
};

// WebSocket Endpoint Constants
export const WS_ENDPOINTS = {
  SIMPLE_METRICS: "/simple-metrics",
  WS_SYSTEM_METRICS: "/ws/system-metrics",
};
