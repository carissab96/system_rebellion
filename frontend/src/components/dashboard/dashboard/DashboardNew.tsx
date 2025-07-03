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

// Sir Hawkington Dashboard Widget Component
const SirHawkingtonDashboardWidget: React.FC = () => {
  const metricsData = useAppSelector((state: RootState) => state.metrics.current);
  const hawkingtonData = metricsData?.sir_hawkington;
  const agentProcessing = metricsData?.agent_processing;
  
  const getMonocleStatus = () => {
    if (!hawkingtonData) return 'adjusting';
    if (hawkingtonData.error) return 'fogged';
    if (hawkingtonData.decision_type === 'alert') return 'popped';
    if (hawkingtonData.decision_type === 'concern') return 'adjusted';
    return 'polished';
  };

  const getDecisionColor = () => {
    if (!hawkingtonData) return 'normal';
    if (hawkingtonData.error) return 'critical';
    if (hawkingtonData.decision_type === 'alert') return 'critical';
    if (hawkingtonData.decision_type === 'concern') return 'warning';
    return 'normal';
  };

  const getMonocleEmoji = () => {
    const status = getMonocleStatus();
    switch (status) {
      case 'polished': return '✨';
      case 'adjusted': return '🔧';
      case 'popped': return '💥';
      case 'fogged': return '😵';
      default: return '🔧';
    }
  };

  const getStatusText = () => {
    const status = getMonocleStatus();
    switch (status) {
      case 'polished': return 'Polished & Ready';
      case 'adjusted': return 'Adjusted with Concern';
      case 'popped': return 'Popped from Alert!';
      case 'fogged': return 'Fogged with Error';
      default: return 'Adjusting...';
    }
  };

  const wasSuccessful = agentProcessing?.successful_agents?.some((agent: { agent_name: string; }) => agent.agent_name === 'sir_hawkington');
  const processingTime = agentProcessing?.successful_agents?.find((agent: { agent_name: string; }) => agent.agent_name === 'sir_hawkington')?.processing_time_seconds;

  return (
    <div className="sr-card sr-card--cyber">
      <div className="sr-card__header">
        <h2>🧐 Sir Hawkington's Analysis</h2>
        <Link to="/metrics" className="sr-card__action">
          Full Analysis
        </Link>
      </div>
      
      <div className="sr-agent-status">
        <div className="sr-agent-status__header">
          <div className="sr-agent-status__avatar">
            🧐
          </div>
          <div className="sr-agent-status__info">
            <h3>Sir Hawkington</h3>
            <p>System Analyst & Gentleman</p>
          </div>
          <div className={`sr-agent-status__badge sr-agent-status__badge--${getMonocleStatus()}`}>
            {getMonocleEmoji()} {getStatusText()}
          </div>
        </div>
        
        {hawkingtonData ? (
          <div className="sr-agent-analysis">
            <div className={`sr-agent-analysis__decision sr-agent-analysis__decision--${getDecisionColor()}`}>
              {hawkingtonData.error ? 'ERROR' : (hawkingtonData.decision_type?.toUpperCase() || 'ANALYZING')}
            </div>
            <p className="sr-agent-analysis__message">
              {hawkingtonData.message || 'Adjusting monocle for optimal analysis...'}
            </p>
            {!hawkingtonData.error && (
              <div className="sr-agent-analysis__confidence">
                <span>Confidence: {((hawkingtonData.confidence || 0) * 100).toFixed(1)}%</span>
                <div className="sr-progress-bar">
                  <div 
                    className="sr-progress-bar__fill" 
                    style={{ width: `${(hawkingtonData.confidence || 0) * 100}%` }}
                  />
                </div>
              </div>
            )}
            <div className="sr-agent-analysis__meta">
              <small>
                {wasSuccessful ? 
                  `✅ Analyzed in ${(processingTime * 1000).toFixed(1)}ms` : 
                  '❌ Analysis failed'
                }
                {hawkingtonData.agent_version && ` • v${hawkingtonData.agent_version}`}
              </small>
            </div>
          </div>
        ) : (
          <div className="sr-agent-analysis">
            <div className="sr-agent-analysis__decision sr-agent-analysis__decision--normal">
              INITIALIZING
            </div>
            <p className="sr-agent-analysis__message">
              🧐 Sir Hawkington is polishing his monocle and preparing for analysis...
            </p>
            <div className="sr-agent-analysis__confidence">
              <span>Confidence: Pending...</span>
              <div className="sr-progress-bar">
                <div className="sr-progress-bar__fill sr-progress-bar__fill--pulse" style={{ width: '50%' }} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

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

      {/* Main Grid - Now with 6 panels (3x2) */}
      <div className="sr-grid sr-grid--3x2">
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

        {/* Sir Hawkington's Analysis Widget */}
        <SirHawkingtonDashboardWidget />

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

        {/* WebSocket Control Panel */}
        <div className="sr-card sr-card--cyber">
          <div className="sr-card__header">
            <h2>🔌 WebSocket Manager</h2>
          </div>
          <WebSocketTest />
        </div>

        {/* Future: Could add Meth Snail widget here */}
        <div className="sr-card sr-card--panel">
          <div className="sr-card__header">
            <h2>🚀 System Status</h2>
          </div>
          <div className="sr-system-overview">
            <p>System Rebellion Dashboard</p>
            <p>🧐 Sir Hawkington: Active</p>
            <p>🐌 Meth Snail: Optimizing</p>
            <p>📏 The Stick: Pending</p>
            <p>🤖 VIC-20: Pending</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardNew