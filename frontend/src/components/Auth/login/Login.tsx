import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { login } from '../../../store/slices/authSlice';
import { useNavigate } from 'react-router-dom';
import { initializeCsrf, checkBackendAvailability } from '../../../utils/api';
import SignupModal from '../SignupModal/SignupModal';
import './login.css';
import { useState, useEffect } from 'react';
import '../../../common/Modal.css';

interface LoginProps {
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

  const isLoading = useAppSelector((state: { auth: { loading: any; }; }) => state.auth.loading);
  const isAuthenticated = useAppSelector((state: { auth: { isAuthenticated: any; }; }) => state.auth.isAuthenticated);
  const authError = useAppSelector((state: { auth: { error: any; }; }) => state.auth.error);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log("Login attempt with:", { username, password: "***" });

    if (!backendAvailable) {
      console.log("Backend not available, aborting login");
      setError('Cannot login: Server is currently unavailable');
      updateHawkingtonQuote('error');
      return;
    }
    
    if (!csrfInitialized) {
      const csrfSuccess = await initializeCsrf();
      setCsrfInitialized(csrfSuccess);
      
      if (!csrfSuccess) {
        setError('Security token initialization failed. Please refresh the page.');
        return;
      }
    }

    try {
      console.log("Dispatching login action");
      const result = await dispatch(login({ username, password })).unwrap();
      console.log("Login successful", result);
      navigate('/dashboard');
    } catch (err) {
      console.error("Login failed", err);
      setError('Login failed. Please check your credentials and try again.');
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
      <div className="auth-login modal">
        <div className="auth-login modal-overlay" onClick={onClose}></div>
        <div className="auth-login modal-content">
          <button className="auth-login close-button" onClick={onClose}>×</button>
          <div className="auth-login modal-header">
            <h2>System Rebellion Login</h2>
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