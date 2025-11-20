// components/navigation/SecondaryNav.tsx
// Secondary info bar - System status, uptime, connection info
// Built by: Dell-Sonnet - November 20, 2025

import React, { useState, useEffect } from 'react';
import { useWebSocketConnection } from '../../hooks/useWebSocketConnection';
import { useDistributedAgents } from '../../hooks/useDistributedAgents';
import './Navigation.css';

interface SecondaryNavProps {
  onRefresh?: () => void;
}

export const SecondaryNav: React.FC<SecondaryNavProps> = ({ onRefresh }) => {
  const { connectionStatus, isConnected } = useWebSocketConnection();
  const { agents } = useDistributedAgents();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [sessionUptime, setSessionUptime] = useState(0);

  // Update current time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Track session uptime
  useEffect(() => {
    const startTime = Date.now();
    const timer = setInterval(() => {
      setSessionUptime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const formatDateTime = (date: Date): string => {
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  const activeAgentCount = agents.filter(a => a.is_active).length;
  const totalAgents = 6; // We have 6 agents

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    }
    // Also trigger a manual refresh of agents data
    window.location.reload();
  };

  return (
    <nav className="secondary-nav">
      <div className="info-item">
        <span className="info-icon">⏱</span>
        <span className="info-label">Uptime:</span>
        <span className="info-value">{formatUptime(sessionUptime)} (Session)</span>
        {/* TODO: Add total uptime from backend */}
      </div>

      <div className="info-item">
        <span className={`info-icon ${activeAgentCount === totalAgents ? 'status-active' : 'status-partial'}`}>
          ●
        </span>
        <span className="info-value">
          {activeAgentCount}/{totalAgents} Agents Active
        </span>
      </div>

      <div className="info-item">
        <span className={`info-icon ${isConnected ? 'status-connected' : 'status-disconnected'}`}>
          🔌
        </span>
        <span className="info-label">WebSocket:</span>
        <span className="info-value">{connectionStatus}</span>
        <button 
          className="refresh-btn"
          onClick={handleRefresh}
          title="Refresh connection"
          aria-label="Refresh connection"
        >
          ↻
        </button>
      </div>

      <div className="info-item">
        <span className="info-icon">📅</span>
        <span className="info-value">{formatDateTime(currentTime)}</span>
      </div>

      <div className="info-item">
        <span className="info-icon">⚠️</span>
        <span className="info-label">Last Incident:</span>
        <span className="info-value">
          {/* TODO: Calculate from backend data */}
          --
        </span>
      </div>
    </nav>
  );
};
