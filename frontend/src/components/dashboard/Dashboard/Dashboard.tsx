import React, { useEffect, useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import './Dashboard.css';
import { UserProfile } from '../UserProfile/UserProfile';
import { CPUMetric } from '../Metrics/CPUMetrics/CPUMetric';
import { MemoryMetric } from '../Metrics/MemoryMetric/MemoryMetric';
import { DiskMetric } from '../Metrics/DiskMetric/DiskMetric';
import { NetworkMetric } from '../Metrics/NetworkMetric/NetworkMetric';
import { initializeWebSocket } from '../../../store/slices/metricsSlice';
import SystemStatus  from './SystemStatus/SystemStatus';


export const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const wsRef = useRef<AbortController | null>(null);
  const error = useAppSelector((state) => state.metrics.error);
  const isLoading = useAppSelector((state) => state.metrics.loading);
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
                console.error("💩 WebSocket initialization fucked up:", error);
                console.log("🐌 The Meth Snail is attempting emergency repairs on the WebSocket connection...");
            }
        }
    };

    initializeWS();

    return () => {
        console.log(`🧹 Dashboard unmounting... (Mount #${mountCountRef.current})`);
        wsRef.current?.abort();
    };
}, [dispatch]);
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
        <h1>System Rebellion HQ</h1>
        <SystemStatus loading={isLoading} error={error} />
      </header>
      <div className="dashboard-content">
        <div className="metrics-row">
          <CPUMetric /> 
          <MemoryMetric />
          <DiskMetric />
          <NetworkMetric />
        </div>

        <div className="controls-section">
          <div className="profile-section">
            <UserProfile />
          </div>

          <div className="optimization-controls">
            <h2>Optimization Controls</h2>
            <div className="control-description">
              Activate the Meth Snail's optimization routines, Sir Hawkington's distinguished system configurations, and keep the Quantum Shadow People away from your router.
            </div>
            <div className="buttons-row">
              <button 
                className="control-button"
                disabled={isLoading || !!error}
                onClick={() => {
                  console.log("🐌 The Meth Snail is powering up the optimization engine...");
                  alert("The Meth Snail is now optimizing your system with the power of methamphetamine! Please wait while it frantically reorganizes your bits.");
                  // In a real implementation, this would dispatch an action to run optimization
                }}
              >
                <span className="button-icon">⚡</span>
                <span className="button-text">Run Optimization</span>
              </button>
              <button 
                className="control-button"
                disabled={isLoading || !!error}
                onClick={() => {
                  console.log("🧐 Sir Hawkington is adjusting his monocle to inspect your system profile...");
                  alert("Sir Hawkington is updating your system profile with distinguished elegance. Your profile shall be most refined!");
                  // In a real implementation, this would open a modal or navigate to profile update page
                }}
              >
                <span className="button-icon">🧐</span>
                <span className="button-text">Update Profile</span>
              </button>
              <button 
                className="control-button"
                disabled={isLoading || !!error}
                onClick={() => {
                  console.log("🪄 The Stick is configuring your anxiety management alerts...");
                  alert("The Stick is now configuring your system alerts. It's not much, but it's honest work.");
                  // In a real implementation, this would open alert configuration modal
                }}
              >
                <span className="button-icon">🔔</span>
                <span className="button-text">Configure Alerts</span>
              </button>
            </div>
          </div>

          <div className="system-alerts">
            <h2>System Alerts</h2>
            {error && (
              <div className="alert error">
                {error}
              </div>
            )}
            {/* More alerts will go here */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;