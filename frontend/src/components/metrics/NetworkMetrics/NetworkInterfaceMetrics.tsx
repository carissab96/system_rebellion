import React from 'react';
import './NetworkMetrics.css';

interface NetworkInterface {
  name: string;
  isUp: boolean;
  internal: boolean;
  type?: string;
  mac?: string;
  address?: string;
  netmask?: string;
  broadcast?: string;
  bytes_sent?: number;
  bytes_recv?: number;
}

interface InterfaceStats {
  latency?: number;
  packet_loss?: number;
  connection_stability?: number;
  packets_sent: number;
  packets_recv: number;
  errin: number;
  errout: number;
  dropin: number;
  dropout: number;
}

interface Props {
  interfaces: Record<string, NetworkInterface>;
  selectedInterface: string | null;
  setSelectedInterface: (name: string) => void;
  interfaceStats?: Record<string, InterfaceStats>;
}

export const NetworkInterfaceMetrics: React.FC<Props> = ({
  interfaces,
  selectedInterface,
  setSelectedInterface,
  interfaceStats = {},
}) => {
  // Convert interfaces object to array for mapping
  const interfacesArray = Object.entries(interfaces).map(([name, details]) => ({
    ...details,
    name,
  }));

  // Get interface type icon
  const getInterfaceTypeIcon = (iface: NetworkInterface): string => {
    if (iface.internal) return '🔄';
    if (iface.name.includes('wl')) return '📱'; // Wireless
    if (iface.name.includes('en') || iface.name.includes('eth')) return '🔌'; // Ethernet
    if (iface.name.includes('docker') || iface.name.includes('veth')) return '🐳'; // Docker
    if (iface.name.includes('tun') || iface.name.includes('tap')) return '🧪'; // Tunnel
    return '🌐'; // Default
  };

  // Get interface status class
  const getInterfaceStatusClass = (iface: NetworkInterface): string => {
    if (iface.internal) return 'internal';
    return 'external';
  };

  // Format bytes to human-readable format
  const formatBytes = (bytes?: number): string => {
    if (!bytes && bytes !== 0) return 'N/A';
    
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let value = bytes;
    let unitIndex = 0;
    
    while (value >= 1024 && unitIndex < units.length - 1) {
      value /= 1024;
      unitIndex++;
    }
    
    return `${value.toFixed(2)} ${units[unitIndex]}`;
  };

  // Get connection stability label
  const getConnectionStabilityLabel = (stability?: number): string => {
    if (!stability && stability !== 0) return 'N/A';
    if (stability >= 90) return 'Excellent';
    if (stability >= 75) return 'Good';
    if (stability >= 50) return 'Fair';
    return 'Poor';
  };

  // Get selected interface details and stats
  const selectedInterfaceDetails = selectedInterface ? interfaces[selectedInterface] : null;
  const selectedInterfaceStats = selectedInterface ? interfaceStats[selectedInterface] : null;

  return (
    <div className="network-interface-metrics">
      <div className="interface-list">
        <h4>Network Interfaces</h4>
        <div className="interface-tabs">
          {interfacesArray.map((iface) => (
            <div 
              key={iface.name}
              className={`interface-tab ${selectedInterface === iface.name ? 'selected' : ''} ${getInterfaceStatusClass(iface)}`}
              onClick={() => setSelectedInterface(iface.name)}
            >
              <span className="interface-icon">{getInterfaceTypeIcon(iface)}</span>
              <span className="interface-name">{iface.name}</span>
              <span className={`interface-status-badge ${iface.isUp ? 'up' : 'down'}`}>
                {iface.isUp ? 'UP' : 'DOWN'}
              </span>
            </div>
          ))}
        </div>
      </div>
      {selectedInterfaceDetails ? (
        <div className="interface-details">
          <div className="interface-info">
            <h4>Interface Information</h4>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">MAC Address:</span>
                <span className="info-value">{selectedInterfaceDetails.mac || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">IP Address:</span>
                <span className="info-value">{selectedInterfaceDetails.address || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Netmask:</span>
                <span className="info-value">{selectedInterfaceDetails.netmask || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Broadcast:</span>
                <span className="info-value">{selectedInterfaceDetails.broadcast || 'N/A'}</span>
              </div>
            </div>
          </div>

          {selectedInterfaceStats && (
            <>
              <div className="connection-quality">
                <h4>Connection Quality</h4>
                <div className="quality-metrics">
                  <div className="metric-item">
                    <span className="metric-label">Latency:</span>
                    <span className="metric-value">
                      {selectedInterfaceStats.latency !== undefined ? `${selectedInterfaceStats.latency.toFixed(2)} ms` : 'N/A'}
                    </span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Packet Loss:</span>
                    <span className="metric-value">
                      {selectedInterfaceStats.packet_loss !== undefined ? `${(selectedInterfaceStats.packet_loss * 100).toFixed(1)}%` : 'N/A'}
                    </span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Connection Stability:</span>
                    <span className="metric-value">
                      {getConnectionStabilityLabel(selectedInterfaceStats.connection_stability)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="traffic-stats">
                <h4>Traffic Statistics</h4>
                <div className="stats-grid">
                  <div className="stats-item">
                    <span className="stats-label">Bytes Sent:</span>
                    <span className="stats-value">
                      {formatBytes(selectedInterfaceDetails.bytes_sent)}
                    </span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Bytes Received:</span>
                    <span className="stats-value">
                      {formatBytes(selectedInterfaceDetails.bytes_recv)}
                    </span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Packets Sent:</span>
                    <span className="stats-value">
                      {selectedInterfaceStats.packets_sent.toLocaleString()}
                    </span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Packets Received:</span>
                    <span className="stats-value">
                      {selectedInterfaceStats.packets_recv.toLocaleString()}
                    </span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Errors In:</span>
                    <span className="stats-value">
                      {selectedInterfaceStats.errin.toLocaleString()}
                    </span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Errors Out:</span>
                    <span className="stats-value">
                      {selectedInterfaceStats.errout.toLocaleString()}
                    </span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Drops In:</span>
                    <span className="stats-value">
                      {selectedInterfaceStats.dropin.toLocaleString()}
                    </span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Drops Out:</span>
                    <span className="stats-value">
                      {selectedInterfaceStats.dropout.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </>
          )}

          {!selectedInterfaceStats && (
            <div className="no-stats-message">
              <p>No traffic statistics available for this interface.</p>
              <p>The quantum shadow people suggest checking your router, but we recommend ignoring them as usual.</p>
            </div>
          )}
        </div>
      ) : (
        <div className="no-interface-message">
          <p>No network interfaces detected.</p>
          <p>Sir Hawkington is perplexed by this development and suggests checking your network configuration.</p>
        </div>
      )}
    </div>
  );
};

export default NetworkInterfaceMetrics;
