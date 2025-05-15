import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { login } from '../../../store/slices/authSlice';
import { useNavigate } from 'react-router-dom';
import { initializeCsrf, checkBackendAvailability } from '../../../utils/api';
import SignupModal from '../SignupModal/SignupModal';
import './login.css';
import { useState, useEffect } from 'react';
import '../../../components/common/Modal.css';
import axios from 'axios';

export interface LoginProps {
  onClose: () => void;
  isOpen: boolean;
}

const Login: React.FC<LoginProps> = ({ onClose, isOpen }) => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [csrfInitialized, setCsrfInitialized] = useState(false);
  const [backendAvailable, setBackendAvailable] = useState(true);
  const [isCheckingBackend, setIsCheckingBackend] = useState(true);
  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false);
  const [hawkingtonQuote, setHawkingtonQuote] = useState("🧐 Sir Hawkington prepares to verify your distinguished credentials!");

  const isLoading = useAppSelector((state) => state.auth.isLoading);
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
  const authError = useAppSelector((state) => state.auth.error);

  const updateHawkingtonQuote = (scenario: 'welcome' | 'error' | 'loading' | 'success') => {
    const quotes = {
      welcome: "🧐 Sir Hawkington prepares to verify your distinguished credentials!",
      error: "🧐 *adjusts monocle in concern* I say, something seems amiss!",
      loading: "🧐 *polishes monocle* Let me verify your credentials...",
      success: "🧐 *tips hat* Welcome back, distinguished rebel!"
    };
    setHawkingtonQuote(quotes[scenario]);
  };

  useEffect(() => {
    const initializeApp = async () => {
      setIsCheckingBackend(true);
      try {
        const available = await checkBackendAvailability();
        setBackendAvailable(available);
        
        if (available) {
          const csrfSuccess = await initializeCsrf();
          setCsrfInitialized(csrfSuccess);
          
          if (!csrfSuccess) {
            setError('Failed to initialize security tokens. Please try again.');
          }
        } else {
          setError('Cannot connect to the server. Please check your connection and try again.');
        }
      } catch (err) {
        setBackendAvailable(false);
        setError('Failed to connect to the server. Please try again later.');
      } finally {
        setIsCheckingBackend(false);
      }
    };

    if (isOpen) {
      initializeApp();
    }
  }, [isOpen]);

  useEffect(() => {
    if (isAuthenticated) {
      console.log('User is authenticated via login modal, redirecting directly to dashboard');
      // Force redirect to dashboard for login users, bypassing onboarding check
      navigate('/dashboard', { replace: true });
      if (onClose) {
        onClose();
      }
    }
  }, [isAuthenticated, navigate, onClose]);

  // Add to your Login component
