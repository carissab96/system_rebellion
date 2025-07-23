// components/AgentTheater/shared/ConnectionStatus.tsx
import React from 'react';
import './ConnectionStatus.css';

interface ConnectionStatusProps {
  status: 'connecting' | 'connected' | 'disconnected';
  error?: string | null;
  lastUpdate?: string | null;
  className?: string;
  metricsData?: any;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  status,
  error,
  lastUpdate,
  className = ''
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'connected':
        return '🟢';
      case 'connecting':
        return '🟡';
      case 'disconnected':
        return '🔴';
      default:
        return '⚫';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'Live Feed Active';
      case 'connecting':
        return 'Connecting...';
      case 'disconnected':
        return 'Disconnected';
      default:
        return 'Unknown Status';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'var(--success)';
      case 'connecting':
        return 'var(--warning)';
      case 'disconnected':
        return 'var(--error)';
      default:
        return 'var(--rebellion-text-dim)';
    }
  };

  const formatLastUpdate = () => {
    if (!lastUpdate) return 'Never';
    
    const now = new Date();
    const updateTime = new Date(lastUpdate);
    const diff = now.getTime() - updateTime.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return updateTime.toLocaleDateString();
  };

  return (
    <div className={`connection-status ${status} ${className}`}>
      <div className="status-main">
        <div className="status-indicator-section">
          <span 
            className="status-icon"
            style={{ color: getStatusColor() }}
          >
            {getStatusIcon()}
          </span>
          <div className="status-text-section">
            <div className="status-text" style={{ color: getStatusColor() }}>
              {getStatusText()}
            </div>
            {status === 'connected' && lastUpdate && (
              <div className="last-update">
                Last: {formatLastUpdate()}
              </div>
            )}
          </div>
        </div>
        
        {status === 'connecting' && (
          <div className="connecting-spinner">
            <div className="spinner"></div>
          </div>
        )}
      </div>
      
      {error && (
        <div className="connection-error">
          <div className="error-icon">⚠️</div>
          <div className="error-message">{error}</div>
        </div>
      )}
      
      {status === 'disconnected' && (
        <div className="reconnection-info">
          <div className="reconnection-text">
            Attempting to reconnect...
          </div>
        </div>
      )}
    </div>
  );
};
export default ConnectionStatus;