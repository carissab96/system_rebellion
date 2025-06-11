import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { Link } from 'react-router-dom';
import './DashboardNew.css';
import { fetchPatterns } from '../../../store/slices/autoTunerSlice';
import { fetchSystemAlerts } from '../../../store/slices/systemAlertsSlice';
import useMetricsWebSocket from '../../../services/websocket/useMetricsWebSocket';
import { RootState } from '../../../store/store';
import SystemStatus from './SystemStatus/SystemStatus';
import CPUMetric from '../../../components/metrics/CPU/CPUMetric';
import MemoryMetric from '../../../components/metrics/memory/MemoryMetric';
import DiskMetric from '../../../components/metrics/disk/DiskMetric';
import NetworkMetric from '../../../components/metrics/Network/NetworkMetric';
import SystemAlertsPanel from '../SystemAlertsPanel/SystemAlertsPanel';
import SystemPatternsPanel from '../SystemPatternsPanel/SystemPatternsPanel';

interface DashboardProps {}

export const DashboardNew: React.FC<DashboardProps> = () => {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { status, error } = useAppSelector(
    (state: RootState) => state.metrics
  );
  const loading = status === 'connecting';

  // Establish WebSocket connection and get controls
  const webSocketControls = useMetricsWebSocket();
  
  // Fetch initial data
  useEffect(() => {
    console.log("🚀 Initializing Dashboard...");
    
    dispatch(fetchPatterns() as any);
    dispatch(fetchSystemAlerts({ skip: 0, limit: 5 }));
    
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

  // Get metrics data to check if we have any metrics loaded
  const cpuMetrics = useAppSelector(state => state.cpu.current);
  const memoryMetrics = useAppSelector(state => state.memory.current);
  const diskMetrics = useAppSelector(state => state.disk.current);
  const networkMetrics = useAppSelector(state => state.network.current);
  
  // Check if we have any metrics data
  const hasMetricsData = cpuMetrics || memoryMetrics || diskMetrics || networkMetrics;
  
  // Log metrics state for debugging
  useEffect(() => {
    console.log('Dashboard metrics state:', { 
      status, 
      hasMetricsData,
      cpuMetrics, 
      memoryMetrics, 
      diskMetrics, 
      networkMetrics 
    });
  }, [status, cpuMetrics, memoryMetrics, diskMetrics, networkMetrics]);
  
  // Only show loading state if we're connecting AND have no metrics data
  if ((status === 'connecting' || status === 'disconnected') && !hasMetricsData) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dashboard metrics...</p>
      </div>
    );
  }

  // Use the webSocketControls initialized above
  
  // Show error state
  if (error) {
    return (
      <div className="error-container">
        <h2>⚠️ Connection Error</h2>
        <p>{error}</p>
        <div className="error-actions">
          <button 
            className="retry-button"
            onClick={() => {
              console.log('Resetting circuit breaker and reconnecting...');
              webSocketControls.resetCircuitBreaker();
            }}
          >
            Reset Circuit Breaker & Reconnect
          </button>
          <button 
            className="retry-button secondary"
            onClick={() => window.location.reload()}
          >
            Reload Page
          </button>
        </div>
        <p className="error-help-text">If the circuit breaker is open, try resetting it first.</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>{getWelcomeMessage()}</h1>
        <SystemStatus loading={loading} error={error} />
      </div>
      
      <div className="dashboard-metrics">
        <div className="metrics-header">
          <h2>System Metrics</h2>
          <Link to="/metrics" className="section-link" replace>View All Metrics</Link>
        </div>
        
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-card-header">
              <h3>CPU Usage</h3>
              <Link to="/metrics" state={{ section: 'cpu' }} className="metric-link" replace>Details</Link>
            </div>
            <CPUMetric />
          </div>
          
          <div className="metric-card">
            <div className="metric-card-header">
              <h3>Memory Usage</h3>
              <Link to="/metrics" state={{ section: 'memory' }} className="metric-link" replace>Details</Link>
            </div>
            <MemoryMetric />
          </div>
          
          <div className="metric-card">
            <div className="metric-card-header">
              <h3>Disk Usage</h3>
              <Link to="/metrics" state={{ section: 'disk' }} className="metric-link" replace>Details</Link>
            </div>
            <DiskMetric />
          </div>
          
          <div className="metric-card">
            <div className="metric-card-header">
              <h3>Network Traffic</h3>
              <Link to="/metrics" state={{ section: 'network' }} className="metric-link" replace>Details</Link>
            </div>
            <NetworkMetric />
          </div>
        </div>
      </div>
      
      <div className="sidebar-panel alerts-panel">
        <div className="panel-header">
          <h2>System Alerts</h2>
          <Link to="/alerts" className="section-link" replace>View All Alerts</Link>
        </div>
        <SystemAlertsPanel maxAlerts={5} showAllLink={false} />
      </div>
      
      <div className="sidebar-panel patterns-panel">
        <div className="panel-header">
          <h2>System Patterns</h2>
          <Link to="/auto-tuner" className="section-link" replace>View All Patterns</Link>
        </div>
        <SystemPatternsPanel maxPatterns={5} />
      </div>
    </div>
  );
};

export default DashboardNew;
