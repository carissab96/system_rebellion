import React, { useState, useEffect } from 'react';
import { useAppSelector } from '../../../store/hooks';
import { Link } from 'react-router-dom';
import CPUMetric from '../../../components/metrics/CPU/CPUMetric';
import MemoryMetric from '../../../components/metrics/memory/MemoryMetric';
import DiskMetric from '../../../components/metrics/disk/DiskMetric';
import DashboardNetworkMetric from '../../../components/metrics/Network/NetworkMetric';
import './MetricsPanel.css';
import '../../common/CharacterIcons.css'
interface MetricsPanelProps {
  showHeader?: boolean;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  showHeader = true
}) => {
  const status = useAppSelector((state) => state.metrics.status);
  const [isUpdating, setIsUpdating] = useState(false);
  const prevStatusRef = React.useRef(status);

  // Effect for status changes
  useEffect(() => {
    if (status && prevStatusRef.current && status !== prevStatusRef.current) {
      setIsUpdating(true);
      const timer = setTimeout(() => setIsUpdating(false), 1000);
      return () => clearTimeout(timer);
    }
    prevStatusRef.current = status;
  }, [status]);

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
            <div className="character-tooltip">
              <p>"Sir Hawkington at your service! I'm monitoring your system metrics with aristocratic precision."</p>
            </div>
          </div>
          
          {/* Small connection indicator */}
          <div className="connection-indicator">
            <span className={`connection-dot ${getStatusColor(status)}`}></span>
            <span className="connection-text">{status}</span>
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