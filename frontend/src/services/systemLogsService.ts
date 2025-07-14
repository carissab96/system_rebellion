import axios from 'axios';

export interface SystemLog {
  message: string;
  level: 'info' | 'warning' | 'error' | 'success' | 'command';
  source: string;
  timestamp: string;
}

export interface SystemLogsResponse {
  logs: SystemLog[];
  total: number;
  has_more: boolean;
}

const systemLogsService = {
  /**
   * Get system logs with optional filtering
   */
  getLogs: async (limit = 100, source?: string, level?: string): Promise<SystemLogsResponse> => {
    try {
      console.log('🦔 Sir Hawkington: Fetching system logs...');
      
      // Get the token from localStorage
      const token = localStorage.getItem('token');
      console.log('🦔 Sir Hawkington: Checking auth token:', token ? 'Token exists' : 'No token');
      
      if (!token) {
        console.warn('🦔 Sir Hawkington: No authentication token found!');
        return { logs: [], total: 0, has_more: false };
      }
      
      // Clean the token to ensure it's properly formatted
      const cleanToken = token.replace(/["']/g, '').trim();
      const authHeader = cleanToken.startsWith('Bearer ') ? cleanToken : `Bearer ${cleanToken}`;
      
      // Build the URL
      let url = 'http://localhost:8000/api/system-logs';
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      if (source) params.append('source', source);
      if (level) params.append('level', level);
      
      const fullUrl = `${url}?${params.toString()}`;
      console.log('🦔 Sir Hawkington: System logs URL:', fullUrl);
      
      // Make a direct axios call with explicit headers
      try {
        const response = await axios.get(fullUrl, {
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        console.log('✅ System logs response:', response.data);
        return response.data;
      } catch (apiError: any) {
        console.error('🚨 API Error details:', {
          status: apiError.response?.status,
          statusText: apiError.response?.statusText,
          data: apiError.response?.data,
          headers: apiError.response?.headers,
          url: apiError.config?.url
        });
        throw apiError;
      }
    } catch (error) {
      console.error('🚨 Error fetching system logs:', error);
      // Return empty response to prevent UI crashes
      return { logs: [], total: 0, has_more: false };
    }
  },
  
  /**
   * Clear all system logs
   */
  clearLogs: async (): Promise<{ message: string }> => {
    try {
      console.log('🦔 Sir Hawkington: Clearing system logs...');
      
      // Get the token from localStorage
      const token = localStorage.getItem('token');
      console.log('🦔 Sir Hawkington: Checking auth token for clear logs:', token ? 'Token exists' : 'No token');
      
      if (!token) {
        console.warn('🦔 Sir Hawkington: No authentication token found for clear logs!');
        return { message: 'Failed to clear logs: No authentication token' };
      }
      
      // Clean the token to ensure it's properly formatted
      const cleanToken = token.replace(/["']/g, '').trim();
      const authHeader = cleanToken.startsWith('Bearer ') ? cleanToken : `Bearer ${cleanToken}`;
      
      // Build the URL
      const url = 'http://localhost:8000/api/system-logs';
      console.log('🦔 Sir Hawkington: Clear logs URL:', url);
      
      // Make a direct axios call with explicit headers
      try {
        const response = await axios.delete(url, {
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        console.log('✅ Clear logs response:', response.data);
        return response.data;
      } catch (apiError: any) {
        console.error('🚨 API Error details for clear logs:', {
          status: apiError.response?.status,
          statusText: apiError.response?.statusText,
          data: apiError.response?.data,
          headers: apiError.response?.headers,
          url: apiError.config?.url
        });
        throw apiError;
      }
    } catch (error) {
      console.error('🚨 Error clearing system logs:', error);
      return { message: 'Failed to clear logs' };
    }
  }
};

export default systemLogsService;
