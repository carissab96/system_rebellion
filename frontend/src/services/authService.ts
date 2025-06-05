// src/services/authService.ts
import axios from 'axios';

// Define types
export interface User {
  id: string;
  username: string;
  email: string;
  operating_system?: string;
  os_version?: string;
  cpu_cores?: number;
  total_memory?: number;
  avatar?: string;
  needs_onboarding?: boolean;
  profile?: any;
  preferences?: any;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface RefreshResponse {
  access_token: string;
  refresh_token?: string;
}

// Set up axios instance with authentication
const authApi = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/auth',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add interceptors here...
authApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Create the AuthService class
class AuthService {
  register(username: any, email: any, password: any) {
    throw new Error('Method not implemented.');
  }
  getCurrentUser() {
    throw new Error('Method not implemented.');
  }
  private authApi = authApi;
  updateProfile: any;
  
  async getCurrentToken(): Promise<string | null> {
    // First try to get from localStorage
    const token = localStorage.getItem('token');
    
    if (!token) {
      return null;
    }
    
    // Check if token is expired
    if (this.isTokenExpired(token)) {
      try {
        await this.refreshToken();
        return localStorage.getItem('token');
      } catch (error) {
        console.error('Failed to refresh token:', error);
        return null;
      }
    }
    
    return token;
  }
  
  private isTokenExpired(token: string): boolean {
    if (!token) return true;
    
    try {
      const decoded = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return decoded.exp < currentTime;
    } catch (error) {
      console.error('Error decoding token:', error);
      return true;
    }
  }
  
  private async refreshToken(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      // throw new Error('No refresh token available');
    }
    
    try {
      const response = await axios.post<RefreshResponse>(
        'http://127.0.0.1:8000/api/auth/refresh-token',
        { refresh_token: refreshToken },
        { withCredentials: true }
      );
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      throw error;
    }
  }
  
  async checkStatus(): Promise<boolean> {
    try {
      console.log('🦔 Sir Hawkington: Checking authentication status...');
      const response = await this.authApi.get('/status/');
      console.log('🦔 Auth status check response:', response.data);
      return response.data.is_authenticated;
    } catch (error: any) {
      console.error('🚨 Auth status check failed:', error);
      return false;
    }
  }
  
  async login(username: string, password: string): Promise<User> {
    try {
      console.log('🦔 Sir Hawkington: Logging in with username:', username);
      
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await axios.post<LoginResponse>(
        'http://127.0.0.1:8000/api/auth/token',
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          withCredentials: true
        }
      );
      
      console.log('✅ Login response:', response.data);
      
      if (!response.data.access_token || !response.data.refresh_token) {
        throw new Error('Invalid response from server: missing tokens');
      }
      
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('username', response.data.user.username);
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      
      return response.data.user;
    } catch (error: any) {
      let errorMessage = 'Authentication failed. Please try again.';
      
      if (error.response) {
        console.error('🚨 Login failed - Server response:', {
          status: error.response.status,
          data: error.response.data
        });
        errorMessage = error.response.data?.detail || 
                       'Authentication failed. Please check your username and password.';
      } else if (error.request) {
        console.error('🚨 Login failed - No response:', error.request);
        errorMessage = 'The Quantum Shadow People blocked your request. Please try again later.';
      } else {
        console.error('🚨 Login setup failed:', error.message);
      }
      
      throw new Error(errorMessage);
    }
  }
  
  async logout(): Promise<boolean> {
    try {
      console.log('🦔 Sir Hawkington: Logging out...');
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username');
      console.log('🐌 The Meth Snail: Local storage cleared, redirecting to login page');
      window.location.href = '/login';
      return true;
    } catch (error: any) {
      console.error('🚨 Logout failed:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username');
      window.location.href = '/login';
      return false;
    }
  }
  
  // Add other methods as needed...
}

// Export a single instance
const authService = new AuthService();
export default authService;