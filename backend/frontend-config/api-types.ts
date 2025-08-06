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
  : "/",
  : "/",
  : "/",
  METRIC_ID: "/{metric_id}",
  METRIC_ID: "/{metric_id}",
  METRIC_ID: "/{metric_id}",
  REGISTER: "/register",
  TOKEN: "/token",
  STATUS: "/status",
  PROFILE: "/profile",
  CSRF_TOKEN: "/csrf_token",
  REFRESH_TOKEN: "/refresh-token",
  LOGIN: "/login",
  ME: "/me",
  VALIDATE_TOKEN: "/validate-token",
  REFRESH: "/refresh",
  LOGOUT: "/logout",
  DETECT: "/detect",
  : "/",
  : "/",
  PROFILE_ID: "/{profile_id}",
  PROFILE_ID: "/{profile_id}",
  PROFILE_ID: "/{profile_id}",
  PROFILE_ID__ACTIVATE: "/{profile_id}/activate",
  : "/",
  : "/",
  CONFIG_ID: "/{config_id}",
  CONFIG_ID: "/{config_id}",
  CONFIG_ID: "/{config_id}",
  CONFIG_ID__ACTIVATE: "/{config_id}/activate",
  : "/",
  : "/",
  ALERT_ID: "/{alert_id}",
  ALERT_ID: "/{alert_id}",
  ALERT_ID: "/{alert_id}",
  ALERT_ID__MARK_AS_READ: "/{alert_id}/mark-as-read",
  MARK_ALL_AS_READ: "/mark-all-as-read",
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
  ME: "/me",
  ME: "/me",
  ONBOARDING_PROGRESS: "/onboarding-progress",
  ONBOARDING_PROGRESS: "/onboarding-progress",
  ONBOARDING_PROGRESS: "/onboarding-progress",
  EMERGENCY_INTERVENTION: "/emergency-intervention",
  DISK_CLEANUP: "/disk-cleanup",
  SUPPLY_CLOSET_INVENTORY: "/supply-closet-inventory",
  BEER_STATUS: "/beer-status",
  RESTOCK_SUPPLIES: "/restock-supplies",
  HAMSTERS_RECOMMENDATIONS: "/hamsters/recommendations",
  HAMSTERS_APPLY_ENGINEERING: "/hamsters/apply-engineering",
  HAMSTERS_EMERGENCY: "/hamsters/emergency",
  HAMSTERS_HISTORY: "/hamsters/history",
  HAMSTERS_COMMUNICATION_LOG: "/hamsters/communication-log",
  HAMSTERS_SUPPLY_CLOSET: "/hamsters/supply-closet",
  HAMSTERS_RESTOCK: "/hamsters/restock",
  HAMSTERS_STATS: "/hamsters/stats",
  HAMSTERS_RESET: "/hamsters/reset",
};

// WebSocket Endpoint Constants
export const WS_ENDPOINTS = {
  SIMPLE_METRICS: "/simple-metrics",
  WS_SYSTEM_METRICS: "/ws/system-metrics",
  WS_SYSTEM_METRICS: "/ws/system-metrics",
};
