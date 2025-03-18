import React from 'react';
import { XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart } from 'recharts';
import { useAppSelector } from '../../../../store/hooks';
import { RootState } from '../../../../store/store';
import './NetworkMetric.css';
import { SystemMetric } from '../../../../types/metrics';

export const NetworkMetric: React.FC = () => {
  // Explicitly type the selectors with SystemMetric
  const currentMetric = useAppSelector((state: RootState) => state.metrics.current) as SystemMetric | null;
  const historicalMetrics = useAppSelector((state: RootState) => state.metrics.historical) as SystemMetric[];
  const isLoading = useAppSelector((state: RootState) => state.metrics.loading);

  // Type your chart data
  const chartData: SystemMetric[] = historicalMetrics;

  if (isLoading) {
    return <div className="metric-card">The Quantum Shadow People are measuring network packets and suggesting router configurations...</div>;
  }

  return (
    <div className="metric-card">
      <h3>Network Usage</h3>
      <div className="metric-value">
        {currentMetric?.network_usage?.toFixed(1) ?? 0} MB/s
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="networkGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.2}/>
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
              tickFormatter={(value: number) => `${value} MB/s`}
              stroke="rgba(255, 255, 255, 0.7)"
            />
            <Tooltip 
              formatter={(value: number) => [`${Number(value).toFixed(1)} MB/s`, 'Network Usage']}
              labelFormatter={(label: string) => new Date(label).toLocaleString()}
              contentStyle={{ background: 'rgba(0, 0, 0, 0.8)', border: 'none', borderRadius: '8px' }}
              itemStyle={{ color: '#3b82f6' }}
              labelStyle={{ color: 'white' }}
            />
            <Area 
              type="monotone" 
              dataKey="network_usage" 
              stroke="#3b82f6" 
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#networkGradient)"
              activeDot={{ r: 6, strokeWidth: 0, fill: '#3b82f6' }}
              isAnimationActive={true}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default NetworkMetric;