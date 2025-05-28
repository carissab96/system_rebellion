// frontend/src/components/metrics/Network/tabs/NetworkInterfacesTab.tsx

import React from 'react';
import './NetworkMetrics.css';

interface NetworkInterface {
  name: string;
  status: string;
  ip_address: string;
  mac_address: string;
  receive_rate: number;
  transmit_rate: number;
}

interface NetworkInterfacesTabProps {
  interfaces: NetworkInterface[];
}

export const NetworkInterfacesTab: React.FC<NetworkInterfacesTabProps> = ({ interfaces }) => {
  // If no interfaces data available
  if (!interfaces || interfaces.length === 0) {
    return (
      <div className="network-section">
        <div className="network-section-title">Network Interfaces</div>
        <div className="no-data-message">No network interfaces data available</div>
      </div>
    );
  }

  return (
    <div className="network-interfaces-tab">
      <div className="network-section">
        <div className="network-section-title">Network Interfaces</div>
        <div className="interfaces-list">
          {interfaces.map((iface, index) => (
            <div key={index} className="interface-card">
              <div className="interface-header">
                <div className="interface-name">{iface.name}</div>
                <div className={`interface-status ${iface.status.toLowerCase() === 'up' ? 'status-up' : 'status-down'}`}>
                  {iface.status}
                </div>
              </div>
              <div className="interface-details">
                <div className="interface-detail">
                  <span className="detail-label">IP Address:</span>
                  <span className="detail-value">{iface.ip_address}</span>
                </div>
                <div className="interface-detail">
                  <span className="detail-label">MAC Address:</span>
                  <span className="detail-value">{iface.mac_address}</span>
                </div>
                <div className="interface-detail">
                  <span className="detail-label">Download Rate:</span>
                  <span className="detail-value">{formatBytes(iface.receive_rate)}/s</span>
                </div>
                <div className="interface-detail">
                  <span className="detail-label">Upload Rate:</span>
                  <span className="detail-value">{formatBytes(iface.transmit_rate)}/s</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Helper function to format bytes
const formatBytes = (bytes: number, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

export default NetworkInterfacesTab;
