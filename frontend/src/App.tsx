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
    
    // Log auth status on mount for debugging purposes
    useEffect(() => {
        console.log(' Auth dispatcher ready');
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
                    console.log(" Reconnecting WebSocket service (CSRF status independent)...");
                    try {
                        await websocketService.connect();
                        websocketService.resetReconnectAttempts();
                        console.log(" WebSocket reconnected successfully");
                    } catch (wsError) {
                        console.warn(" WebSocket reconnection failed, will retry later");
                    }
                }
            } else {
                // Backend is still unavailable
                console.error(" Backend server is still not available");
                setShowOfflineNotification(true);
                setReconnectAttempts(prev => prev + 1);
                
                // Schedule another reconnection attempt with exponential backoff
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS - 1) { // Limit to MAX_RECONNECT_ATTEMPTS
                    const delay = Math.min(30000, 1000 * Math.pow(2, reconnectAttempts)); // Max 30 seconds
                    console.log(` Scheduling next reconnection attempt in ${delay/1000} seconds`);
                    
                    if (reconnectTimeoutRef.current) {
                        window.clearTimeout(reconnectTimeoutRef.current);
                    }
                    
                    reconnectTimeoutRef.current = window.setTimeout(() => {
                        attemptReconnect();
                    }, delay);
                }
            }
        } catch (error) {
            console.error(" Reconnection attempt failed:", error);
            setBackendAvailable(false);
            setShowOfflineNotification(true);
            setReconnectAttempts(prev => prev + 1);
        } finally {
            setIsReconnecting(false);
        }
    }, [reconnectAttempts, isReconnecting, permanentlyFailed, MAX_RECONNECT_ATTEMPTS]);
    
    useEffect(() => {
        cleanupRef.current = false;

        // Initialize CSRF token and check backend availability when app loads
        const initializeApp = async () => {
            try {
                console.log(" Checking backend availability...");
                const available = await checkBackendAvailability(true);
                setBackendAvailable(available);
                
                if (available) {
                    // Try to initialize CSRF protection, but continue even if it fails
                    console.log(" Initializing CSRF protection...");
                    try {
                        await initializeCsrf();
                        console.log(" CSRF token initialized successfully");
                    } catch (csrfError) {
                        console.warn(" CSRF token initialization failed, but continuing anyway:", csrfError);
                        // We'll proceed without CSRF token - WebSockets don't need it
                    }
                    
                    // Initialize WebSocket connection regardless of CSRF status
                    try {
                        console.log(" Connecting WebSocket (CSRF status independent)...");
                        await websocketService.connect();
                        console.log(" WebSocket connected successfully on app initialization");
                    } catch (wsError) {
                        console.warn(" Initial WebSocket connection failed, will retry later", wsError);
                    }
                } else {
                    console.error(" Backend server is not available");
                    setShowOfflineNotification(true);
                    // Schedule a reconnection attempt
                    attemptReconnect();
                }
            } catch (error) {
                console.error(" Failed to initialize application:", error);
                setBackendAvailable(false);
                setShowOfflineNotification(true);
                // Schedule a reconnection attempt
                attemptReconnect();
            }
        };

        // Set up periodic backend availability check
        const setupBackendCheck = () => {
            // Don't set up checks if we've permanently failed
            if (permanentlyFailed) {
                console.log(' Not setting up backend checks - system is permanently offline');
                return null;
            }
            
            // Check every 30 seconds
            const intervalId = window.setInterval(async () => {
                if (cleanupRef.current) return;
                
                try {
                    const wasAvailable = getBackendAvailability();
                    const isNowAvailable = await checkBackendAvailability();
                    
                    // Update state only if availability changed
                    if (wasAvailable !== isNowAvailable) {
                        setBackendAvailable(isNowAvailable);
                        
                        if (isNowAvailable) {
                            // Backend is now available, try to initialize CSRF and reconnect
                            attemptReconnect();
                        } else {
                            // Backend is now unavailable
                            console.error(" Backend became unavailable");
                            setShowOfflineNotification(true);
                            
                            // Reset reconnect attempts since this is a new disconnection
                            setReconnectAttempts(0);
                        }
                    }
                    
                    // Check WebSocket connection status regardless of backend availability
                    if (isNowAvailable && !websocketService.isConnected()) {
                        console.log(" WebSocket disconnected but backend available, attempting reconnection...");
                        try {
                            await websocketService.connect();
                            console.log(" WebSocket reconnected successfully during periodic check");
                        } catch (wsError) {
                            console.warn(" WebSocket reconnection failed during periodic check");
                        }
                    }
                } catch (error) {
                    console.error(" Error checking backend availability:", error);
                }
            }, 30000); // 30 seconds
            
            checkIntervalRef.current = intervalId;
            return intervalId;
        };

        initializeApp();
        setupBackendCheck(); // Sets up interval for checking backend availability

        return () => {
            cleanupRef.current = true;
            console.log(" App unmounting...");
            
            // Clear all timers
            if (checkIntervalRef.current) {
                window.clearInterval(checkIntervalRef.current);
                checkIntervalRef.current = null;
            }
            
            if (reconnectTimeoutRef.current) {
                window.clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = null;
            }
            
            const cleanup = () => {
                if (cleanupRef.current) {
                    console.log(" Performing final cleanup...");
                    if (websocketService.isConnected()) {
                        console.log(" Disconnecting established connection...");
                        websocketService.disconnect();
                    } else {
                        console.log(" No active connection to disconnect");
                    }
                }
            };

            setTimeout(cleanup, 100);
        };
    }, [attemptReconnect]);

    return (
        <BrowserRouter>
            {showOfflineNotification && (
                <div className="offline-notification">
                    {permanentlyFailed ? (
                        <>
                            <span> Server connection permanently failed. Please refresh the page to try again.</span>
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
            <Layout>
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/login" element={
                      <Login 
                        isOpen={true}
                        onClose={() => console.log('Login closed')} 
                      />
                    } />
                    <Route 
                        path="/dashboard" 
                        element={
                            <PrivateRoute>
                                <Dashboard />
                            </PrivateRoute>
                        } 
                    />
                    <Route 
                        path="/onboarding" 
                        element={
                            <PrivateRoute>
                                <OnboardingPage />
                            </PrivateRoute>
                        } 
                    />
                    <Route 
                        path="/auto-tuners" 
                        element={
                            <PrivateRoute>
                                <AutoTunerComponent />
                            </PrivateRoute>
                        } 
                    />
                    <Route 
                        path="/system-metrics" 
                        element={
                            <PrivateRoute>
                                <SystemMetrics />
                            </PrivateRoute>
                        } 
                    />
                    <Route 
                        path="/optimizations" 
                        element={
                            <PrivateRoute>
                                <OptimizationProfiles />
                            </PrivateRoute>
                        } 
                    />
                    <Route 
                        path="/system-alerts" 
                        element={
                            <PrivateRoute>
                                <SystemAlerts />
                            </PrivateRoute>
                        } 
                    />
                    <Route 
                        path="/system-configuration" 
                        element={
                            <PrivateRoute>
                                <SystemConfiguration />
                            </PrivateRoute>
                        } 
                    />
                </Routes>
            </Layout>
        </BrowserRouter>
    );
};

export default App;