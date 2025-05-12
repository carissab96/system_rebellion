// frontend/src/components/metrics/NetworkMetrics/tabs/NetworkInterfaceMetrics.tsx

import React from 'react';
import { NetworkInterface } from '../types';
import { formatBytes } from '../utils/formatters';
import './NetworkMetrics.css';

interface NetworkInterfaceMetricsProps {
  interfaces: NetworkInterface[];
  compact?: boolean;
}

const NetworkInterfaceMetrics: React.FC<NetworkInterfaceMetricsProps> = ({ interfaces, compact = false }) => {
  // If no interface data available
  if (!interfaces || interfaces.length === 0) {
    return (
      <div className="network-section">
        <div className="network-section-title">Network Interfaces</div>
        <div className="no-data-message">No interface data available</div>
      </div>
    );
  }

  return (
    <div className="network-section">
      <div className="network-section-title">Network Interfaces</div>
      <div className="interface-stats">
        {interfaces.map((iface, index) => (
          <div key={index} className="interface-item">
            <div className="interface-header">
              <div className="interface-name">{iface.name}</div>
              <div className={`interface-status ${iface.isup ? '' : 'down'}`}>
                {iface.isup ? 'Up' : 'Down'}
              </div>
            </div>
            <div className="interface-details">
              <div className="interface-detail">
                <div className="detail-label">IP Address:</div>
                <div className="detail-value">{iface.address || 'N/A'}</div>
              </div>
              <div className="interface-detail">
                <div className="detail-label">MAC Address:</div>
                <div className="detail-value">{iface.mac_address || 'N/A'}</div>
              </div>
              <div className="interface-detail">
                <div className="detail-label">Speed:</div>
                <div className="detail-value">{iface.speed ? `${iface.speed} Mbps` : 'N/A'}</div>
              </div>
              <div className="interface-detail">
                <div className="detail-label">MTU:</div>
                <div className="detail-value">{iface.mtu || 'N/A'}</div>
              </div>
              <div className="interface-detail">
                <div className="detail-label">Sent:</div>
                <div className="detail-value">{formatBytes(iface.bytes_sent || 0)}</div>
              </div>
              <div className="interface-detail">
                <div className="detail-label">Received:</div>
                <div className="detail-value">{formatBytes(iface.bytes_recv || 0)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NetworkInterfaceMetrics;