import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios';
import { API_BASE_URL, WS_BASE_URL } from '../config/constants';


// Types
export interface ApiResponse<T = any> {
  [x: string]: any;
  data: T;
  status: number;
  statusText: string;
}

export interface ApiError {
  message: string;
  status?: number;
  data?: any;
}

// Create axios instance with base config
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor for API calls
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('access_token');
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          // No refresh token, redirect to login
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        const response = await axios.post(
          `${API_BASE_URL}/api/auth/refresh-token`,
          { refresh_token: refreshToken },
          { withCredentials: true }
        );
        
        const { access_token, refresh_token } = response.data;
        
        localStorage.setItem('access_token', access_token);
        if (refresh_token) {
          localStorage.setItem('refresh_token', refresh_token);
        }
        
        // Update the authorization header
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        
        // Retry the original request
        return api(originalRequest);
      } catch (error) {
        // Refresh token failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);

// API methods
export const apiService = {
  // Auth
  login: async (email: string, password: string): Promise<ApiResponse<{ access_token: string; refresh_token: string }>> => {
    const response = await api.post('/api/auth/token', { 
      username: email,  // OAuth2 expects 'username' not 'email'
      password: password,
      grant_type: 'password'  // OAuth2 password flow
    });
    return response;
  },
  
  register: async (email: string, password: string, username: string): Promise<ApiResponse> => {
    const response = await api.post('/api/auth/register', { email, password, username });
    return response;
  },
  
  updateProfile: async (profileData: object): Promise<ApiResponse> => {
    const response = await api.put('/api/auth/me', profileData);  // This endpoint isn't in your config
    return response;
  },

// Add the Authorization header manually to the completeOnboarding call:
completeOnboarding: async (onboardingData: object): Promise<AxiosResponse> => {
  const token = localStorage.getItem('access_token');
  const response = await api.post('/api/auth/complete-onboarding', onboardingData, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response;
},

  //System detection method
  detectSystem: async(): Promise<ApiResponse> => {
    const response = await api.get('/api/system/detect');
    return response;
  },
  
  // System Metrics
  getSystemMetrics: async (): Promise<ApiResponse> => {
    const response = await api.get('/api/metrics/system');  // Should match your config
    return response;
  },
  
  // AI Agents
  getAgentStatus: async (): Promise<ApiResponse> => {
    const response = await api.get('/api/ai-agents/status');  // Added /api prefix
    return response;
  },

  
  // WebSocket
  getWebSocketUrl: (): string => {
    const token = localStorage.getItem('access_token');
    return `${WS_BASE_URL}/ws/system-metrics?token=${token}`;
  },
  
  // Generic request method
  request: async <T = any>(config: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    const response = await api.request<T>(config);
    return response;
  },
};

export default apiService;
