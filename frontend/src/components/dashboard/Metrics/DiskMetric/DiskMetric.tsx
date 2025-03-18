// src/components/dashboard/Metrics/DiskMetric/DiskMetric.tsx
import React from 'react';
import { XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart } from 'recharts';
import { useAppSelector } from '../../../../store/hooks';
import { RootState } from '../../../../store/store';
import './DiskMetric.css';
import { SystemMetric } from '../../../../types/metrics';

export const DiskMetric: React.FC = () => {
    // Explicitly type the selectors with SystemMetric
    const currentMetric = useAppSelector((state: RootState) => state.metrics.current) as SystemMetric | null;
    const historicalMetrics = useAppSelector((state: RootState) => state.metrics.historical) as SystemMetric[];
    const isLoading = useAppSelector((state: RootState) => state.metrics.loading);

    // Type your chart data
    const chartData: SystemMetric[] = historicalMetrics;

    if (isLoading) {
        return <div className="metric-card">The Stick is monitoring anxiety levels in your disk...</div>;
    }

    return (
      <div className="metric-card">
        <h3>Disk Usage</h3>
        <div className="metric-value">
            {currentMetric?.disk_usage?.toFixed(1) ?? 0}%
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="diskGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ec4899" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#ec4899" stopOpacity={0.2}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
              <XAxis 
                dataKey="timestamp"
                tickFormatter={(time: string) => new Date(time).toLocaleTimeString()}
                stroke="rgba(255, 255, 255, 0.7)"
              />
              <YAxis 
                domain={[0, 100]}
                tickFormatter={(value: number) => `${value}%`}
                stroke="rgba(255, 255, 255, 0.7)"
              />
              <Tooltip 
                formatter={(value: number) => [`${Number(value).toFixed(1)}%`, 'Disk Usage']}
                labelFormatter={(label: string) => new Date(label).toLocaleString()}
                contentStyle={{ background: 'rgba(0, 0, 0, 0.8)', border: 'none', borderRadius: '8px' }}
                itemStyle={{ color: '#ec4899' }}
                labelStyle={{ color: 'white' }}
              />
              <Area 
                type="monotone" 
                dataKey="disk_usage" 
                stroke="#ec4899" 
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#diskGradient)"
                activeDot={{ r: 6, strokeWidth: 0, fill: '#ec4899' }}
                isAnimationActive={true}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  export default DiskMetric;