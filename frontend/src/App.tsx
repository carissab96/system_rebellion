import React, { useEffect, useRef, useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Provider as ReduxProvider, useDispatch } from 'react-redux';
import { store, AppDispatch } from './store/store';
import { ToastProvider } from './components/common/Toast';
import { checkBackendAvailability } from './utils/api';
import { initializeCsrf } from './utils/csrf';
import { runDiagnostics } from './utils/diagnostics';
import { checkAuthStatus } from './store/slices/authSlice';
import './App.css';

// Components
import Login, { LoginProps } from './components/Auth/login/Login';
import Dashboard from './components/dashboard/Dashboard/Dashboard';
import Layout from './components/common/Layout';
import OptimizationProfiles from './components/optimization/OptimizationProfiles';
import SystemAlerts from './components/alerts/SystemAlerts';
import SystemConfiguration from './components/configuration/SystemConfiguration';
import SystemMetrics from './components/metrics/SystemMetrics';
import AutoTunerComponent from './components/auto_tuners/auto_tuner';
import OnboardingPage from './pages/OnboardingPage';
import LandingPage from './pages/LandingPage';
import ProtectedRoute from './utils/ProtectedRoute';
import { DesignSystemShowcase } from './design-system/docs';

// Error Boundary State
type ErrorBoundaryState = {
  hasError: boolean;
  error: Error | null;
};

// Error Boundary Component
class ErrorBoundary extends React.Component<{children: React.ReactNode}, ErrorBoundaryState> {
  state: ErrorBoundaryState = {
    hasError: false,
    error: null
  };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error("Error Boundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message || 'An unknown error occurred'}</p>
          <button onClick={() => window.location.reload()}>Reload Application</button>
        </div>
      );
    }
    return this.props.children;
  }
}

