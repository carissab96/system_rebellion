// frontend/src/components/metrics/NetworkMetrics/tabs/NetworkOverviewTab.tsx

import React, { useMemo } from 'react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  ResponsiveContainer 
} from 'recharts';
import { NetworkData } from '../types';
import { SystemMetric } from '../../../../types/metrics';
import { formatBytes, formatLatency, getQualityClass } from '../utils/formatters';
import './NetworkMetrics.css';

interface NetworkOverviewTabProps {
  data: NetworkData;
  historicalMetrics: SystemMetric[];
  compact?: boolean;
}

const NetworkOverviewTab: React.FC<NetworkOverviewTabProps> = ({ 
  data, 
  historicalMetrics, 
  compact = false 
}) => {
  // Extract the data we need
  const { io_stats, connection_quality } = data;

  // Create chart data from historical metrics
  const chartData = useMemo(() => {
    if (!historicalMetrics || historicalMetrics.length === 0) return [];

    return historicalMetrics.map(metric => {
      let sentValue = 0;
      let receivedValue = 0;
      
      // Safely extract network data from historical metrics
      const networkData = metric.network || metric.additional?.network_details;
      if (networkData) {
        if (networkData.io_stats) {
          sentValue = networkData.io_stats.bytes_sent || 0;
          receivedValue = networkData.io_stats.bytes_recv || 0;
        } else {
          sentValue = networkData.bytes_sent || 0;
          receivedValue = networkData.bytes_recv || 0;
        }
      }
      
      return {
        timestamp: metric.timestamp,
        bytes_sent: sentValue,
        bytes_recv: receivedValue
      };
    });
  }, [historicalMetrics]);

  return (
    <>
      <div className="metric-value network-metrics">
        <div className="network-sent">
          <div className="network-label">Upload:</div>
          <div className="network-rate">{formatBytes(io_stats.sent_rate)}/s</div>
          <div className="network-total">Total: {formatBytes(io_stats.bytes_sent)}</div>
        </div>
        <div className="network-received">
          <div className="network-label">Download:</div>
          <div className="network-rate">{formatBytes(io_stats.recv_rate)}/s</div>
          <div className="network-total">Total: {formatBytes(io_stats.bytes_recv)}</div>
        </div>
      </div>
      
      {!compact && chartData.length > 0 && (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="sentGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00F5D4" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#00F5D4" stopOpacity={0.2}/>
                </linearGradient>
                <linearGradient id="receivedGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FF9F1C" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#FF9F1C" stopOpacity={0.2}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
              <XAxis 
                dataKey="timestamp"
                tickFormatter={(time: string) => new Date(time).toLocaleTimeString()}
                stroke="rgba(255, 255, 255, 0.7)"
              />
              <YAxis 
                tickFormatter={(value: number) => formatBytes(value)}
                stroke="rgba(255, 255, 255, 0.7)"
              />
              <RechartsTooltip 
                formatter={(value: number, name: string) => {
                  if (name === 'bytes_sent') return [formatBytes(value), 'Sent'];
                  if (name === 'bytes_recv') return [formatBytes(value), 'Received'];
                  return [formatBytes(value), name];
                }}
                labelFormatter={(label: string) => new Date(label).toLocaleString()}
                contentStyle={{ background: 'rgba(0, 0, 0, 0.8)', border: 'none', borderRadius: '8px' }}
                itemStyle={{ color: 'white' }}
                labelStyle={{ color: 'white' }}
              />
              <Area 
                type="monotone" 
                dataKey="bytes_sent" 
                name="Sent"
                stroke="#00F5D4" 
                strokeWidth={2}
                fillOpacity={0.5}
                fill="url(#sentGradient)"
                activeDot={{ r: 4, strokeWidth: 0, fill: '#00F5D4' }}
                isAnimationActive={true}
              />
              <Area 
                type="monotone" 
                dataKey="bytes_recv" 
                name="Received"
                stroke="#FF9F1C" 
                strokeWidth={2}
                fillOpacity={0.5}
                fill="url(#receivedGradient)"
                activeDot={{ r: 4, strokeWidth: 0, fill: '#FF9F1C' }}
                isAnimationActive={true}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
      
      <div className="network-section">
        <div className="network-section-title">Connection Quality</div>
        <div className="connection-quality">
          <div className="quality-score">
            {connection_quality.connection_stability.toFixed(0)}/100
          </div>
          <div className="quality-meter">
            <div 
              className={`quality-meter-fill ${getQualityClass(connection_quality.connection_stability)}`}
              style={{ width: `${connection_quality.connection_stability}%` }}
            />
          </div>
          <div className="quality-details">
            <span>Latency: {formatLatency(connection_quality.average_latency)}</span>
            <span>Packet Loss: {connection_quality.packet_loss_percent.toFixed(1)}%</span>
            <span>Jitter: {formatLatency(connection_quality.jitter)}</span>
          </div>
        </div>
      </div>
    </>
  );
};

export default NetworkOverviewTab;