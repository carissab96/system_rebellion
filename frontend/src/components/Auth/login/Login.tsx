import React, { useState, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { login } from '../../../store/slices/authSlice';
import { useNavigate } from 'react-router-dom';
import { initializeCsrf, checkBackendAvailability } from '../../../utils/api';
import SignupModal from '../SignupModal/SignupModal';
import './login.css';

export const Login: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [csrfInitialized, setCsrfInitialized] = useState(false);
  const [backendAvailable, setBackendAvailable] = useState(true);
  const [isCheckingBackend, setIsCheckingBackend] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false);
  const [hawkingtonQuote, setHawkingtonQuote] = useState("🧐 Sir Hawkington welcomes you to the System Rebellion HQ!");

  // Sir Hawkington's distinguished quotes for different scenarios
  const updateHawkingtonQuote = (scenario: 'welcome' | 'error' | 'loading' | 'success') => {
    const quotes = {
      welcome: "🧐 Sir Hawkington welcomes you to the System Rebellion HQ!",
      error: "🧐 *adjusts monocle in concern* I say, something seems amiss!",
      loading: "🧐 *polishes monocle* Let me verify your credentials...",
      success: "🧐 *tips hat* Welcome back, distinguished rebel!"
    };
    setHawkingtonQuote(quotes[scenario]);
  };

  const isLoading = useAppSelector((state: { auth: { loading: any; }; }) => state.auth.loading);
  const isAuthenticated = useAppSelector((state: { auth: { isAuthenticated: any; }; }) => state.auth.isAuthenticated);
  const authError = useAppSelector((state: { auth: { error: any; }; }) => state.auth.error);

  // Check backend availability and initialize CSRF token when component mounts
  useEffect(() => {
    const initializeApp = async () => {
      setIsCheckingBackend(true);
      try {
        // Check if backend is available
        const available = await checkBackendAvailability();
        setBackendAvailable(available);
        
        if (available) {
          // Initialize CSRF token only if backend is available
          // initializeCsrf now returns a boolean indicating success
          const csrfSuccess = await initializeCsrf();
          setCsrfInitialized(csrfSuccess);
          
          if (csrfSuccess) {
            console.log('🍪 CSRF token initialized successfully');
          } else {
            console.error('🚨 CSRF token initialization failed');
            setError('Failed to initialize security tokens. Please try again.');
          }
        } else {
          console.error('🚨 Backend server is not available');
          setError('Cannot connect to the server. Please check your connection and try again.');
        }
      } catch (err) {
        console.error('🚨 Error during initialization:', err);
        setBackendAvailable(false);
        setError('Failed to connect to the server. Please try again later.');
      } finally {
        setIsCheckingBackend(false);
      }
    };

    initializeApp();
  }, [retryCount]);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!backendAvailable) {
      setError('Cannot login: Server is currently unavailable');
      updateHawkingtonQuote('error');
      return;
    }
    
    if (!csrfInitialized) {
      console.warn('🚨 Attempting login before CSRF token is initialized');
      // Try to initialize CSRF again
      try {
        // initializeCsrf now returns a boolean indicating success
        const csrfSuccess = await initializeCsrf();
        setCsrfInitialized(csrfSuccess);
        
        if (!csrfSuccess) {
          setError('Security token initialization failed. Please refresh the page.');
          updateHawkingtonQuote('error');
          return;
        }
      } catch (err) {
        setError('Security token initialization failed. Please refresh the page.');
        updateHawkingtonQuote('error');
        return;
      }
    }
    
    setError(''); // Clear previous errors
    updateHawkingtonQuote('loading');
    
    try {
      console.log('🔐 Submitting login credentials to API...');
      const result = await dispatch(login({ username, password })).unwrap();
      console.log('✅ Login result:', result); // Debug log
      
      if (result && result.data && result.data.access) {
        console.log('🎉 Login successful!');
        updateHawkingtonQuote('success');
        
        // Check if user needs onboarding
        if (result.data.user && result.data.user.needs_onboarding) {
          console.log('🧐 Sir Hawkington notices you need to set up your system...');
          navigate('/onboarding');
        } else {
          console.log('🎩 Sir Hawkington welcomes you back to your dashboard!');
          navigate('/dashboard');
        }
      } else {
        console.error('❌ Login response missing expected data structure');
        setError('Invalid response from server. Please try again.');
        updateHawkingtonQuote('error');
      }
    } catch (err: any) {
      console.error('🚨 Login error:', err); // Debug log
      
      // Check if this is a network error
      if (err.isNetworkError) {
        setBackendAvailable(false);
        setError('Cannot connect to the server. Please check your connection and try again.');
      } else {
        setError(err instanceof Error ? err.message : 'Login failed. Please check your credentials.');
      }
      updateHawkingtonQuote('error');
    }
  };

  // Add effect to handle successful login
  useEffect(() => {
    if (isAuthenticated) {
      console.log('🔄 Auth state changed to authenticated, navigating...');
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  // If backend is not available, show offline message
  if (!backendAvailable && !isCheckingBackend) {
    return (
      <div className="login-container">
        <div className="offline-message">
          <h3>Server Unavailable</h3>
          <p>We're unable to connect to the server at the moment. This could be due to:</p>
          <ul>
            <li>The server is not running</li>
            <li>Network connectivity issues</li>
            <li>Temporary server maintenance</li>
          </ul>
          <p>Please check your connection and try again.</p>
          <button 
            className="retry-button" 
            onClick={handleRetry} 
            disabled={isCheckingBackend}
          >
            {isCheckingBackend ? 'Checking...' : 'Retry Connection'}
          </button>
          
          {/* Debug info */}
          {process.env.NODE_ENV === 'development' && (
            <div className="debug-info">
              <div>Backend Status: Unavailable</div>
              <div>CSRF Initialized: {csrfInitialized ? 'Yes' : 'No'}</div>
              <div>Retry Count: {retryCount}</div>
            </div>
          )}
        </div>
      </div>
    );
  }

  const handleOpenSignup = () => {
    setIsSignupModalOpen(true);
    console.log("🧐 Sir Hawkington prepares to guide a new recruit through registration!");
    console.log("🐌 The Meth Snail vibrates with anticipation!");
  };

  const handleCloseSignup = () => {
    setIsSignupModalOpen(false);
    console.log("🧐 Sir Hawkington adjusts his monocle and returns to login duties.");
  };

  return (
    <div className="login-container">
      <div className="hawkington-welcome">
        <div className="hawkington-icon">🧐</div>
        <p className="hawkington-quote">{hawkingtonQuote}</p>
      </div>

      <form onSubmit={handleSubmit} className="login-form">
        <h2>System Rebellion Login</h2>
        
        {isLoading && <div className="loading">Logging in...</div>}
        {isCheckingBackend && <div className="loading">Checking server connection...</div>}
        {error && <div className="error-message">{error}</div>}
        {authError && <div className="error-message">{authError}</div>}
        
        <div className="form-group">
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
        
        <div className="form-group">
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
          disabled={isLoading || !csrfInitialized || isCheckingBackend || !backendAvailable}
        >
          {isLoading ? 'Sir Hawkington is verifying...' : 'Enter the System Rebellion'}
        </button>

        <div className="signup-prompt">
          <p>Not a member of the System Rebellion yet?</p>
          <button 
            type="button" 
            className="signup-button cosmic-button" 
            onClick={handleOpenSignup}
            disabled={isLoading || isCheckingBackend}
          >
            Join the System Rebellion
          </button>
        </div>

        <SignupModal 
          isOpen={isSignupModalOpen} 
          onClose={handleCloseSignup}
        />

        {/* Debug info */}
        {process.env.NODE_ENV === 'development' && (
          <div className="debug-info">
            <div>Auth State: {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</div>
            <div>Backend Available: {backendAvailable ? 'Yes' : 'No'}</div>
            <div>CSRF Initialized: {csrfInitialized ? 'Yes' : 'No'}</div>
            <div>Checking Backend: {isCheckingBackend ? 'Yes' : 'No'}</div>
          </div>
        )}
      </form>
    </div>
  );
};