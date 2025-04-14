import React, { useEffect, useRef, useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './components/Auth/login/Login';
import { Dashboard } from './components/dashboard/Dashboard/Dashboard';
import { PrivateRoute } from './utils/PrivateRoute';
import { websocketService } from './utils/websocketService';
import { checkBackendAvailability, getBackendAvailability } from './utils/api';
import { useAppDispatch } from './store/hooks';
import { checkAuthStatus } from './store/slices/authSlice';
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
    const dispatch = useAppDispatch();
    // We don't need to use these variables directly as they're handled by the PrivateRoute component
    // but we do need to dispatch checkAuthStatus
    
    // Initialize authentication on app startup
    useEffect(() => {
        console.log('Initializing authentication status');
        dispatch(checkAuthStatus());
    }, [dispatch]);
    
    // This state tracks backend availability and is used throughout the component
    const [backendAvailable, setBackendAvailable] = useState<boolean>(true);
    
    // Log backend availability changes
    useEffect(() => {
        console.log(`Backend availability changed: ${backendAvailable ? 'Available' : 'Unavailable'}`);
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
        // Don't try to reconnect if we've already reconnecting or permanently failed
        if (isReconnecting || permanentlyFailed) return;
        
        setIsReconnecting(true);
        console.log(`Attempting to reconnect to backend (attempt ${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
        
        try {
            const available = await checkBackendAvailability();
            console.log(`Reconnection check result: ${available ? 'Success' : 'Failed'}`);
            
            if (available) {
                // Backend is back online
                setBackendAvailable(true);
                setShowOfflineNotification(false);
                setReconnectAttempts(0);
                setPermanentlyFailed(false);
                
                // Re-check auth status when backend becomes available
                dispatch(checkAuthStatus());
                
                // Restart websocket connection if needed
                websocketService.connect();
            } else {
                // Backend is still offline
                const newAttempts = reconnectAttempts + 1;
                setReconnectAttempts(newAttempts);
                
                if (newAttempts >= MAX_RECONNECT_ATTEMPTS) {
                    console.log('Maximum reconnection attempts reached. Giving up automatic reconnection.');
                    setPermanentlyFailed(true);
                } else {
                    // Schedule another reconnection attempt
                    if (reconnectTimeoutRef.current) {
                        window.clearTimeout(reconnectTimeoutRef.current);
                    }
                    reconnectTimeoutRef.current = window.setTimeout(() => {
                        attemptReconnect();
                    }, 5000); // Try again in 5 seconds
                }
            }
        } catch (error) {
            console.error('Error during reconnection attempt:', error);
            const newAttempts = reconnectAttempts + 1;
            setReconnectAttempts(newAttempts);
            
            if (newAttempts >= MAX_RECONNECT_ATTEMPTS) {
                console.log('Maximum reconnection attempts reached. Giving up automatic reconnection.');
                setPermanentlyFailed(true);
            }
        } finally {
            setIsReconnecting(false);
        }
    }, [reconnectAttempts, isReconnecting, permanentlyFailed, dispatch]);

    // Initialize backend availability check
    useEffect(() => {
        const checkBackend = async () => {
            try {
                const available = await getBackendAvailability();
                if (backendAvailable !== available) {
                    console.log(`Backend availability changed to: ${available ? 'Available' : 'Unavailable'}`);
                    setBackendAvailable(available);
                    
                    if (!available) {
                        // Backend just went offline
                        setShowOfflineNotification(true);
                        attemptReconnect();
                    } else {
                        // Backend just came back online
                        setShowOfflineNotification(false);
                        setReconnectAttempts(0);
                        setPermanentlyFailed(false);
                        
                        // Re-check auth status when backend becomes available
                        dispatch(checkAuthStatus());
                    }
                }
            } catch (error) {
                console.error('Error checking backend availability:', error);
                if (backendAvailable) {
                    // If we were previously online, now we're offline
                    setBackendAvailable(false);
                    setShowOfflineNotification(true);
                    attemptReconnect();
                }
            }
        };
        
        // Initial check
        checkBackend();
        
        // Set up periodic checking
        if (checkIntervalRef.current === null) {
            checkIntervalRef.current = window.setInterval(checkBackend, 30000); // Check every 30 seconds
        }
        
        // Initialize websocket connection if backend is available
        if (backendAvailable) {
            websocketService.connect();
        }
        
        // Cleanup function
        return () => {
            cleanupRef.current = true;
            
            // Clear any pending timeouts/intervals
            if (checkIntervalRef.current) {
                window.clearInterval(checkIntervalRef.current);
                checkIntervalRef.current = null;
            }
            
            if (reconnectTimeoutRef.current) {
                window.clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = null;
            }
            
            // Disconnect websocket
            websocketService.disconnect();
        };
    }, [backendAvailable, attemptReconnect, dispatch]);

    // Handle manual reconnection attempt
    const handleManualReconnect = () => {
        console.log('Manual reconnection attempt initiated by user');
        setReconnectAttempts(0);
        setPermanentlyFailed(false);
        attemptReconnect();
    };

    return (
        <BrowserRouter>
            {/* Backend offline notification */}
            {showOfflineNotification && (
                <div className="backend-offline-notification">
                    <div className="offline-content">
                        <div className="offline-icon">🔌</div>
                        <div className="offline-message">
                            <h3>Backend Connection Lost</h3>
                            <p>We're having trouble connecting to the System Rebellion backend services.</p>
                            {permanentlyFailed ? (
                                <p className="offline-help">
                                    Please check your network connection and ensure the backend server is running.
                                </p>
                            ) : (
                                <p className="offline-help">
                                    Attempting to reconnect automatically...
                                </p>
                            )}
                        </div>
                        {permanentlyFailed && (
                            <>
                                <button 
                                    className={`reconnect-button ${isReconnecting ? 'reconnecting' : ''}`} 
                                    onClick={handleManualReconnect}
                                    disabled={isReconnecting}
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
