// frontend/src/components/metrics/Network/tabs/NetworkConnectionsTab.tsx

import React from 'react';
import NetworkConnectionsTable from './NetworkConnectionsTable';
import './NetworkMetrics.css';

interface NetworkConnection {
  protocol: string;
  active: number;
  listening?: number;
  established: number;
}

interface NetworkConnectionsTabProps {
  connections: NetworkConnection[];
  processes?: any[];
}

export const NetworkConnectionsTab: React.FC<NetworkConnectionsTabProps> = ({ connections, processes = [] }) => {
  // If no connections data available
  if (!connections || connections.length === 0) {
    return (
      <div className="network-section">
        <div className="network-section-title">Network Connections</div>
        <div className="no-data-message">No connection data available</div>
      </div>
    );
  }

  return (
    <div className="network-connections-tab">
      <div className="network-section">
        <div className="network-section-title">Network Connections</div>
        
        <div className="connections-summary">
          <div className="connection-stats">
            <div className="connection-stat">
              <div className="stat-value">{getTotalActiveConnections(connections)}</div>
              <div className="stat-label">Active Connections</div>
            </div>
            <div className="connection-stat">
              <div className="stat-value">{getTotalEstablishedConnections(connections)}</div>
              <div className="stat-label">Established</div>
            </div>
            <div className="connection-stat">
              <div className="stat-value">{getTotalListeningConnections(connections)}</div>
              <div className="stat-label">Listening</div>
            </div>
          </div>
        </div>
        
        <div className="connections-by-protocol">
          <h4>Connections by Protocol</h4>
          <div className="protocol-list">
            {connections.map((conn, index) => (
              <div key={index} className="protocol-item">
                <div className="protocol-name">{conn.protocol}</div>
                <div className="protocol-stats">
                  <div className="protocol-stat">
                    <span className="stat-label">Active:</span>
                    <span className="stat-value">{conn.active}</span>
                  </div>
                  {conn.established !== undefined && (
                    <div className="protocol-stat">
                      <span className="stat-label">Established:</span>
                      <span className="stat-value">{conn.established}</span>
                    </div>
                  )}
                  {conn.listening !== undefined && (
                    <div className="protocol-stat">
                      <span className="stat-label">Listening:</span>
                      <span className="stat-value">{conn.listening}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Add the NetworkConnectionsTable component */}
      <NetworkConnectionsTable processes={processes} />
    </div>
  );
};

// Helper functions to calculate totals
const getTotalActiveConnections = (connections: NetworkConnection[]): number => {
  return connections.reduce((total, conn) => total + conn.active, 0);
};

const getTotalEstablishedConnections = (connections: NetworkConnection[]): number => {
  return connections.reduce((total, conn) => total + (conn.established || 0), 0);
};

const getTotalListeningConnections = (connections: NetworkConnection[]): number => {
  return connections.reduce((total, conn) => total + (conn.listening || 0), 0);
};

export default NetworkConnectionsTab;
