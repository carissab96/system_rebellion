import React, { useState } from 'react';
import './NetworkMetrics.css';

interface NetworkInterface {
  name: string;
  address?: string;
  netmask?: string;
  family?: string;
  mac?: string;
  internal?: boolean;
  cidr?: string;
  isUp?: boolean;
  isVPN?: boolean;
  type?: string;
}

interface InterfaceStats {
  [interfaceName: string]: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
    errin: number;
    errout: number;
    dropin: number;
    dropout: number;
    sent_rate?: number;
    recv_rate?: number;
    error_rate?: number;
    drop_rate?: number;
  };
}

interface NetworkInterfaceMetricsProps {
  interfaces: NetworkInterface[] | Record<string, NetworkInterface> | null | undefined;
  interfaceStats: InterfaceStats;
}

const NetworkInterfaceMetrics: React.FC<NetworkInterfaceMetricsProps> = ({ 
  interfaces, 
  interfaceStats 
}) => {
  // Convert interfaces to array if it's an object or handle null/undefined
  const interfacesArray: NetworkInterface[] = React.useMemo(() => {
    if (!interfaces) return [];
    if (Array.isArray(interfaces)) return interfaces;
    return Object.entries(interfaces).map(([key, details]) => ({
      ...details,
      name: key // Ensure name property is set from the key
    }));
  }, [interfaces]);
  
  const [selectedInterface, setSelectedInterface] = useState<string | null>(
    interfacesArray.length > 0 ? interfacesArray[0].name : null
  );
  
  // Format bytes to human-readable format
  const formatBytes = (bytes?: number): string => {
    if (!bytes && bytes !== 0) return 'N/A';
    
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
  };
  
  // Format rate to human-readable format
  const formatRate = (bytesPerSec?: number): string => {
    if (!bytesPerSec && bytesPerSec !== 0) return 'N/A';
    
    return `${formatBytes(bytesPerSec)}/s`;
  };
  
  // Calculate error/drop percentage
  const calculateErrorPercentage = (errors: number, total: number): string => {
    if (total === 0) return '0.00%';
    return `${((errors / total) * 100).toFixed(2)}%`;
  };
  
  // Get interface type icon
  const getInterfaceTypeIcon = (iface: NetworkInterface): string => {
    if (iface.isVPN) return '🔒'; // VPN
    if (iface.internal) return '🔄'; // Loopback
    if (iface.name.includes('wl')) return '📡'; // Wireless
    if (iface.name.includes('en') || iface.name.includes('eth')) return '🔌'; // Ethernet
    if (iface.name.includes('docker') || iface.name.includes('veth')) return '🐳'; // Docker
    if (iface.name.includes('tun') || iface.name.includes('tap')) return '🧪'; // Tunnel
    return '🌐'; // Default
  };
  
  // Get interface status class
  const getInterfaceStatusClass = (iface: NetworkInterface): string => {
    if (!iface.isUp) return 'interface-down';
    return 'interface-up';
  };
  
  // Get selected interface details
  const selectedInterfaceDetails = selectedInterface 
    ? interfacesArray.find((iface: NetworkInterface) => iface.name === selectedInterface) 
    : null;
    
  // Get selected interface stats
  const selectedInterfaceStats = selectedInterface && interfaceStats[selectedInterface] 
    ? interfaceStats[selectedInterface] 
    : null;
  
  return (
    <div className="network-interface-metrics">
      <div className="interface-list">
        <h4>Network Interfaces</h4>
        <div className="interface-tabs">
          {interfacesArray.map((iface: NetworkInterface) => (
            <div 
              key={iface.name}
              className={`interface-tab ${selectedInterface === iface.name ? 'selected' : ''} ${getInterfaceStatusClass(iface)}`}
              onClick={() => setSelectedInterface(iface.name)}
            >
              <span className="interface-icon">{getInterfaceTypeIcon(iface)}</span>
              <span className="interface-name">{iface.name}</span>
              {iface.isUp === false && <span className="interface-status">DOWN</span>}
            </div>
          ))}
        </div>
      </div>
      
      {selectedInterfaceDetails && (
        <div className="interface-details">
          <div className="interface-header">
            <h4>
              {getInterfaceTypeIcon(selectedInterfaceDetails)} {selectedInterfaceDetails.name}
              {selectedInterfaceDetails.type && <span className="interface-type">({selectedInterfaceDetails.type})</span>}
            </h4>
            <div className={`interface-status-badge ${selectedInterfaceDetails.isUp ? 'up' : 'down'}`}>
              {selectedInterfaceDetails.isUp ? 'UP' : 'DOWN'}
            </div>
          </div>
          
          <div className="interface-info-grid">
            <div className="interface-info-item">
              <span className="info-label">IP Address</span>
              <span className="info-value">{selectedInterfaceDetails.address || 'N/A'}</span>
            </div>
            <div className="interface-info-item">
              <span className="info-label">Netmask</span>
              <span className="info-value">{selectedInterfaceDetails.netmask || 'N/A'}</span>
            </div>
            <div className="interface-info-item">
              <span className="info-label">MAC Address</span>
              <span className="info-value">{selectedInterfaceDetails.mac || 'N/A'}</span>
            </div>
            <div className="interface-info-item">
              <span className="info-label">Family</span>
              <span className="info-value">{selectedInterfaceDetails.family || 'N/A'}</span>
            </div>
            <div className="interface-info-item">
              <span className="info-label">CIDR</span>
              <span className="info-value">{selectedInterfaceDetails.cidr || 'N/A'}</span>
            </div>
            <div className="interface-info-item">
              <span className="info-label">Internal</span>
              <span className="info-value">{selectedInterfaceDetails.internal ? 'Yes' : 'No'}</span>
            </div>
          </div>
          
          {selectedInterfaceStats && (
            <>
              <h4>Traffic Statistics</h4>
              <div className="interface-stats-grid">
                <div className="interface-stat-card">
                  <div className="stat-header">Sent</div>
                  <div className="stat-value">{formatBytes(selectedInterfaceStats.bytes_sent)}</div>
                  <div className="stat-subvalue">{selectedInterfaceStats.packets_sent} packets</div>
                  <div className="stat-rate">{formatRate(selectedInterfaceStats.sent_rate)}</div>
                </div>
                
                <div className="interface-stat-card">
                  <div className="stat-header">Received</div>
                  <div className="stat-value">{formatBytes(selectedInterfaceStats.bytes_recv)}</div>
                  <div className="stat-subvalue">{selectedInterfaceStats.packets_recv} packets</div>
                  <div className="stat-rate">{formatRate(selectedInterfaceStats.recv_rate)}</div>
                </div>
                
                <div className="interface-stat-card">
                  <div className="stat-header">Errors</div>
                  <div className="stat-value">{selectedInterfaceStats.errin + selectedInterfaceStats.errout}</div>
                  <div className="stat-subvalue">In: {selectedInterfaceStats.errin} | Out: {selectedInterfaceStats.errout}</div>
                  <div className="stat-rate">
                    {calculateErrorPercentage(
                      selectedInterfaceStats.errin + selectedInterfaceStats.errout,
                      selectedInterfaceStats.packets_sent + selectedInterfaceStats.packets_recv
                    )}
                  </div>
                </div>
                
                <div className="interface-stat-card">
                  <div className="stat-header">Drops</div>
                  <div className="stat-value">{selectedInterfaceStats.dropin + selectedInterfaceStats.dropout}</div>
                  <div className="stat-subvalue">In: {selectedInterfaceStats.dropin} | Out: {selectedInterfaceStats.dropout}</div>
                  <div className="stat-rate">
                    {calculateErrorPercentage(
                      selectedInterfaceStats.dropin + selectedInterfaceStats.dropout,
                      selectedInterfaceStats.packets_sent + selectedInterfaceStats.packets_recv
                    )}
                  </div>
                </div>
              </div>
              
              <div className="interface-note">
                <div className="note-icon">💡</div>
                <div className="note-text">
                  {selectedInterfaceStats.error_rate && selectedInterfaceStats.error_rate > 0.01 ? (
                    <span className="note-warning">
                      The Hamsters have detected an elevated error rate on this interface. 
                      Sir Hawkington recommends checking your aristocratic cable connections.
                    </span>
                  ) : (
                    <span>
                      This interface is operating within acceptable parameters. 
                      The Meth Snail approves of your networking configuration.
                    </span>
                  )}
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
      )}
      
      {!selectedInterfaceDetails && (
        <div className="no-interface-message">
          <p>No network interfaces detected.</p>
          <p>Sir Hawkington is perplexed by this development and suggests checking your network configuration.</p>
        </div>
      )}
    </div>
  );
};

export default NetworkInterfaceMetrics;