const handleDirectLogin = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/auth/token', 
      new URLSearchParams({
        'username': 'test',
        'password': 'test'
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        withCredentials: true
      }
    );
    
    console.log("✅ Direct login succeeded:", response.data);
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    // Redirect or update UI
  } catch (error) {
    console.error("❌ Direct login failed:", error);
  }
};


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); // Clear previous errors
    
    // Validate form data
    if (!username || !password) {
      setError('Username and password are required');
      updateHawkingtonQuote('error');
      return;
    }
    
    console.log("Login attempt with:", { username, password: "***" });

    // Check backend availability first
    try {
      const available = await checkBackendAvailability();
      if (!available) {
        console.log("Backend not available, aborting login");
        setError('Cannot login: Server is currently unavailable');
        updateHawkingtonQuote('error');
        return;
      }
      setBackendAvailable(true);
    } catch (err) {
      console.error("Backend availability check failed", err);
      setError('Cannot connect to server. Please try again later.');
      updateHawkingtonQuote('error');
      return;
    }
    
    // Initialize CSRF if needed
    if (!csrfInitialized) {
      try {
        const csrfSuccess = await initializeCsrf();
        setCsrfInitialized(csrfSuccess);
        
        if (!csrfSuccess) {
          setError('Security token initialization failed. Please refresh the page.');
          return;
        }
      } catch (err) {
        console.error("CSRF initialization failed", err);
        setError('Security setup failed. Please refresh and try again.');
        return;
      }
    }

    try {
      console.log("Dispatching login action with:", { username, password: '***' });
      updateHawkingtonQuote('loading');
      
      // Ensure we're sending the correct data format
      const loginData = {
        username: username.trim(),
        password: password
      };
      
      // Clear any existing tokens to prevent conflicts
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      
      // Store username in localStorage before dispatching login
      localStorage.setItem('username', username.trim());
      console.log("Stored username in localStorage:", username.trim());
      
      const result = await dispatch(login(loginData)).unwrap();
      console.log("Login successful", result);
      
      if (!result) {
        throw new Error('Invalid response received from server');
      }
      
      updateHawkingtonQuote('success');
      
      // Login users should always go directly to dashboard
      console.log('Login successful via login modal, will redirect to dashboard');
      
      // No need to check system info for login users - the useEffect will handle the redirect
    } catch (err: any) {
      console.error("Login failed", err);
      
      // Extract meaningful error message if possible
      let errorMessage = 'Login failed. Please check your credentials and try again.';
      
      if (err.response?.data?.detail) {
        errorMessage = `Login failed: ${err.response.data.detail}`;
      } else if (err.message) {
        errorMessage = `Login failed: ${err.message}`;
      }
      
      setError(errorMessage);
      updateHawkingtonQuote('error');
    }
  };

  const handleOpenSignup = () => {
    setIsSignupModalOpen(true);
    console.log("🧐 Sir Hawkington prepares to guide a new recruit through registration!");
    console.log("🐌 The Meth Snail vibrates with anticipation!");
  };

  const handleCloseSignup = () => {
    setIsSignupModalOpen(false);
    console.log("🧐 Sir Hawkington adjusts his monocle and returns to login duties.");
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="auth-login-container" style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
      }}>
        <div className="auth-login-content" style={{
          backgroundColor: '#1a0458',
          borderRadius: '12px',
          boxShadow: '0 0 20px rgba(0, 245, 212, 0.5)',
          width: '90%',
          maxWidth: '500px',
          padding: '2rem',
          position: 'relative',
          color: '#e2e8f0',
          border: '1px solid rgba(51, 51, 255, 0.3)',
        }}>
          <button style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            background: 'transparent',
            border: 'none',
            color: '#00f5d4',
            fontSize: '24px',
            cursor: 'pointer',
            zIndex: 10,
          }} onClick={onClose}>×</button>
          <div style={{
            marginBottom: '1.5rem',
            textAlign: 'center',
          }}>
            <h2 style={{
              fontSize: '1.8rem',
              color: '#00f5d4',
              marginBottom: '0.5rem',
            }}>System Rebellion Login</h2>
          </div>
          <div className="auth-login modal-body">
            <div className="hawkington-welcome">
              <div className="hawkington-icon">🧐</div>
              <p className="hawkington-quote">{hawkingtonQuote}</p>
            </div>

            <form onSubmit={handleSubmit} className="auth-login login-form">
              {isLoading && <div className="auth-login loading">Logging in...</div>}
              {isCheckingBackend && <div className="auth-login loading">Checking server connection...</div>}
              {error && <div className="auth-login error-message">{error}</div>}
              {authError && <div className="auth-login error-message">{authError}</div>}
              
              <div className="auth-login form-group">
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={isLoading || isCheckingBackend}
                  required
                />
              </div>
              
              <div className="auth-login form-group">
                <label htmlFor="password">Password</label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading || isCheckingBackend}
                  required
                />
              </div>
              
              <button 
                type="submit" 
                className="auth-login button"
                disabled={isLoading || !csrfInitialized || isCheckingBackend || !backendAvailable}
              >
                {isLoading ? 'Sir Hawkington is verifying...' : 'Enter the System Rebellion'}
              </button>
              
              <button type="button" onClick={handleDirectLogin}>
                Direct Login Test
              </button>

              <div className="auth-login signup-prompt">
                <p>Not a member of the System Rebellion yet?</p>
                <button 
                  type="button" 
                  className="auth-login signup-button cosmic-button" 
                  onClick={handleOpenSignup}
                  disabled={isLoading || isCheckingBackend}
                >
                  Join the System Rebellion
                </button>
              </div>
              
              <div className="auth-login test-user-section" style={{ marginTop: '20px', textAlign: 'center' }}>
                <p style={{ fontSize: '0.9em', color: '#00f5d4' }}>🧐 Sir Hawkington suggests using the test account:</p>
                <button 
                  type="button" 
                  style={{
                    background: 'rgba(0, 245, 212, 0.2)',
                    border: '1px solid #00f5d4',
                    borderRadius: '4px',
                    padding: '8px 12px',
                    color: '#00f5d4',
                    cursor: 'pointer',
                    fontSize: '0.9em',
                    marginTop: '5px'
                  }}
                  onClick={() => {
                    setUsername('testuser');
                    setPassword('password123');
                    updateHawkingtonQuote('welcome');
                  }}
                  disabled={isLoading || isCheckingBackend}
                >
                  Use Test Credentials
                </button>
              </div>

              {/* Debug info */}
              {process.env.NODE_ENV === 'development' && (
                <div className="auth-login debug-info">
                  <div>Auth State: {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</div>
                  <div>Backend Available: {backendAvailable ? 'Yes' : 'No'}</div>
                  <div>CSRF Initialized: {csrfInitialized ? 'Yes' : 'No'}</div>
                  <div>Checking Backend: {isCheckingBackend ? 'Yes' : 'No'}</div>
                </div>
              )}
            </form>
          </div>
        </div>
      </div>

      {isSignupModalOpen && (
        <SignupModal 
          isOpen={isSignupModalOpen} 
          onClose={handleCloseSignup}
        />
      )}
    </>
  );
};

export default Login;