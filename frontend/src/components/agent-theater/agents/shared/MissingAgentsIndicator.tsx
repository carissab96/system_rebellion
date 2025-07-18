// components/AgentTheater/shared/MissingAgentsIndicator.tsx
import React from 'react';
import './MissingAgentsIndicator.css';

interface MissingAgentsIndicatorProps {
  metricsData: any;
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
  className?: string;
}

interface AgentInfo {
  id: string;
  name: string;
  title: string;
  expectedData: string;
}

const EXPECTED_AGENTS: AgentInfo[] = [
  {
    id: 'sir_hawkington',
    name: 'Sir Hawkington Von Monitorious III',
    title: 'Systems Watchman',
    expectedData: 'sir_hawkington'
  },
  {
    id: 'meth_snail',
    name: 'Meth Snail',
    title: 'Optimization Specialist',
    expectedData: 'meth_snail'
  },
  {
    id: 'hamsters',
    name: 'The Hamsters',
    title: 'Rapid Response Engineering',
    expectedData: 'hamsters'
  },
  {
    id: 'quantum_shadow',
    name: 'Quantum Shadow People',
    title: 'Interdimensional Networking',
    expectedData: 'quantum_shadow'
  },
  {
    id: 'the_stick',
    name: 'The Stick',
    title: 'Compliance Expert',
    expectedData: 'the_stick'
  },
  {
    id: 'vic20',
    name: 'VIC-20 Sage',
    title: 'Ancient Wisdom Coordinator',
    expectedData: 'vic20_sage'
  }
];

export const MissingAgentsIndicator: React.FC<MissingAgentsIndicatorProps> = ({
  metricsData,
  connectionStatus,
  className = ''
}) => {
  // Don't show if we're still connecting
  if (connectionStatus === 'connecting') {
    return null;
  }

  // Find missing agents - NO FAKE DATA, just truth
  const missingAgents = EXPECTED_AGENTS.filter(agent => 
    !metricsData || !metricsData[agent.expectedData]
  );

  // Don't show if all agents are present
  if (missingAgents.length === 0) {
    return null;
  }

  const getMissingReason = (agent: AgentInfo): string => {
    if (connectionStatus === 'disconnected') {
      return 'WebSocket connection lost';
    }
    
    // Specific reasons based on agent type
    switch (agent.id) {
      case 'sir_hawkington':
        return 'Monocle adjustment protocol offline';
      case 'meth_snail':
        return 'Shell spinning handler not responding';
      case 'hamsters':
        return 'Beer supply monitoring offline';
      case 'quantum_shadow':
        return 'Interdimensional connection severed';
      case 'the_stick':
        return 'Compliance monitoring handler offline';
      case 'vic20':
        return 'Ancient wisdom bridge disconnected';
      default:
        return 'WebSocket handler not streaming data';
    }
  };

  const getSeverityLevel = (): 'info' | 'warning' | 'error' => {
    if (connectionStatus === 'disconnected') return 'error';
    if (missingAgents.length >= 4) return 'error';
    if (missingAgents.length >= 2) return 'warning';
    return 'info';
  };

  const severity = getSeverityLevel();

  return (
    <div className={`missing-agents-indicator ${severity} ${className}`}>
      <div className="missing-agents-header">
        <div className="header-icon">
          {severity === 'error' ? '🚨' : severity === 'warning' ? '⚠️' : 'ℹ️'}
        </div>
        <div className="header-text">
          <h3>Missing Agents ({missingAgents.length}/{EXPECTED_AGENTS.length})</h3>
          <p>The following agents are not streaming data:</p>
        </div>
      </div>
      
      <div className="missing-agents-grid">
        {missingAgents.map(agent => (
          <div key={agent.id} className="missing-agent-card">
            <div className="agent-info">
              <div className="agent-name">{agent.name}</div>
              <div className="agent-title">{agent.title}</div>
              <div className="missing-reason">
                <strong>Reason:</strong> {getMissingReason(agent)}
              </div>
            </div>
            <div className="agent-status">
              <span className="status-dot offline"></span>
              <span className="status-text">Offline</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="missing-agents-footer">
        <div className="troubleshooting-info">
          <strong>Troubleshooting:</strong>
          <ul>
            <li>Check individual agent WebSocket handlers</li>
            <li>Verify agent decision engines are running</li>
            <li>Confirm database connections are active</li>
            <li>Review agent-specific log files</li>
          </ul>
        </div>
        
        {connectionStatus === 'connected' && (
          <div className="connection-note">
            <strong>Note:</strong> WebSocket connection is active but agents are not streaming data.
            This indicates agent-specific issues, not connection problems.
          </div>
        )}
      </div>
    </div>
  );
};
export default MissingAgentsIndicator;
