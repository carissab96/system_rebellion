// frontend/src/utils/csrf.ts
import axios from 'axios';

// Sir Hawkington's Distinguished CSRFAxios Instance
// This prevents the circular dependency by not applying interceptors
const csrfAxios = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true
});

// The Meth Snail's Global Token Cache
let csrfTokenCache: string | null = null;

export const getCsrfToken = async (forceRefresh = false): Promise<string | null> => {
  // Return cached token unless refresh is forced
  if (csrfTokenCache && !forceRefresh) {
    console.log("🦔 Sir Hawkington: Using cached CSRF token");
    return csrfTokenCache;
  }

  try {
    console.log("🐌 The Meth Snail: Fetching fresh CSRF token...");
    const response = await csrfAxios.get('/api/auth/csrf_token', {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      },
      params: {
        _t: Date.now() // Add timestamp to prevent caching
      }
    });

    console.log("🦔 Sir Hawkington: CSRF response status:", response.status);
    
    if (response.data && response.data.csrf_token) {
      csrfTokenCache = response.data.csrf_token;
      console.log("🐌 The Meth Snail: CSRF token obtained successfully");
      return csrfTokenCache;
    } else {
      console.warn("🦔 Sir Hawkington is concerned! No CSRF token in response");
      return null;
    }
  } catch (error) {
    console.error('🐌 The Meth Snail failed to fetch the CSRF token!', error);
    return null;
  }
};

// Add CSRF token to all axios requests (but not to CSRF token requests)
axios.interceptors.request.use(async (config) => {
    // Skip for CSRF token endpoint to avoid circular dependency
    if (config.url && config.url.includes('/api/auth/csrf_token')) {
        return config;
    }
    
    try {
        // Get token (use cache if available)
        const token = await getCsrfToken();
        if (token) {
            // Set the header with the token
            config.headers['X-CSRFToken'] = token;
        }
    } catch (error) {
        console.warn("🧙‍♂️ The Stick warns: Failed to add CSRF token to request", error);
    }
    
    return config;
});

export const initializeCsrf = async (): Promise<boolean> => {
    console.log("🦔 Sir Hawkington is initializing CSRF protection...");
    try {
        // Try to get a CSRF token (this will set cookies as well)
        const token = await getCsrfToken(true);
        
        if (!token) {
            console.error("🧙‍♂️ The Stick says: Failed to get CSRF token!");
            return false;
        }
        
        // Let's make sure our token is valid by checking another endpoint
        try {
            console.log("🐹 Hamsters verifying token validity...");
            await axios.get(`${import.meta.env.VITE_API_URL}/api/auth/status/`, {
                withCredentials: true,
                headers: {
                    'X-CSRFToken': token
                },
                timeout: 5000
            });
            console.log("🐹 Hamsters: Token validation successful!");
        } catch (statusError) {
            console.warn("🐹 Hamsters: Status check with token failed:", statusError);
            // Continue anyway - this is just a validation check
        }
        
        console.log("🎉 The VIC-20 celebrates! CSRF initialized successfully!");
        return true;
    } catch (error) {
        console.error('🖥️ The VIC-20 crashed during CSRF initialization!', error);
        return false;
    }
};

// Export a function to get the current CSRF token value
export const getCurrentCsrfToken = () => csrfTokenCache;