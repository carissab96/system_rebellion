import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { useToast } from '../../../components/common/Toast';
import './Dashboard.css';
import { fetchPatterns } from '../../../store/slices/autoTunerSlice';
import { fetchSystemAlerts } from '../../../store/slices/systemAlertsSlice';
import { initializeWebSocket } from '../../../store/slices/metricsSlice';
import { RootState } from '../../../store/store';
import SystemStatus from './SystemStatus/SystemStatus';
import MetricsPanel from '../MetricsPanel/MetricsPanel';
import SystemAlertsPanel from '../SystemAlertsPanel/SystemAlertsPanel';
import SystemPatternsPanel from '../SystemPatternsPanel/SystemPatternsPanel';

interface DashboardProps {}

export const Dashboard: React.FC<DashboardProps> = () => {
  const dispatch = useAppDispatch();
  const toast = useToast();
  const { user } = useAppSelector((state) => state.auth);
  const { loading, error, useWebSocket, connectionStatus } = useAppSelector((state: RootState) => state.metrics);
  
  // Initialize WebSocket and fetch initial data
  useEffect(() => {
    console.log("🚀 Initializing Dashboard...");
    
    // Initialize WebSocket connection
    dispatch(initializeWebSocket() as any);
    
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
  if (loading) {
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
  
  // Show connection status
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'status-connected';
      case 'connecting':
        return 'status-connecting';
      case 'disconnected':
        return 'status-disconnected';
      default:
        return 'status-disconnected';
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>{getWelcomeMessage()}</h1>
          <p className="connection-status">
            Status: <span className={getStatusColor(connectionStatus)}>
              {connectionStatus.toUpperCase()}
            </span>
            {useWebSocket ? ' (WebSocket)' : ' (REST API)'}
          </p>
        </div>
        <div className="dashboard-actions">
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
