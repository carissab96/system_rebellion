// src/components/dashboard/Metrics/MemoryMetric/MemoryMetric.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart } from 'recharts';
import { useAppSelector } from '../../../../store/hooks';
import { RootState } from '../../../../store/store';
import { MetricsCard } from '../../../../design-system/components/MetricsCard';
import { SystemMetric } from '../../../../types/metrics';

export const MemoryMetric: React.FC = () => {
    const currentMetric = useAppSelector((state: RootState) => state.metrics.current) as SystemMetric | null;
    const historicalMetrics = useAppSelector((state: RootState) => state.metrics.historical) as SystemMetric[];
    const isLoading = useAppSelector((state: RootState) => state.metrics.loading);

    const memoryUsage = currentMetric?.memory_usage ?? 0;
    const chartData = historicalMetrics;

    // Get previous value from historical metrics
    const previousValue = historicalMetrics.length > 1 ? 
        historicalMetrics[historicalMetrics.length - 2].memory_usage : 
        memoryUsage;

    // Calculate change percentage (avoid division by zero)
    const changePercentage = previousValue && previousValue !== 0 ? 
        ((memoryUsage - previousValue) / previousValue) * 100 : 
        0;

    // Calculate status based on memory usage
    const getStatus = (usage: number) => {
        if (usage > 90) return 'critical';
        if (usage > 75) return 'warning';
        return 'normal';
    };

    // Calculate trend
    const getTrend = (current: number, previous: number): 'up' | 'down' | 'stable' => {
        if (current > previous + 5) return 'up';
        if (current < previous - 5) return 'down';
        return 'stable';
    };

    if (isLoading) {
        return <MetricsCard title="Memory Usage" value="--" unit="%" updating={true} />;
    }

    return (
        <MetricsCard
            title="Memory Usage"
            value={memoryUsage.toFixed(1)}
            unit="%"
            status={getStatus(memoryUsage)}
            trend={getTrend(memoryUsage, previousValue)}
            changePercentage={changePercentage}
            showSparkline={true}
            sparklineData={historicalMetrics.map(m => m.memory_usage)}
        >
            <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={chartData}>
                    <defs>
                        <linearGradient id="memoryGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="var(--primary)" stopOpacity={0.2}/>
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis 
                        dataKey="timestamp"
                        tickFormatter={(time: string) => new Date(time).toLocaleTimeString()}
                        stroke="var(--text-secondary)"
                    />
                    <YAxis 
                        domain={[0, 100]}
                        tickFormatter={(value: number) => `${value}%`}
                        stroke="var(--text-secondary)"
                    />
                    <Tooltip 
                        formatter={(value: number) => [`${Number(value).toFixed(1)}%`, 'Memory Usage']}
                        labelFormatter={(label: string) => new Date(label).toLocaleString()}
                        contentStyle={{ background: 'var(--background)', border: 'none', borderRadius: '8px' }}
                        itemStyle={{ color: 'var(--primary)' }}
                        labelStyle={{ color: 'var(--text-primary)' }}
                    />
                    <Area 
                        type="monotone" 
                        dataKey="memory_usage" 
                        stroke="var(--primary)" 
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#memoryGradient)"
                        activeDot={{ r: 6, strokeWidth: 0, fill: 'var(--primary)' }}
                        isAnimationActive={true}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </MetricsCard>
    );
};

export default MemoryMetric;