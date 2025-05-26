import React, { useState, useEffect } from 'react';
import { useAppSelector } from '../../../store/hooks';
import { Link } from 'react-router-dom';
import CPUMetric from '../Metrics/CPUMetrics/CPUMetric';
import { MemoryMetric } from '../Metrics/MemoryMetric/MemoryMetric';
import { DiskMetric } from '../Metrics/DiskMetric/DiskMetric';
import DashboardNetworkMetric from '../Metrics/NetworkMetric/NetworkMetric';
import { SirHawkington } from '../../common/CharacterIcons';
import './MetricsPanel.css';

interface MetricsPanelProps {
  showHeader?: boolean;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  showHeader = true
}) => {
  const metrics = useAppSelector((state) => state.metrics.current);
  const { connectionStatus } = useAppSelector((state) => state.metrics);
  const [isUpdating, setIsUpdating] = useState(false);
  const prevMetricsRef = React.useRef(metrics);

  // Effect for data update animations
  useEffect(() => {
    if (metrics && prevMetricsRef.current && JSON.stringify(metrics) !== JSON.stringify(prevMetricsRef.current)) {
      setIsUpdating(true);
      const timer = setTimeout(() => setIsUpdating(false), 1000);
      return () => clearTimeout(timer);
    }
    prevMetricsRef.current = metrics;
  }, [metrics]);

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'status-connected';
      case 'connecting':
        return 'status-connecting';
      case 'disconnected':
      case 'error':
        return 'status-disconnected';
      default:
        return 'status-disconnected';
    }
  };

  return (
    <div className="metrics-panel">
      {showHeader && (
        <div className="metrics-panel-header">
          <div className="metrics-header-left">
            <h2>System Metrics</h2>
            <Link to="/metrics" className="view-full-metrics-link">
              View Full Metrics
            </Link>
          </div>
          <div className="sir-hawkington-icon">
            <SirHawkington className="hawk-icon" />
            <div className="character-tooltip">
              <p>"Sir Hawkington at your service! I'm monitoring your system metrics with aristocratic precision."</p>
            </div>
          </div>
          
          {/* Small connection indicator */}
          <div className="connection-indicator">
            <span className={`connection-dot ${getStatusColor(connectionStatus)}`}></span>
            <span className="connection-text">{connectionStatus}</span>
          </div>
        </div>
      )}
      
      <div className={`metrics-row ${isUpdating ? 'data-updating' : ''}`}>
        <CPUMetric />
        <MemoryMetric />
        <DiskMetric />
        <DashboardNetworkMetric />
      </div>
    </div>
  );
};

export default MetricsPanel;