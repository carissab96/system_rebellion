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
};

// WebSocket Endpoint Constants
export const WS_ENDPOINTS = {
};
