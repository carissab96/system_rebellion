// frontend/src/components/metrics/NetworkMetrics/tabs/NetworkQualityMetrics.tsx

import React from 'react';
import { ConnectionQuality } from './types';
import { formatLatency, getQualityClass, getLatencyClass } from '../utils/formatters';
import './NetworkMetrics.css';

interface NetworkQualityMetricsProps {
  data: ConnectionQuality;
}

const NetworkQualityMetrics: React.FC<NetworkQualityMetricsProps> = ({ data }) => {
  return (
    <div className="network-section">
      <div className="network-section-title">Connection Quality Score</div>
      <div className="connection-quality">
        <div className="quality-score">
          {data.connection_stability.toFixed(0)}/100
        </div>
        <div className="quality-meter">
          <div 
            className={`quality-meter-fill ${getQualityClass(data.connection_stability)}`}
            style={{ width: `${data.connection_stability}%` }}
          />
        </div>
        <div className="quality-score-label">Connection Stability Score</div>
      </div>
      
      <div className="network-section-title">Latency Metrics</div>
      <div className="latency-metrics">
        <div className="latency-item">
          <div className="latency-name">Gateway</div>
          <div className={`latency-value ${getLatencyClass(data.gateway_latency)}`}>
            {formatLatency(data.gateway_latency)}
          </div>
        </div>
        <div className="latency-item">
          <div className="latency-name">DNS</div>
          <div className={`latency-value ${getLatencyClass(data.dns_latency)}`}>
            {formatLatency(data.dns_latency)}
          </div>
        </div>
        <div className="latency-item">
          <div className="latency-name">Internet</div>
          <div className={`latency-value ${getLatencyClass(data.internet_latency)}`}>
            {formatLatency(data.internet_latency)}
          </div>
        </div>
      </div>
      
      <div className="network-section-title">Connection Stability Factors</div>
      <div className="quality-details">
        <div className="quality-detail">
          <div className="detail-label">Average Latency:</div>
          <div className="detail-value">{formatLatency(data.average_latency)}</div>
        </div>
        <div className="quality-detail">
          <div className="detail-label">Packet Loss:</div>
          <div className="detail-value">{data.packet_loss_percent.toFixed(1)}%</div>
        </div>
        <div className="quality-detail">
          <div className="detail-label">Jitter:</div>
          <div className="detail-value">{formatLatency(data.jitter)}</div>
        </div>
      </div>
    </div>
  );
};

export default NetworkQualityMetrics;