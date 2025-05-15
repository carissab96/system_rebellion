import React, { useEffect, useRef, useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Provider as ReduxProvider, useDispatch } from 'react-redux';
import { store, AppDispatch } from './store/store';
import { ToastProvider } from './components/common/Toast';
import { checkBackendAvailability } from './utils/api';
import { initializeCsrf } from './utils/csrf';
import { runDiagnostics } from './utils/diagnostics';
import webSocketService from './utils/websocketService';
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

  // Debug log when component mounts
  console.log('App component mounted');

  // Main initialization effect
  useEffect(() => {
    let isMounted = true;
    console.log('Initialization effect running');

    const initializeApp = async () => {
      try {
        // 1. Check backend availability
        const isAvailable = await checkBackendAvailability();
        if (!isMounted) return;
        
        if (!isAvailable) {
          throw new Error('Backend service is not available. Please check your connection.');
        }

        // 2. Initialize CSRF
        const csrfInitialized = await initializeCsrf();
        if (!csrfInitialized) {
          throw new Error('Failed to initialize security token');
        }

        // 3. Check authentication status
        await dispatch(checkAuthStatus());

        // 4. Run diagnostics (non-blocking)
        runDiagnostics().catch(console.error);

        // 5. Set up WebSocket connection
        try {
          await webSocketService.connect();
        } catch (error) {
          console.warn('WebSocket connection failed:', error);
        }

        // 6. Set up periodic health checks
        const checkBackend = async () => {
          if (!isMounted) return;
          
          try {
            await checkBackendAvailability();
          } catch (error) {
            console.error('Health check failed:', error);
          }
        };

        // Initial check
        await checkBackend();
        
        // Set up interval for periodic checks
        checkIntervalRef.current = window.setInterval(checkBackend, 30000);

      } catch (error) {
        console.error('Initialization error:', error);
        if (isMounted) {
          setInitializationError(error instanceof Error ? error : new Error('Initialization failed'));
        }
      } finally {
        if (isMounted) {
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
      }
      
      // Clean up WebSocket
      webSocketService.disconnect();
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