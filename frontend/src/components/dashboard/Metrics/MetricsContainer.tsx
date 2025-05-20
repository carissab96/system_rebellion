// src/components/dashboard/Metrics/MetricsContainer.tsx
import React, { useEffect } from 'react';
import { useAppSelector } from '../../../store/hooks';
import CPUMetric from './CPUMetrics/CPUMetric';
import { MemoryMetric } from './MemoryMetric/MemoryMetric';
import { DiskMetric } from './DiskMetric/DiskMetric';
import NetworkMetric from './NetworkMetric/NetworkMetric';

export const MetricsContainer: React.FC = () => {
    const metrics = useAppSelector((state) => state.metrics);
    
    useEffect(() => {
        console.log("🎨 METRICS CONTAINER UPDATED:", {
            current: metrics.current,
            lastUpdated: metrics.lastUpdated,
            historicalLength: metrics.historical.length
        });
    }, [metrics]);

    return (
        <div className="metrics-grid">
            <CPUMetric />
            <MemoryMetric />
            <DiskMetric />
            <NetworkMetric />
        </div>
    );
};