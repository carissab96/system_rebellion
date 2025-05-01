import api from './api';

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
    let url = `/api/system-logs?limit=${limit}`;
    if (source) url += `&source=${source}`;
    if (level) url += `&level=${level}`;
    
    const response = await api.get<SystemLogsResponse>(url);
    return response.data;
  },
  
  /**
   * Clear all system logs
   */
  clearLogs: async (): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>('/api/system-logs');
    return response.data;
  }
};

export default systemLogsService;
