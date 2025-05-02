import React, { useEffect, useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import './Dashboard.css';
import { initializeWebSocket } from '../../../store/slices/metricsSlice';
import { fetchPatterns } from '../../../store/slices/autoTunerSlice';
import { fetchSystemAlerts } from '../../../store/slices/systemAlertsSlice';
import SystemStatus from './SystemStatus/SystemStatus';
import MetricsPanel from '../MetricsPanel/MetricsPanel';
import SystemAlertsPanel from '../SystemAlertsPanel/SystemAlertsPanel';
import SystemPatternsPanel from '../SystemPatternsPanel/SystemPatternsPanel';

export const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const wsRef = useRef<AbortController | null>(null);
  const error = useAppSelector((state) => state.metrics.error);
  const isLoading = useAppSelector((state) => state.metrics.loading);
  const { user } = useAppSelector((state) => state.auth);
  const mountCountRef = useRef(0);



  useEffect(() => {
    mountCountRef.current += 1;
    console.log(`🎭 Dashboard mounting... (Mount #${mountCountRef.current})`);
    
    if (mountCountRef.current === 2) {
        console.log("⚠️ StrictMode second mount detected, proceeding with initialization");
    }

    wsRef.current = new AbortController();
    const signal = wsRef.current.signal;

    const initializeWS = async () => {
        try {
            if (!signal.aborted) {
                console.log("🚀 Starting WebSocket initialization for live metrics...");
                const result = await dispatch(initializeWebSocket()).unwrap();
                
                if (!signal.aborted && result.status === 'connected') {
                    console.log("✨ WebSocket connected! Sir Hawkington is now receiving live metrics via WebSocket.");
                    console.log("🐹 The Hamsters are monitoring the WebSocket tubes for metric data...");
                    // No need to call fetchSystemMetrics() as we're getting live updates via WebSocket
                }
            }
        } catch (error) {
            if (!signal.aborted) {
                console.error("💩 WebSocket initialization error:", error);
                console.log("🐌 The Meth Snail is attempting emergency repairs on the WebSocket connection...");
            }
        }
    };

    initializeWS();
    
    // Fetch system patterns
    dispatch(fetchPatterns());
    
    // Fetch unread system alerts for the dashboard
    dispatch(fetchSystemAlerts({ skip: 0, limit: 5, is_read: false }));

    return () => {
        if (wsRef.current) {
            console.log("🛑 Aborting WebSocket connection...");
            wsRef.current.abort();
        }
    };
  }, [dispatch]);

  // Display personalized welcome message if user is available
  const getWelcomeMessage = () => {
    if (user) {
      const hour = new Date().getHours();
      const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
      return `${greeting}, ${user.username}!`;
    }
    return "System Dashboard";
  };

  if (isLoading) {
      return <div>Loading your distinguished metrics...</div>;
  }

  if (error) {
      return (
          <div className="error-container">
              <h3>Well, shit...</h3>
              <p>{error}</p>
              <button onClick={() => dispatch(initializeWebSocket())}>
                  Try this shit again
              </button>
          </div>
      );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>{getWelcomeMessage()}</h1>
        <SystemStatus loading={isLoading} error={error} />
      </header>
      <div className="dashboard-content">
        {/* Metrics Panel */}
        <MetricsPanel />

        <div className="controls-section">
          {/* System Alerts Panel */}
          <SystemAlertsPanel maxAlerts={5} showAllLink={true} />

          {/* System Patterns Panel */}
          <SystemPatternsPanel maxPatterns={5} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
