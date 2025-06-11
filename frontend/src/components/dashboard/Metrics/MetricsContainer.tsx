// src/components/dashboard/Metrics/MetricsContainer.tsx
import React, { useEffect } from 'react';
import { useAppSelector } from '../../../store/hooks';
import CPUMetric from '../../../components/metrics/CPU/CPUMetric';
import MemoryMetric from '../../../components/metrics/memory/MemoryMetric';
import { DiskMetric } from '../../../components/metrics/disk/DiskMetric';
import NetworkMetric from '../../../components/metrics/Network/NetworkMetric';

export const MetricsContainer: React.FC = () => {
    const metrics = useAppSelector((state) => state.metrics);
    
    useEffect(() => {
        console.log("🎨 METRICS CONTAINER UPDATED:", {
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