// In a new file: src/utils/diagnostics.ts
import axios from 'axios';

export const runDiagnostics = async () => {
  console.log("🔍 Running system diagnostics...");
  
  try {
    // Check backend health
    console.log("🩺 Checking backend health...");
    try {
      const healthResponse = await axios.get('http://127.0.0.1:8000/api/health-check');
      console.log("✅ Backend health check succeeded:", healthResponse.data);
    } catch (error) {
      console.error("❌ Backend health check failed:", error);
    }
    
    // Check auth endpoints
    console.log("🔐 Checking auth status endpoint...");
    try {
      const authResponse = await axios.get('http://127.0.0.1:8000/api/auth/status', { withCredentials: true });
      console.log("✅ Auth status check succeeded:", authResponse.data);
    } catch (error) {
      console.error("❌ Auth status check failed:", error);
    }
    
    // First request to get the CSRF cookie
    const response = await axios.get('http://127.0.0.1:8000/api/auth/csrf_token', { 
      withCredentials: true 
    });
    
    console.log('🔍 Response headers:', JSON.stringify(response.headers, null, 2));
    console.log('🍪 Document cookies:', typeof document !== 'undefined' ? document.cookie : 'No document object');


    /// Try to get token from response headers (case insensitive)
const headers = response.headers as Record<string, string>;
const headerKeys = Object.keys(headers);
const csrfHeaderKey = headerKeys.find(key => key.toLowerCase() === 'x-csrftoken');

if (csrfHeaderKey) {
  const csrfToken = headers[csrfHeaderKey];
  console.log('🔑 Found CSRF token in headers:', csrfToken);
} 
// Fallback to checking cookies if running in browser
else if (typeof document !== 'undefined') {
  const getCookie = (name: string): string | undefined => {
    return document.cookie
      .split('; ')
      .find(row => row.startsWith(`${name}=`))
      ?.split('=')[1];
  };
  const csrfToken = getCookie('XSRF-TOKEN');
  if (csrfToken) {
    console.log('🍪 Found CSRF token in cookies:', csrfToken);
    }
  }   

  console.log("🏁 Diagnostics completed");
  } catch (error) {
    console.error("💥 Diagnostics crashed:", error);
  }
}
