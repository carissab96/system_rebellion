import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import './Dashboard.css';
import { fetchPatterns } from '../../../store/slices/autoTunerSlice';
import { fetchSystemAlerts } from '../../../store/slices/systemAlertsSlice';
import useMetricsWebSocket from '../../../services/websocket/useMetricsWebSocket'; // Restore this import
import { RootState } from '../../../store/store';
import SystemStatus from './SystemStatus/SystemStatus';
import MetricsPanel from '../MetricsPanel/MetricsPanel';
import SystemAlertsPanel from '../SystemAlertsPanel/SystemAlertsPanel';
import SystemPatternsPanel from '../SystemPatternsPanel/SystemPatternsPanel';

interface DashboardProps {}

export const Dashboard: React.FC<DashboardProps> = () => {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { status, error } = useAppSelector(
    (state: RootState) => state.metrics
  );
  const loading = status ==='connecting';

  // IMPORTANT: Restore this hook to ensure WebSocket connection is established
  useMetricsWebSocket();
  
  // Fetch initial data
  useEffect(() => {
    console.log("🚀 Initializing Dashboard...");
    
    // Fetch initial data
    dispatch(fetchPatterns() as any);
    dispatch(fetchSystemAlerts({ skip: 0, limit: 20 }));
    
    return () => {
      console.log("🧹 Cleaning up Dashboard resources...");
    };
  }, [dispatch]);

  // Display personalized welcome message if user is available
  const getWelcomeMessage = () => {
    if (user?.username) {
      const hour = new Date().getHours();
      const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
      return `${greeting}, ${user.username}!`;
    }
    return "System Dashboard";
  };

  // Show loading state
  if (status === 'connecting' || status === 'disconnected') {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="error-container">
        <h2>⚠️ Connection Error</h2>
        <p>{error}</p>
        <button 
          className="retry-button"
          onClick={() => window.location.reload()}
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>{getWelcomeMessage()}</h1>
        
        <div className="ticker-container">
          <SystemStatus loading={loading} error={error} />
        </div>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-main">
          <MetricsPanel />
        </div>
        <div className="dashboard-sidebar">
          <SystemAlertsPanel maxAlerts={5} showAllLink={true} />
          <SystemPatternsPanel maxPatterns={5} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;