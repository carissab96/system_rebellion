// frontend/src/utils/csrf.ts
import axios from 'axios';

export const getCsrfToken = async () => {
    try {
        const response = await axios.get('/csrf-token', { 
            withCredentials: true 
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