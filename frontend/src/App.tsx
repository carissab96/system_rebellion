import React, { useEffect, useRef, useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './components/Auth/login/Login';
import { Dashboard } from './components/dashboard/Dashboard/Dashboard';
import { PrivateRoute } from './utils/PrivateRoute';
import { websocketService } from './utils/websocketService';
import { initializeCsrf, checkBackendAvailability, getBackendAvailability } from './utils/api';
import { useAppDispatch } from './store/hooks';
import Layout from './components/common/Layout';
import OptimizationProfiles from './components/optimization/OptimizationProfiles';
import SystemAlerts from './components/alerts/SystemAlerts';
import SystemConfiguration from './components/configuration/SystemConfiguration';
import SystemMetrics from './components/metrics/SystemMetrics';
import AutoTunerComponent from './components/auto_tuners/auto_tuner';
import OnboardingPage from './pages/OnboardingPage';
import LandingPage from './pages/LandingPage';
import './App.css';

const App: React.FC = () => {
    const cleanupRef = useRef<boolean>(false);
    // We'll use dispatch in a useEffect to handle auth-related actions when needed
    const dispatch = useAppDispatch();
    
    // Initialize authentication on app startup
    useEffect(() => {
        console.log(' Auth dispatcher ready');
        
        // Check if we have a token in localStorage and set it in the axios headers
        const token = localStorage.getItem('token');
        if (token) {
            console.log(' Found existing auth token, initializing authorization header');
            // Import axios and set the authorization header
            import('axios').then(axios => {
                // Set the token directly on axios defaults
                axios.default.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                console.log(' Authorization header set successfully');
                
                // Make a test request to verify the token is working
                axios.default.get('/api/auth/status/')
                    .then(response => {
                        console.log(' Auth status check successful:', response.data);
                    })
                    .catch(error => {
                        console.error(' Auth status check failed:', error);
                        // If token is invalid, clear it
                        if (error.response?.status === 401) {
                            console.log(' Token appears to be invalid, clearing it');
                            localStorage.removeItem('token');
                            localStorage.removeItem('refreshToken');
                        }
                    });
            });
        } else {
            console.log(' No auth token found in localStorage');
        }
    }, [dispatch]);
    // This state tracks backend availability and is used throughout the component
    const [backendAvailable, setBackendAvailable] = useState<boolean>(true);
    
    // Log backend availability changes
    useEffect(() => {
        console.log(` Backend availability changed: ${backendAvailable ? 'Available' : 'Unavailable'}`);
    }, [backendAvailable]);
    const [showOfflineNotification, setShowOfflineNotification] = useState<boolean>(false);
    const [reconnectAttempts, setReconnectAttempts] = useState<number>(0);
    const MAX_RECONNECT_ATTEMPTS = 3; // Maximum number of reconnection attempts
    const [permanentlyFailed, setPermanentlyFailed] = useState<boolean>(false); // Track if we've given up
    const [isReconnecting, setIsReconnecting] = useState<boolean>(false);
    const checkIntervalRef = useRef<number | null>(null);
    const reconnectTimeoutRef = useRef<number | null>(null);

    // Function to attempt reconnection to the backend
    const attemptReconnect = useCallback(async () => {
        // Don't try to reconnect if we've permanently failed
        if (isReconnecting || permanentlyFailed) return;
        
        // If we've reached the maximum number of attempts, mark as permanently failed
        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            console.error(' Maximum reconnection attempts reached. Giving up.');
            setPermanentlyFailed(true);
            setShowOfflineNotification(true);
            return;
        }
        
        setIsReconnecting(true);
        try {
            console.log(` Attempting to reconnect to backend (attempt ${reconnectAttempts + 1} of ${MAX_RECONNECT_ATTEMPTS})...`);
            const available = await checkBackendAvailability(true); // Force a fresh check
            
            setBackendAvailable(available);
            if (available) {
                // Backend is now available
                console.log(" Initializing CSRF protection...");
                try {
                    await initializeCsrf();
                    console.log(" CSRF token initialized successfully");
                } catch (csrfError) {
                    console.warn(" CSRF token initialization failed, but continuing anyway:", csrfError);
                    // We'll proceed without CSRF token - WebSockets don't need it
                }
                
                setShowOfflineNotification(false);
                setReconnectAttempts(0);
                
                // Try to reconnect WebSocket if needed (regardless of CSRF status)
                if (!websocketService.isConnected()) {
                    console.log(" Attempting to reconnect WebSocket...");
                    try {
                        await websocketService.connect();
                        console.log(" WebSocket reconnected successfully");
                    } catch (wsError) {
                        console.warn(" WebSocket reconnection failed:", wsError);
                        // We'll proceed without WebSocket
                    }
                }
            } else {
                // Backend is still unavailable
                setReconnectAttempts(prev => prev + 1);
                console.log(` Reconnection attempt ${reconnectAttempts + 1} failed. ${MAX_RECONNECT_ATTEMPTS - reconnectAttempts - 1} attempts remaining.`);
                
                // Schedule another reconnection attempt if we haven't reached the maximum
                if (reconnectAttempts + 1 < MAX_RECONNECT_ATTEMPTS) {
                    const nextDelay = Math.min(2000 * Math.pow(2, reconnectAttempts), 30000); // Exponential backoff with max of 30 seconds
                    console.log(` Scheduling next reconnection attempt in ${nextDelay / 1000} seconds...`);
                    
                    if (reconnectTimeoutRef.current) {
                        window.clearTimeout(reconnectTimeoutRef.current);
                    }
                    
                    reconnectTimeoutRef.current = window.setTimeout(() => {
                        attemptReconnect();
                    }, nextDelay);
                } else {
                    console.error(' All reconnection attempts failed. Giving up.');
                    setPermanentlyFailed(true);
                }
            }
        } catch (error) {
            console.error(' Error during reconnection attempt:', error);
            setReconnectAttempts(prev => prev + 1);
        } finally {
            setIsReconnecting(false);
        }
    }, [isReconnecting, permanentlyFailed, reconnectAttempts, MAX_RECONNECT_ATTEMPTS]);
    
    // Initialize CSRF token and check backend availability when app loads
    const initializeApp = useCallback(async () => {
        try {
            console.log(" Checking backend availability...");
            const available = await checkBackendAvailability();
            setBackendAvailable(available);
            
            if (available) {
                console.log(" Backend is available. Initializing CSRF protection...");
                try {
                    await initializeCsrf();
                    console.log(" CSRF token initialized successfully");
                } catch (csrfError) {
                    console.warn(" CSRF token initialization failed:", csrfError);
                    // We'll proceed without CSRF token
                }
                
                // Initialize WebSocket connection
                console.log(" Initializing WebSocket connection...");
                try {
                    await websocketService.connect();
                    console.log(" WebSocket connected successfully");
                } catch (wsError) {
                    console.warn(" WebSocket connection failed:", wsError);
                    // We'll proceed without WebSocket
                }
            } else {
                console.warn(" Backend is not available. Some features may be limited.");
                setShowOfflineNotification(true);
            }
        } catch (error) {
            console.error(" Error during app initialization:", error);
            setBackendAvailable(false);
            setShowOfflineNotification(true);
        }
    }, []);
    
    // Set up periodic backend availability check
    const setupBackendCheck = useCallback(() => {
        if (checkIntervalRef.current) {
            window.clearInterval(checkIntervalRef.current);
        }
        
        // Check backend availability every 30 seconds
        checkIntervalRef.current = window.setInterval(async () => {
            if (cleanupRef.current) return; // Don't run if component is unmounting
            
            try {
                // Only check if we're not already trying to reconnect
                if (!isReconnecting && !permanentlyFailed) {
                    const wasAvailable = backendAvailable;
                    const isAvailable = await getBackendAvailability(); // Use cached value if available
                    
                    if (wasAvailable && !isAvailable) {
                        // Backend just went offline
                        console.warn(" Backend connection lost!");
                        setBackendAvailable(false);
                        setShowOfflineNotification(true);
                        
                        // Attempt to reconnect immediately
                        attemptReconnect();
                    } else if (!wasAvailable && isAvailable) {
                        // Backend just came back online
                        console.log(" Backend connection restored!");
                        setBackendAvailable(true);
                        setShowOfflineNotification(false);
                        setReconnectAttempts(0);
                        setPermanentlyFailed(false);
                        
                        // Re-initialize CSRF and WebSocket
                        initializeApp();
                    }
                }
            } catch (error) {
                console.error(" Error during backend availability check:", error);
            }
        }, 30000);
        
        return () => {
            if (checkIntervalRef.current) {
                window.clearInterval(checkIntervalRef.current);
            }
        };
    }, [backendAvailable, isReconnecting, permanentlyFailed, attemptReconnect, initializeApp]);
    
    // Initialize app on mount
    useEffect(() => {
        initializeApp();
        const cleanup = setupBackendCheck();
        
        return () => {
            cleanupRef.current = true;
            cleanup();
            
            if (reconnectTimeoutRef.current) {
                window.clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [initializeApp, setupBackendCheck]);
    
    return (
        <BrowserRouter>
            {showOfflineNotification && (
                <div className="offline-notification">
                    {permanentlyFailed ? (
                        <>
                            <span> Server connection failed. Please check your network or server status.</span>
                            <button 
                                onClick={() => window.location.reload()}
                                className="refresh-button"
                            >
                                Refresh Page
                            </button>
                        </>
                    ) : (
                        <>
                            <span> Server connection lost. Some features may be unavailable.</span>
                            <button 
                                disabled={isReconnecting}
                                onClick={attemptReconnect}
                                className={isReconnecting ? 'reconnecting' : ''}
                            >
                                {isReconnecting ? 'Reconnecting...' : 'Retry Connection'}
                            </button>
                            {reconnectAttempts > 0 && (
                                <span className="reconnect-attempts">
                                    {reconnectAttempts >= MAX_RECONNECT_ATTEMPTS - 1 
                                        ? 'Multiple reconnection attempts failed. Please check your network or server status.' 
                                        : `Reconnection attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}`}
                                </span>
                            )}
                        </>
                    )}
                </div>
            )}
            <Routes>
                {/* Landing page route - outside of Layout */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={
                    <Login 
                        isOpen={true}
                        onClose={() => console.log('Login closed')} 
                    />
                } />
                
                {/* All other routes wrapped in Layout */}
                <Route path="/*" element={
                    <Layout>
                        <Routes>
                            <Route 
                                path="dashboard" 
                                element={
                                    <PrivateRoute>
                                        <Dashboard />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="onboarding" 
                                element={
                                    <PrivateRoute>
                                        <OnboardingPage />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="auto-tuners" 
                                element={
                                    <PrivateRoute>
                                        <AutoTunerComponent />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="system-metrics" 
                                element={
                                    <PrivateRoute>
                                        <SystemMetrics />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="optimizations" 
                                element={
                                    <PrivateRoute>
                                        <OptimizationProfiles />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="system-alerts" 
                                element={
                                    <PrivateRoute>
                                        <SystemAlerts />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="system-configuration" 
                                element={
                                    <PrivateRoute>
                                        <SystemConfiguration />
                                    </PrivateRoute>
                                } 
                            />
                        </Routes>
                    </Layout>
                } />
            </Routes>
        </BrowserRouter>
    );
};

export default App;
