import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { initializeWebSocket } from '../../store/slices/metricsSlice';
import CPUMetric from '../dashboard/Metrics/CPUMetrics/CPUMetric';
import MemoryMetric from '../dashboard/Metrics/MemoryMetric/MemoryMetric';
import DiskMetric from '../dashboard/Metrics/DiskMetric/DiskMetric';
import { NetworkMetric } from '../dashboard/Metrics/NetworkMetric/NetworkMetric';
import { SystemStatus } from '../dashboard/Dashboard/SystemStatus/SystemStatus';
import './SystemMetrics.css';

const SystemMetrics: React.FC = () => {
  const dispatch = useAppDispatch();
  const error = useAppSelector((state) => state.metrics.error);
  const isLoading = useAppSelector((state) => state.metrics.loading);

  useEffect(() => {
    // Initialize WebSocket connection for metrics
    dispatch(initializeWebSocket());

    return () => {
      // No need to clean up as the websocket service handles this
    };
  }, [dispatch]);

  return (
    <div className="system-metrics-container">
      <header className="metrics-header">
        <h1>System Metrics</h1>
        <SystemStatus loading={isLoading} error={error} />
      </header>
      <div className="metrics-content">
        <div className="metrics-grid">
          <CPUMetric />
          <MemoryMetric />
          <DiskMetric />
          <NetworkMetric />
        </div>
      </div>
    </div>
  );
};

export default SystemMetrics;
