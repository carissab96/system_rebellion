import React, { useEffect, useRef, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import './Dashboard.css';
import { CPUMetric } from '../Metrics/CPUMetrics/CPUMetric';
import { MemoryMetric } from '../Metrics/MemoryMetric/MemoryMetric';
import { DiskMetric } from '../Metrics/DiskMetric/DiskMetric';
import { NetworkMetric } from '../Metrics/NetworkMetric/NetworkMetric';
import { initializeWebSocket } from '../../../store/slices/metricsSlice';
import { fetchPatterns } from '../../../store/slices/autoTunerSlice';
import SystemStatus from './SystemStatus/SystemStatus';

export const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const wsRef = useRef<AbortController | null>(null);
  const error = useAppSelector((state) => state.metrics.error);
  const isLoading = useAppSelector((state) => state.metrics.loading);
  const { user } = useAppSelector((state) => state.auth);
  const metrics = useAppSelector((state) => state.metrics.current);
  const patterns = useAppSelector((state) => state.autoTuner.patterns);
  const patternsStatus = useAppSelector((state) => state.autoTuner.status);
  const mountCountRef = useRef(0);
  
  // State for data update animations
  const [isUpdating, setIsUpdating] = useState(false);
  const prevMetricsRef = useRef(metrics);

  // Effect for data update animations
  useEffect(() => {
    if (metrics && prevMetricsRef.current && JSON.stringify(metrics) !== JSON.stringify(prevMetricsRef.current)) {
      setIsUpdating(true);
      const timer = setTimeout(() => setIsUpdating(false), 1000);
      return () => clearTimeout(timer);
    }
    prevMetricsRef.current = metrics;
  }, [metrics]);

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

    return () => {
        console.log(`🧹 Dashboard unmounting... (Mount #${mountCountRef.current})`);
        wsRef.current?.abort();
    };
  }, [dispatch]);

  // Display personalized welcome message if user is available
  const getWelcomeMessage = () => {
    if (user && user.username) {
      return `Welcome back, ${user.username}!`;
    }
    return "System Rebellion HQ";
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
      <div className={`dashboard-content ${isUpdating ? 'data-updating' : ''}`}>
        <div className="metrics-row">
          <CPUMetric /> 
          <MemoryMetric />
          <DiskMetric />
          <NetworkMetric />
        </div>

        <div className="controls-section">
          <div className="system-alerts">
            <h2>System Alerts</h2>
            {error && (
              <div className="alert error">
                {error}
              </div>
            )}
            {/* More alerts will go here */}
          </div>

          <div className="system-patterns">
            <h2>Detected System Patterns</h2>
            {patternsStatus === 'loading' ? (
              <div className="patterns-loading">Loading patterns...</div>
            ) : !patterns || patterns.length === 0 ? (
              <div className="patterns-empty">No patterns detected</div>
            ) : (
              <div className="patterns-list">
                {patterns.map((pattern, index) => (
                  <div key={index} className="pattern-card">
                    <div className="pattern-header">
                      <h3>{pattern.type}</h3>
                      <div className="pattern-confidence">
                        Confidence: {(pattern.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="pattern-details">
                      <div className="pattern-description">{pattern.pattern}</div>
                      <div className="pattern-info">
                        {Object.entries(pattern.details).map(([key, value]) => (
                          <div key={key} className="pattern-detail-item">
                            <span className="detail-key">{key}:</span> {JSON.stringify(value)}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
