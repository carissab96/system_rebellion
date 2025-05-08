import React, { useState, useRef, useEffect } from 'react';
import './NetworkMetrics.css';

interface Connection {
  type: string;
  laddr: string;
  raddr: string;
  status: string;
  pid?: number;
  process_name?: string;
  protocol?: string;
  bytes_sent?: number;
  bytes_recv?: number;
  created?: string;
  total_rate?: number;
}

interface NetworkConnectionsTableProps {
  connections: Connection[];
}

const NetworkConnectionsTable: React.FC<NetworkConnectionsTableProps> = ({ connections }) => {
  const [sortField, setSortField] = useState<keyof Connection>('bytes_sent');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [filter, setFilter] = useState('');
  const [displayLimit, setDisplayLimit] = useState<number>(50);
  const tableContainerRef = useRef<HTMLDivElement>(null);
  
  // Handle sort click
  const handleSortClick = (field: keyof Connection) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };
  
  // Format bytes to human-readable format
  const formatBytes = (bytes?: number): string => {
    if (!bytes) return '0 B';
    
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
  };
  
  // Sort connections
  const sortedConnections = [...connections].sort((a, b) => {
    const aValue = a[sortField] || 0;
    const bValue = b[sortField] || 0;
    
    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  
  // Filter connections
  const filteredConnections = sortedConnections.filter(conn => {
    if (!filter) return true;
    
    const searchValue = filter.toLowerCase();
    return (
      (conn.process_name?.toLowerCase().includes(searchValue)) ||
      (conn.laddr?.toLowerCase().includes(searchValue)) ||
      (conn.raddr?.toLowerCase().includes(searchValue)) ||
      (conn.status?.toLowerCase().includes(searchValue)) ||
      (conn.protocol?.toLowerCase().includes(searchValue))
    );
  });
  
  // Get visible connections based on display limit
  const visibleConnections = filteredConnections.slice(0, displayLimit);
  
  // Handle scroll to load more connections
  useEffect(() => {
    const handleScroll = () => {
      if (tableContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = tableContainerRef.current;
        // When user scrolls to bottom, load more connections
        if (scrollTop + clientHeight >= scrollHeight - 50) {
          setDisplayLimit(prev => Math.min(prev + 20, filteredConnections.length));
        }
      }
    };
    
    const currentTable = tableContainerRef.current;
    if (currentTable) {
      currentTable.addEventListener('scroll', handleScroll);
    }
    
    return () => {
      if (currentTable) {
        currentTable.removeEventListener('scroll', handleScroll);
      }
    };
  }, [filteredConnections.length]);
  
  // Render sort indicator
  const renderSortIndicator = (field: keyof Connection) => {
    if (field !== sortField) return null;
    
    return (
      <span className="sort-indicator">
        {sortDirection === 'asc' ? '▲' : '▼'}
      </span>
    );
  };
  
  return (
    <div className="network-connections-container">
      <div className="table-controls">
        <input
          type="text"
          placeholder="Filter connections..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="connection-filter"
        />
        <div className="connection-count">
          Showing {visibleConnections.length} of {filteredConnections.length} connections
        </div>
      </div>
      
      <div ref={tableContainerRef} className="network-connections-scrollable">
        {filteredConnections.length > 0 ? (
          <table className="network-connections-table">
            <thead>
              <tr>
                <th onClick={() => handleSortClick('process_name')}>
                  Process {renderSortIndicator('process_name')}
                </th>
                <th onClick={() => handleSortClick('protocol')}>
                  Protocol {renderSortIndicator('protocol')}
                </th>
                <th onClick={() => handleSortClick('laddr')}>
                  Local Address {renderSortIndicator('laddr')}
                </th>
                <th onClick={() => handleSortClick('raddr')}>
                  Remote Address {renderSortIndicator('raddr')}
                </th>
                <th onClick={() => handleSortClick('status')}>
                  Status {renderSortIndicator('status')}
                </th>
                <th onClick={() => handleSortClick('bytes_sent')}>
                  Sent {renderSortIndicator('bytes_sent')}
                </th>
                <th onClick={() => handleSortClick('bytes_recv')}>
                  Received {renderSortIndicator('bytes_recv')}
                </th>
              </tr>
            </thead>
            <tbody>
              {visibleConnections.map((conn, index) => (
                <tr key={index} className={conn.status === 'ESTABLISHED' ? 'connection-established' : ''}>
                  <td className="process-name">
                    {conn.process_name || 'Unknown'}
                    {conn.pid && <span className="process-pid">({conn.pid})</span>}
                  </td>
                  <td>{conn.protocol || conn.type || 'Unknown'}</td>
                  <td>{conn.laddr || 'N/A'}</td>
                  <td>{conn.raddr || 'N/A'}</td>
                  <td>
                    <span className={`connection-status status-${conn.status?.toLowerCase()}`}>
                      {conn.status || 'Unknown'}
                    </span>
                  </td>
                  <td>{formatBytes(conn.bytes_sent)}</td>
                  <td>{formatBytes(conn.bytes_recv)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="no-connections">
            <p>No connections match your filter criteria.</p>
            <p>The quantum shadow people suggest checking your router, but Sir Hawkington recommends ignoring them.</p>
          </div>
        )}
      </div>
      
      {filteredConnections.length > displayLimit && (
        <div className="load-more-container">
          <button 
            className="load-more-button"
            onClick={() => setDisplayLimit(prev => Math.min(prev + 20, filteredConnections.length))}
          >
            Load More Connections
          </button>
        </div>
      )}
    </div>
  );
};

export default NetworkConnectionsTable;
