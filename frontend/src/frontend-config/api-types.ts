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
  DETECT: "/detect",
  SYSTEM: "/system",
  METRICS: "/metrics",
  : "/",
  METRIC_ID: "/{metric_id}",
  METRIC_ID: "/{metric_id}",
  METRIC_ID: "/{metric_id}",
  : "/",
  : "/",
  HEALTH_CHECK: "/health-check",
  CSRF_TOKEN: "/csrf_token",
  METRICS_CURRENT: "/metrics/current",
  RECOMMENDATIONS: "/recommendations",
  PROFILES__PROFILE_ID__APPLY: "/profiles/{profile_id}/apply",
  RECOMMENDATIONS_APPLY: "/recommendations/apply",
  PATTERNS: "/patterns",
  HISTORY: "/history",
  ONBOARDING_PROGRESS: "/onboarding-progress",
  ONBOARDING_PROGRESS: "/onboarding-progress",
  ONBOARDING_PROGRESS: "/onboarding-progress",
  ME: "/me",
  ME: "/me",
  REFRESH_TOKEN: "/refresh-token",
  REGISTER: "/register",
  CREATE_TEST_USER: "/create-test-user",
  TOKEN: "/token",
  DEBUG_USER_MODEL: "/debug/user-model",
  DEBUG_DB_TEST: "/debug/db-test",
  DEBUG_DB_CONFIG: "/debug/db-config",
  HEALTH_CHECK: "/health-check/",
  STATUS: "/status/",
  ME: "/me",
  COMPLETE_ONBOARDING: "/complete-onboarding",
  DIRECT_PROFILE_UPDATE__EMAIL: "/direct-profile-update/{email}",
  UPDATE_PROFILE: "/update-profile",
  HAMSTERS_RECOMMENDATIONS: "/hamsters/recommendations",
  HAMSTERS_APPLY_ENGINEERING: "/hamsters/apply-engineering",
  HAMSTERS_EMERGENCY: "/hamsters/emergency",
  HAMSTERS_HISTORY: "/hamsters/history",
  HAMSTERS_COMMUNICATION_LOG: "/hamsters/communication-log",
  HAMSTERS_SUPPLY_CLOSET: "/hamsters/supply-closet",
  HAMSTERS_RESTOCK: "/hamsters/restock",
  HAMSTERS_STATS: "/hamsters/stats",
  HAMSTERS_RESET: "/hamsters/reset",
  EMERGENCY_INTERVENTION: "/emergency-intervention",
  DISK_CLEANUP: "/disk-cleanup",
  SUPPLY_CLOSET_INVENTORY: "/supply-closet-inventory",
  BEER_STATUS: "/beer-status",
  RESTOCK_SUPPLIES: "/restock-supplies",
  JITTER_LEVELS: "/jitter-levels",
  OPTIMIZATION_METRICS: "/optimization-metrics",
  JITTER_AGGREGATES: "/jitter-aggregates",
};

// WebSocket Endpoint Constants
export const WS_ENDPOINTS = {
  SIMPLE_METRICS: "/simple-metrics",
  WS_SYSTEM_METRICS: "/ws/system-metrics",
};
