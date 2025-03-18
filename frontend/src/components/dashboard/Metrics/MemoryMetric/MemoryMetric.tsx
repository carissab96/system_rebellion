// src/components/dashboard/Metrics/MemoryMetric/MemoryMetric.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart } from 'recharts';
import { useAppSelector } from '../../../../store/hooks';
import { RootState } from '../../../../store/store';
import './MemoryMetric.css';
import { SystemMetric } from '../../../../types/metrics';

export const MemoryMetric: React.FC = () => {
    // Explicitly type the selectors with SystemMetric
    const currentMetric = useAppSelector((state: RootState) => state.metrics.current) as SystemMetric | null;
    const historicalMetrics = useAppSelector((state: RootState) => state.metrics.historical) as SystemMetric[];
    const isLoading = useAppSelector((state: RootState) => state.metrics.loading);

    // Type your chart data
    const chartData: SystemMetric[] = historicalMetrics;

    if (isLoading) {
        return <div className="metric-card">The Hamsters are fetching memory data...</div>;
    }

    return (
      <div className="metric-card">
        <h3>Memory Usage</h3>
        <div className="metric-value">
            {currentMetric?.memory_usage?.toFixed(1) ?? 0}%
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="memoryGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.2}/>
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
                formatter={(value: number) => [`${Number(value).toFixed(1)}%`, 'Memory Usage']}
                labelFormatter={(label: string) => new Date(label).toLocaleString()}
                contentStyle={{ background: 'rgba(0, 0, 0, 0.8)', border: 'none', borderRadius: '8px' }}
                itemStyle={{ color: '#8b5cf6' }}
                labelStyle={{ color: 'white' }}
              />
              <Area 
                type="monotone" 
                dataKey="memory_usage" 
                stroke="#8b5cf6" 
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#memoryGradient)"
                activeDot={{ r: 6, strokeWidth: 0, fill: '#8b5cf6' }}
                isAnimationActive={true}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };
  
  export default MemoryMetric;