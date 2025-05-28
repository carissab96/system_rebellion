// frontend/src/components/metrics/NetworkMetrics/tabs/NetworkConnectionsTable.tsx

import React from 'react';
import { NetworkProcess } from '@/components/metrics/Network/tabs/types'; // You'll need to create this type file
import { formatBytes } from '@/components/metrics/Network/utils/formatters';
import './NetworkMetrics.css';

interface NetworkConnectionsTableProps {
  processes: NetworkProcess[];
  compact?: boolean;
}

const NetworkConnectionsTable: React.FC<NetworkConnectionsTableProps> = ({ processes, compact: _ = false }) => {
  // If no process data available
  if (!processes || processes.length === 0) {
    return (
      <div className="network-section">
        <div className="network-section-title">Top Bandwidth Processes</div>
        <div className="no-data-message">No process data available</div>
      </div>
    );
  }

  return (
    <div className="network-section">
      <div className="network-section-title">Top Bandwidth Processes</div>
      <table className="process-table">
        <thead>
          <tr>
            <th>Process</th>
            <th>PID</th>
            <th>Upload</th>
            <th>Download</th>
            <th>Total</th>
            <th>Connections</th>
          </tr>
        </thead>
        <tbody>
          {processes.map((process, index) => (
            <tr key={index}>
              <td>{process.name}</td>
              <td>{process.pid}</td>
              <td>{formatBytes(process.write_rate || 0)}/s</td>
              <td>{formatBytes(process.read_rate || 0)}/s</td>
              <td>{formatBytes((process.write_rate || 0) + (process.read_rate || 0))}/s</td>
              <td>{process.connection_count || 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default NetworkConnectionsTable;