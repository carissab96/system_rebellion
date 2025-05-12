// frontend/src/components/metrics/NetworkMetrics/tabs/NetworkProtocolChart.tsx

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';
import { ProtocolBreakdown, ProtocolStats } from '../types';
import './NetworkMetrics.css';

// Protocol colors for charts
const PROTOCOL_COLORS = {
  web: '#00F5D4',
  email: '#3A86FF',
  streaming: '#FF9F1C',
  gaming: '#9EF01A',
  file_transfer: '#F8E71C',
  other: '#8A8D91'
};

interface NetworkProtocolChartProps {
  data: ProtocolBreakdown;
  stats: ProtocolStats;
  compact?: boolean;
}

const NetworkProtocolChart: React.FC<NetworkProtocolChartProps> = ({ data, stats, compact = false }) => {
  // Format data for the pie chart
  const chartData = Object.entries(data)
    .map(([name, value]) => ({
      name,
      value: value || 0
    }))
    .filter(item => item.value > 0);

  // If no protocol data available
  if (!chartData || chartData.length === 0) {
    return (
      <div className="network-section">
        <div className="network-section-title">Protocol Breakdown</div>
        <div className="no-data-message">No protocol data available</div>
      </div>
    );
  }

  return (
    <>
      <div className="network-section">
        <div className="network-section-title">Protocol Breakdown</div>
        <div style={{ height: compact ? 200 : 250 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={compact ? 70 : 90}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              >
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={PROTOCOL_COLORS[entry.name as keyof typeof PROTOCOL_COLORS] || '#8884d8'} 
                  />
                ))}
              </Pie>
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="network-section">
        <div className="network-section-title">Protocol Statistics</div>
        <div className="protocol-breakdown">
          <div className="protocol-item">
            <div className="protocol-name">TCP Connections</div>
            <div className="protocol-value">{stats.tcp.active}</div>
          </div>
          <div className="protocol-item">
            <div className="protocol-name">TCP Established</div>
            <div className="protocol-value">{stats.tcp.established}</div>
          </div>
          <div className="protocol-item">
            <div className="protocol-name">UDP Active</div>
            <div className="protocol-value">{stats.udp.active}</div>
          </div>
          <div className="protocol-item">
            <div className="protocol-name">HTTP Connections</div>
            <div className="protocol-value">{stats.http.connections}</div>
          </div>
          <div className="protocol-item">
            <div className="protocol-name">HTTPS Connections</div>
            <div className="protocol-value">{stats.https.connections}</div>
          </div>
          <div className="protocol-item">
            <div className="protocol-name">DNS Queries</div>
            <div className="protocol-value">{stats.dns.queries}</div>
          </div>
        </div>
      </div>
    </>
  );
};

export default NetworkProtocolChart;