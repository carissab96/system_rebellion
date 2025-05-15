// frontend/src/utils/csrf.ts
import axios from 'axios';

export const getCsrfToken = async () => {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/auth/csrf_token`, {
      withCredentials: true,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Cache': 'no-cache'
      },
      params: {
        _t: Date.now() // Add timestamp to prevent caching
      }
    });

      return response.data.csrf_token;
  } catch (error) {
      console.error('Failed to get CSRF token', error);
      return null;
  }
};

// Add CSRF token to all axios requests
axios.interceptors.request.use(async (config) => {
    const csrfToken = await getCsrfToken();
    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
});
export const initializeCsrf = async () => {
    try {
      // Make the request but don't store the response since we're not using it
      await axios.get(`${import.meta.env.VITE_API_URL}/health-check/`, {
        withCredentials: true,
        timeout: 5000 // 5 second timeout
      });
  
      // Verify CSRF token
      const csrfToken = await getCsrfToken();
      if (!csrfToken) {
        console.warn('CSRF token not found in cookies after initialization');
        
        // Retry once
        await axios.get(`${import.meta.env.VITE_API_URL}/health-check/`, {
          withCredentials: true,
          timeout: 5000
        });
      }
  
      return true;
    } catch (error) {
      console.error('CSRF initialization failed', error);
      return false;
    }
  };