const App: React.FC = () => {
  const cleanupRef = useRef<boolean>(false);
  const checkIntervalRef = useRef<number | null>(null);
  const dispatch = useDispatch<AppDispatch>();
  
  // State
  const [initializationError, setInitializationError] = useState<Error | null>(null);
  const [isInitialized, setIsInitialized] = useState<boolean>(false);

  // Handle manual reconnection
  const handleManualReconnect = useCallback(async () => {
    console.log('Attempting manual reconnection...');
    setInitializationError(null);
    
    try {
      await initializeCsrf();
      await dispatch(checkAuthStatus());
    } catch (error) {
      console.error('Reconnection failed:', error);
      setInitializationError(error instanceof Error ? error : new Error('Reconnection failed'));
    }
  }, [dispatch]);

  // Main initialization effect
  useEffect(() => {
    let isMounted = true;
    console.log('Initialization effect running');

    // Define a timeout wrapper function
    const withTimeout = <T,>(promise: Promise<T>, ms: number, errorMsg: string): Promise<T> => {
      return new Promise<T>((resolve, reject) => {
        const timeoutId = setTimeout(() => {
          reject(new Error(errorMsg));
        }, ms);
        
        promise
          .then(result => {
            clearTimeout(timeoutId);
            resolve(result);
          })
          .catch(error => {
            clearTimeout(timeoutId);
            reject(error);
          });
      });
    };

    const initializeApp = async () => {
      // Overall timeout to ensure we don't get stuck
      const overallTimeoutId = setTimeout(() => {
        if (isMounted) {
          console.log('Force completing initialization due to timeout');
          setInitializationError(new Error('Initialization timed out'));
          setIsInitialized(true); // Force complete even with error
        }
      }, 15000); // 15 seconds total

      try {
        // 1. Check backend availability
        console.log('Checking backend availability...');
        let isAvailable = false;
        try {
          isAvailable = await withTimeout(
            checkBackendAvailability(),
            5000, 
            'Backend availability check timed out'
          );
        } catch (error) {
          console.error('Backend availability check failed:', error);
          throw new Error('Backend service is not available');
        }

        if (!isMounted) return;
        
        if (!isAvailable) {
          throw new Error('Backend service is not available. Please check your connection.');
        }

        // 2. Initialize CSRF
        console.log('Initializing CSRF...');
        let csrfInitialized = false;
        try {
          csrfInitialized = await withTimeout(
            initializeCsrf(),
            5000,
            'CSRF initialization timed out'
          );
        } catch (error) {
          console.error('CSRF initialization failed:', error);
          throw new Error('Failed to initialize security token');
        }
        console.log('Attempting manual CSRF fetch...');
        try {
          fetch('/api/auth/csrf_token', {
            method: 'GET',
            credentials: 'include'
          })
          .then(response => {
            console.log('CSRF fetch response:', response);
            return response.json();
          })
          .then(data => {
            console.log('CSRF data:', data);
          })
          .catch(error => {
            console.error('CSRF fetch error:', error);
          });
          console.log('CSRF fetch initiated');
        } catch (error) {
          console.error('Error setting up CSRF fetch:', error);
        }
        if (!isMounted) return;
        
        if (!csrfInitialized) {
          throw new Error('Failed to initialize security token');
        }

        // 3. Check authentication (non-blocking)
        console.log('Checking authentication status...');
        withTimeout(
          dispatch(checkAuthStatus()),
          5000,
          'Authentication check timed out'
        ).catch(error => {
          console.warn('Authentication check failed (continuing anyway):', error);
        });

        // 4. Run diagnostics (non-blocking)
        console.log('Running diagnostics...');
        runDiagnostics().catch(error => {
          console.warn('Diagnostics failed (continuing anyway):', error);
        });
        
        // 5. Set up backend availability monitoring
        const checkBackend = async () => {
          if (!isMounted) return;
          
          try {
            const isStillAvailable = await checkBackendAvailability();
            if (!isStillAvailable && isMounted) {
              console.error('Backend connection lost');
              setInitializationError(new Error('Lost connection to backend services'));
            }
          } catch (error) {
            if (isMounted) {
              console.error('Backend health check failed:', error);
            }
          }
        };

        // Start periodic checks
        checkIntervalRef.current = window.setInterval(checkBackend, 30000);
        
        console.log('Initialization completed successfully');

      } catch (error) {
        console.error('Initialization error:', error);
        if (isMounted) {
          setInitializationError(error instanceof Error ? error : new Error('Initialization failed'));
        }
      } finally {
        clearTimeout(overallTimeoutId);
        
        // Always set initialized to true to prevent getting stuck
        if (isMounted) {
          console.log('Setting isInitialized to true');
          setIsInitialized(true);
        }
      }
    };

    initializeApp();

    // Cleanup function
    return () => {
      isMounted = false;
      cleanupRef.current = true;
      
      if (checkIntervalRef.current) {
        window.clearInterval(checkIntervalRef.current);
        checkIntervalRef.current = null;
      }
    };
  }, [dispatch]);

  // Loading state
  if (!isInitialized) {
    console.log('App is in loading state');
    return (
      <div className="app-loading" style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#120258',
        color: 'white',
        fontSize: '1.5rem',
        textAlign: 'center',
        padding: '2rem'
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          border: '5px solid #f3f3f3',
          borderTop: '5px solid #3498db',
          borderRadius: '50%',
          animation: 'spin 2s linear infinite',
          marginBottom: '1rem'
        }}></div>
        <p>Initializing application...</p>
        <p style={{ fontSize: '1rem', opacity: 0.8 }}>Please wait while we set things up</p>
        <style>{
          `@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`
        }</style>
      </div>
    );
  }

  // Error state
  if (initializationError) {
    return (
      <div className="error-state">
        <h2>Connection Error</h2>
        <p>{initializationError.message || 'An unknown error occurred'}</p>
        <div className="button-group">
          <button onClick={handleManualReconnect}>Retry Connection</button>
          <button onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      </div>
    );
  }

  // Default login props
  const loginProps: LoginProps = {
    isOpen: true,
    onClose: () => console.log('Login closed')
  };

  // Main app content
  return (
    <ReduxProvider store={store}>
      <ToastProvider>
        <ErrorBoundary>
          <BrowserRouter>
            <Layout>
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<Login {...loginProps} />} />
                
                <Route element={
                  <ProtectedRoute>
                    <Outlet />
                  </ProtectedRoute>
                }>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/optimization" element={<OptimizationProfiles />} />
                  <Route path="/alerts" element={<SystemAlerts />} />
                  <Route path="/configuration" element={<SystemConfiguration />} />
                  <Route path="/metrics" element={<SystemMetrics />} />
                  <Route path="/auto-tuner" element={<AutoTunerComponent />} />
                  <Route path="/onboarding" element={<OnboardingPage />} />
                  <Route path="/design-system" element={<DesignSystemShowcase />} />
                </Route>

                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Layout>
          </BrowserRouter>
        </ErrorBoundary>
      </ToastProvider>
    </ReduxProvider>
  );
};

export default App;