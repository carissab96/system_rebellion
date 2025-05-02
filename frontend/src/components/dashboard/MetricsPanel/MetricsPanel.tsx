import React, { useState, useEffect } from 'react';
import { useAppSelector } from '../../../store/hooks';
import { CPUMetric } from '../Metrics/CPUMetrics/CPUMetric';
import { MemoryMetric } from '../Metrics/MemoryMetric/MemoryMetric';
import { DiskMetric } from '../Metrics/DiskMetric/DiskMetric';
import { NetworkMetric } from '../Metrics/NetworkMetric/NetworkMetric';
import { SirHawkington } from '../../common/CharacterIcons';
import './MetricsPanel.css';

interface MetricsPanelProps {
  showHeader?: boolean;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  showHeader = true
}) => {
  const metrics = useAppSelector((state) => state.metrics.current);
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

  return (
    <div className="metrics-panel">
      {showHeader && (
        <div className="metrics-panel-header">
          <h2>System Metrics</h2>
          <div className="sir-hawkington-icon">
            <SirHawkington className="hawk-icon" />
            <div className="character-tooltip">
              <p>"Sir Hawkington at your service! I'm monitoring your system metrics with aristocratic precision."</p>
            </div>
          </div>
        </div>
      )}
      
      <div className={`metrics-row ${isUpdating ? 'data-updating' : ''}`}>
        <CPUMetric />
        <MemoryMetric />
        <DiskMetric />
        <NetworkMetric />
      </div>
    </div>
  );
};

export default MetricsPanel;
