// Import our beautiful new styles
import '../../../styles/index.css';

import React, { useEffect } from 'react';

import {
  Link,
  useNavigate,
} from 'react-router-dom';

import useMetricsWebSocket
  from '../../../services/websocket/useMetricsWebSocket';
import {
  useAppDispatch,
  useAppSelector,
} from '../../../store/hooks';
import { fetchPatterns } from '../../../store/slices/autoTunerSlice';
import { fetchSystemAlerts } from '../../../store/slices/systemAlertsSlice';
import { RootState } from '../../../store/store';
import WebSocketTest from '../../WebSocketTest';
import SystemAlertsPanel from '../system-alerts-panel/SystemAlertsPanel';
import SystemPatternsPanel from '../system-patterns-panel/SystemPatternsPanel';
import { DashboardMetricWrapper } from './DashboardMetricWrapper';
import SystemStatus from './system-status/SystemStatus';

interface DashboardProps { }

export const DashboardNew: React.FC<DashboardProps> = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const { status, error } = useAppSelector((state: RootState) => state.metrics);
  const loading = status === 'connecting';
  const webSocketControls = useMetricsWebSocket();

  // Fetch initial data
  useEffect(() => {
    console.log("🚀 Initializing Dashboard with new architecture...");
    dispatch(fetchPatterns() as any);
    dispatch(fetchSystemAlerts({ skip: 0, limit: 5 }));

    return () => {
      console.log("🧹 Cleaning up Dashboard resources...");
    };
  }, [dispatch]);

  const getWelcomeMessage = () => {
    if (user?.username) {
      const hour = new Date().getHours();
      const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
      return `${greeting}, ${user.username}!`;
    }
    return "System Rebellion Dashboard";
  };

  const handleRefresh = () => {
    console.log('🔄 Manual refresh requested');
    webSocketControls.requestSystemInfo();
  };

  const handleResetCircuitBreaker = () => {
    console.log('⚡ Resetting circuit breaker and reconnecting...');
    webSocketControls.resetCircuitBreaker();
  };

  // Get metrics data
  const CPUMetrics = useAppSelector(state => state.cpu.current);
  const MemoryMetrics = useAppSelector(state => state.memory.current);
  const DiskMetrics = useAppSelector(state => state.disk.current);
  const NetworkMetrics = useAppSelector(state => state.network.current);
  const hasMetricsData = CPUMetrics || MemoryMetrics || DiskMetrics || NetworkMetrics;

  // Loading state
  if ((status === 'connecting' || status === 'disconnected') && !hasMetricsData) {
    return (
      <div className="sr-loading">
        <div className="sr-loading__spinner"></div>
        <p>Initializing System Rebellion Dashboard...</p>
        <small>The hamsters are preparing the quantum duct tape...</small>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="sr-dashboard">
        <div className="sr-dashboard__header">
          <h1>System Rebellion Dashboard</h1>
          <div className="sr-dashboard__controls">
            <div className={`sr-connection-status sr-connection-status--${status}`}>
              {status === 'connected' ? '✅ Connected' :
                status === 'error' ? '❌ Disconnected' :
                  '🔄 Connecting...'}
            </div>
            <button
              className="sr-button sr-button--danger"
              onClick={handleResetCircuitBreaker}
              title="Reset the circuit breaker and reconnect"
            >
              ⚡ Reset Circuit Breaker
            </button>
            <button
              className="sr-button sr-button--secondary"
              onClick={handleRefresh}
              title="Refresh metrics data"
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        <div className="sr-card sr-card--cyber">
          <div className="sr-card__header">
            <h2>🚨 Connection Error</h2>
          </div>
          <p>{error}</p>
          <div className="sr-dashboard__controls">
            <button
              className="sr-button sr-button--cyber"
              onClick={handleResetCircuitBreaker}
            >
              ⚡ Reset Circuit Breaker & Reconnect
            </button>
            <button
              className="sr-button sr-button--outline"
              onClick={() => window.location.reload()}
            >
              🔄 Reload Page
            </button>
          </div>
          <p><small>The Stick's anxiety levels are through the roof. Try resetting the circuit breaker first.</small></p>
        </div>
      </div>
    );
  }

  return (
    <div className="sr-dashboard">
      {/* Header */}
      <div className="sr-dashboard__header">
        <h1>{getWelcomeMessage()}</h1>
        <div className="sr-dashboard__controls">
          <div className={`sr-connection-status sr-connection-status--${status}`}>
            {status === 'connected' ? '✅ Connected' :
              status === 'error' ? '❌ Disconnected' :
                '🔄 Connecting...'}
          </div>
          <button
            className="sr-button sr-button--danger"
            onClick={handleResetCircuitBreaker}
            title="Reset the circuit breaker and reconnect"
          >
            ⚡ Reset Circuit Breaker
          </button>
          <button
            className="sr-button sr-button--secondary"
            onClick={handleRefresh}
            title="Refresh metrics data"
          >
            🔄 Refresh
          </button>
        </div>
        <SystemStatus loading={loading} error={error} />
      </div>

      {/* Main Grid */}
      <div className="sr-grid sr-grid--2x2">
        {/* Metrics Panel */}
        <div className="sr-card sr-card--panel">
          <div className="sr-card__header">
            <h2>📊 System Metrics</h2>
            <Link to="/metrics" className="sr-card__action">
              View All Metrics
            </Link>
          </div>

          <div className="sr-grid sr-grid--metrics">
            <DashboardMetricWrapper
              title="CPU Usage"
              value={CPUMetrics?.usage_percent || 0}
              unit="%"
              linkTo="/metrics"
              linkState={{ section: 'cpu' }}
              status={(CPUMetrics?.usage_percent || 0) > 90 ? 'critical' : (CPUMetrics?.usage_percent || 0) > 70 ? 'warning' : 'normal'}
            />
            <DashboardMetricWrapper
              title="Memory Usage"
              value={MemoryMetrics?.percent || 0}
              unit="%"
              linkTo="/metrics"
              linkState={{ section: 'memory' }}
              status={(MemoryMetrics?.percent || 0) > 90 ? 'critical' : (MemoryMetrics?.percent || 0) > 75 ? 'warning' : 'normal'}
            />
            <DashboardMetricWrapper
              title="Disk Usage"
              value={DiskMetrics?.percent || 0}
              unit="%"
              linkTo="/metrics"
              linkState={{ section: 'disk' }}
              status={(DiskMetrics?.percent || 0) > 90 ? 'critical' : (DiskMetrics?.percent || 0) > 75 ? 'warning' : 'normal'}
            />
            <DashboardMetricWrapper
              title="Network Traffic"
              value={(((NetworkMetrics?.recv_rate || 0) + (NetworkMetrics?.sent_rate || 0)) / 1024 / 1024)}
              unit="MB/s"
              linkTo="/metrics"
              linkState={{ section: 'network' }}
              status={((((NetworkMetrics?.recv_rate || 0) + (NetworkMetrics?.sent_rate || 0)) / 1024 / 1024) > 50) ? 'critical' : ((((NetworkMetrics?.recv_rate || 0) + (NetworkMetrics?.sent_rate || 0)) / 1024 / 1024) > 10) ? 'warning' : 'normal'}
            />
          </div>
        </div>

        {/* Alerts Panel */}
        <div className="sr-card sr-card--panel">
          <div className="sr-card__header">
            <h2>🚨 System Alerts</h2>
            <Link to="/alerts" className="sr-card__action">
              View All Alerts
            </Link>
          </div>
          <SystemAlertsPanel maxAlerts={5} showAllLink={false} onNavigateToAlerts={() => navigate('/alerts')} />
        </div>

        {/* Patterns Panel */}
        <div className="sr-card sr-card--panel">
          <div className="sr-card__header">
            <h2>🧠 System Patterns</h2>
            <Link to="/auto-tuner" className="sr-card__action">
              View All Patterns
            </Link>
          </div>
          <SystemPatternsPanel maxPatterns={5} />
        </div>

        {/* WebSocket Test */}
        <div className="sr-card sr-card--cyber">
          <div className="sr-card__header">
            <h2>🔌 WebSocket Manager</h2>
          </div>
          <WebSocketTest />
        </div>
      </div>
    </div>
  );
};

export default DashboardNew;