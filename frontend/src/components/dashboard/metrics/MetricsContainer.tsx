// src/components/dashboard/Metrics/MetricsContainer.tsx
import React, { useEffect } from 'react';

import { useAppSelector } from '../../../store/hooks';
import CPUMetric from '../../metrics/cpu/CpuMetric';
import DiskMetric from '../../metrics/disk/DiskMetric';
import MemoryMetric from '../../metrics/memory/MemoryMetric';
import NetworkMetric from '../../metrics/network/NetworkMetric';

export const MetricsContainer: React.FC = () => {
    const metrics = useAppSelector((state) => state.metrics.current);

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