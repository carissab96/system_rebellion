// components/agent-theater/AdminConsole/AdminConsole.tsx
import React, { useState, useRef, useEffect } from 'react';

import { useSelector } from 'react-redux';

import { useAgentTheater } from '../../hooks/useAgentTheater';
import type { RootState } from '../../store/store';
import './AdminConsole.css';

interface ConsoleLog {
  timestamp: Date;
  type: 'info' | 'error' | 'warning' | 'success' | 'websocket' | 'database';
  message: string;
  data?: any;
}

export const AdminConsole: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [logs, setLogs] = useState<ConsoleLog[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const { 
    connectionStatus, 
    error, 
    sendMessage, 
    resetCircuitBreaker, 
    setUpdateInterval 
  } = useAgentTheater();
  
  const auth = useSelector((state: RootState) => state.auth);
  const agentTheater = useSelector((state: RootState) => state.agentTheater);

  const addLog = (type: ConsoleLog['type'], message: string, data?: any) => {
    const newLog: ConsoleLog = {
      timestamp: new Date(),
      type,
      message,
      data
    };
    
    setLogs(prev => {
      const updated = [...prev, newLog];
      // Keep only last 1000 logs to prevent memory issues
      return updated.length > 1000 ? updated.slice(-1000) : updated;
    });
  };

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  // Monitor WebSocket messages and add to logs
  useEffect(() => {
    if (connectionStatus === 'connected') {
      addLog('success', 'WebSocket connected successfully');
    } else if (connectionStatus === 'disconnected') {
      addLog('error', 'WebSocket disconnected');
    } else if (connectionStatus === 'connecting') {
      addLog('info', 'Attempting WebSocket connection...');
    }
  }, [connectionStatus]);
  
  // Monitor agent data changes instead of raw messages
  useEffect(() => {
    const agentStates = [
      agentTheater.sirHawkington,
      agentTheater.methSnail,
      agentTheater.hamsters,
      agentTheater.quantumShadow,
      agentTheater.theStick,
      agentTheater.vic20
    ];
    
    agentStates.forEach((agent, index) => {
      const agentNames = ['Sir Hawkington', 'Meth Snail', 'Hamsters', 'Quantum Shadow', 'The Stick', 'VIC-20'];
      if (agent?.isOnline) {
        addLog('websocket', `${agentNames[index]} metrics updated`, agent.data);
      }
    });
  }, [agentTheater]); // Monitor the entire agentTheater state  
  
  
  // Monitor connection status changes
  useEffect(() => {
    if (connectionStatus === 'connected') {
      addLog('success', 'WebSocket connected successfully');
    } else if (connectionStatus === 'disconnected') {
      addLog('error', 'WebSocket disconnected');
    } else if (connectionStatus === 'connecting') {
      addLog('info', 'Attempting WebSocket connection...');
    }
  }, [connectionStatus]);

  // Monitor errors
  useEffect(() => {
    if (error) {
      addLog('error', `System error: ${error}`);
    }
  }, [error]);

  const handleResetCircuitBreaker = () => {
    addLog('info', 'Resetting circuit breaker...');
    resetCircuitBreaker();
  };

  const handleRefreshPage = () => {
    addLog('info', 'Refreshing page...');
    window.location.reload();
  };

  const handleDisconnectWebSocket = () => {
    addLog('warning', 'Manually disconnecting WebSocket...');
    sendMessage({ type: 'disconnect' });
  };

  const handleForceReconnect = () => {
    addLog('info', 'Forcing WebSocket reconnection...');
    // This will trigger a reconnection through the hook
    handleDisconnectWebSocket();
    setTimeout(() => {
      addLog('info', 'Reconnection initiated');
    }, 1000);
  };

  const handleSetUpdateInterval = (interval: number) => {
    addLog('info', `Setting update interval to ${interval}ms`);
    setUpdateInterval(interval);
  };

  const clearLogs = () => {
    setLogs([]);
    addLog('info', 'Console logs cleared');
  };

  const exportLogs = () => {
    const logText = logs.map(log => 
      `[${log.timestamp.toISOString()}] ${log.type.toUpperCase()}: ${log.message}${
        log.data ? `\nData: ${JSON.stringify(log.data, null, 2)}` : ''
      }`
    ).join('\n\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `system-rebellion-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    addLog('info', 'Logs exported to file');
  };

  const formatLogMessage = (log: ConsoleLog) => {
    const timestamp = log.timestamp.toLocaleTimeString();
    return (
      <div key={log.timestamp.getTime()} className={`console-log console-log--${log.type}`}>
        <span className="console-timestamp">[{timestamp}]</span>
        <span className="console-type">{log.type.toUpperCase()}</span>
        <span className="console-message">{log.message}</span>
        {log.data && (
          <details className="console-data">
            <summary>Data</summary>
            <pre>{JSON.stringify(log.data, null, 2)}</pre>
          </details>
        )}
      </div>
    );
  };

  if (!isOpen) {
    return (
      <button 
        className="admin-console-toggle"
        onClick={() => setIsOpen(true)}
        title="Open Admin Console"
      >
        <span className="console-icon">⚡</span>
        Dev Console
      </button>
    );
  }

  return (
    <div className="admin-console-overlay">
      <div className="admin-console">
        <div className="admin-console-header">
          <div className="console-title">
            <span className="console-icon">⚡</span>
            System Rebellion Admin Console
          </div>
          <div className="console-status">
            <span className={`status-indicator status-indicator--${connectionStatus}`}>
              {connectionStatus.toUpperCase()}
            </span>
            <span className="auth-status">
              {auth.isAuthenticated ? `✅ ${auth.user?.email}` : '❌ Not Authenticated'}
            </span>
          </div>
          <button 
            className="console-close"
            onClick={() => setIsOpen(false)}
          >
            ✕
          </button>
        </div>

        <div className="admin-console-controls">
          <div className="control-group">
            <h4>WebSocket Controls</h4>
            <button onClick={handleForceReconnect} className="control-btn control-btn--info">
              🔄 Reconnect
            </button>
            <button onClick={handleDisconnectWebSocket} className="control-btn control-btn--warning">
              🔌 Disconnect
            </button>
            <button onClick={handleResetCircuitBreaker} className="control-btn control-btn--primary">
              🔧 Reset Circuit Breaker
            </button>
          </div>

          <div className="control-group">
            <h4>System Controls</h4>
            <button onClick={handleRefreshPage} className="control-btn control-btn--warning">
              🔄 Refresh Page
            </button>
            <select 
              onChange={(e) => handleSetUpdateInterval(Number(e.target.value))}
              className="control-select"
            >
              <option value="">Update Interval</option>
              <option value="1000">1 second</option>
              <option value="5000">5 seconds</option>
              <option value="10000">10 seconds</option>
              <option value="30000">30 seconds</option>
            </select>
          </div>

          <div className="control-group">
            <h4>Console Controls</h4>
            <button onClick={clearLogs} className="control-btn control-btn--secondary">
              🗑️ Clear Logs
            </button>
            <button onClick={exportLogs} className="control-btn control-btn--success">
              💾 Export Logs
            </button>
            <label className="control-checkbox">
              <input 
                type="checkbox" 
                checked={autoScroll} 
                onChange={(e) => setAutoScroll(e.target.checked)}
              />
              Auto-scroll
            </label>
          </div>
        </div>

        <div className="admin-console-logs">
          <div className="logs-header">
            <h4>Real-time System Logs ({logs.length})</h4>
          </div>
          <div className="logs-container">
            {logs.map(formatLogMessage)}
            <div ref={logsEndRef} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminConsole;