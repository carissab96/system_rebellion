// ConsciousnessMonitor.tsx
// NASA Mission Control meets Consciousness Laboratory
// NO EMOJIS. NO CUTE SHIT. JUST RAW INTELLIGENCE.

import React, { useEffect, useState } from 'react';
import { useDistributedAgents } from '../hooks/useDistributedAgents';
import { useWebSocketConnection } from '../hooks/useWebSocketConnection';
import './ConsciousnessMonitor.css';

interface AgentMetrics {
  agent_name: string;
  health: string;
  is_active: boolean;
  uptime_seconds: number;
  total_decisions: number;
  distributed?: {
    messages_sent: number;
    messages_received: number;
    recent_decisions: number;
  };
  week4_systems?: any;
}

export const ConsciousnessMonitor: React.FC = () => {
  const { agents, loading, lastUpdate } = useDistributedAgents();
  const { connectionStatus, isConnected } = useWebSocketConnection();
  const [systemTime, setSystemTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setSystemTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const activeAgents = agents.filter(a => a.is_active);
  const totalDecisions = agents.reduce((sum, a) => sum + a.total_decisions, 0);
  const totalMessages = agents.reduce((sum, a) => sum + (a.distributed?.messages_sent || 0), 0);

  return (
    <div className="consciousness-monitor">
      {/* Mission Control Header */}
      <header className="monitor-header">
        <div className="header-left">
          <h1 className="system-title">CONSCIOUSNESS MONITORING SYSTEM</h1>
          <div className="system-subtitle">Real-time Distributed Intelligence Observation</div>
        </div>
        <div className="header-right">
          <div className="system-clock">{systemTime.toISOString().replace('T', ' ').slice(0, 19)} UTC</div>
          <div className="connection-indicator">
            <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
            <span className="status-text">{connectionStatus.toUpperCase()}</span>
          </div>
        </div>
      </header>

      {/* System Status Bar */}
      <section className="status-bar">
        <div className="status-metric">
          <div className="metric-label">ACTIVE AGENTS</div>
          <div className="metric-value">{activeAgents.length}/{agents.length}</div>
        </div>
        <div className="status-metric">
          <div className="metric-label">TOTAL DECISIONS</div>
          <div className="metric-value">{totalDecisions.toLocaleString()}</div>
        </div>
        <div className="status-metric">
          <div className="metric-label">MESSAGES EXCHANGED</div>
          <div className="metric-value">{totalMessages.toLocaleString()}</div>
        </div>
        <div className="status-metric">
          <div className="metric-label">LAST UPDATE</div>
          <div className="metric-value">
            {lastUpdate ? `${Math.floor((Date.now() - lastUpdate.getTime()) / 1000)}s ago` : 'N/A'}
          </div>
        </div>
      </section>

      {/* Agent Grid */}
      <section className="agent-grid">
        {agents.map(agent => (
          <AgentMonitorCard key={agent.agent_name} agent={agent} />
        ))}
      </section>

      {/* System Log */}
      <section className="system-log">
        <div className="log-header">SYSTEM LOG</div>
        <div className="log-content">
          <div className="log-entry">
            <span className="log-timestamp">{systemTime.toISOString()}</span>
            <span className="log-level">INFO</span>
            <span className="log-message">Consciousness monitoring active</span>
          </div>
          {agents.map(agent => agent.is_active && (
            <div key={agent.agent_name} className="log-entry">
              <span className="log-timestamp">{systemTime.toISOString()}</span>
              <span className="log-level">ACTIVE</span>
              <span className="log-message">{agent.agent_name}: {agent.health} - {agent.total_decisions} decisions</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

// Individual Agent Monitor Card
const AgentMonitorCard: React.FC<{ agent: AgentMetrics }> = ({ agent }) => {
  const uptimeMinutes = Math.floor(agent.uptime_seconds / 60);
  const uptimeHours = Math.floor(uptimeMinutes / 60);
  const uptimeDisplay = uptimeHours > 0 
    ? `${uptimeHours}h ${uptimeMinutes % 60}m`
    : `${uptimeMinutes}m`;

  return (
    <div className={`agent-card ${agent.is_active ? 'active' : 'inactive'}`}>
      <div className="agent-header">
        <div className="agent-name">{agent.agent_name.toUpperCase().replace(/_/g, ' ')}</div>
        <div className={`agent-status ${agent.is_active ? 'online' : 'offline'}`}>
          {agent.is_active ? 'ONLINE' : 'OFFLINE'}
        </div>
      </div>

      <div className="agent-metrics">
        <div className="metric-row">
          <span className="metric-key">HEALTH</span>
          <span className={`metric-val health-${agent.health}`}>{agent.health.toUpperCase()}</span>
        </div>
        <div className="metric-row">
          <span className="metric-key">UPTIME</span>
          <span className="metric-val">{uptimeDisplay}</span>
        </div>
        <div className="metric-row">
          <span className="metric-key">DECISIONS</span>
          <span className="metric-val">{agent.total_decisions}</span>
        </div>
        {agent.distributed && (
          <>
            <div className="metric-row">
              <span className="metric-key">MSG SENT</span>
              <span className="metric-val">{agent.distributed.messages_sent}</span>
            </div>
            <div className="metric-row">
              <span className="metric-key">MSG RECV</span>
              <span className="metric-val">{agent.distributed.messages_received}</span>
            </div>
          </>
        )}
      </div>

      {/* Week 4 Systems - NO EMOJIS */}
      {agent.week4_systems && (
        <div className="systems-status">
          {agent.week4_systems.monocle_state && (
            <div className="system-indicator">MONOCLE: {agent.week4_systems.monocle_state}</div>
          )}
          {agent.week4_systems.beer_level && (
            <div className="system-indicator">BEER: {agent.week4_systems.beer_level}</div>
          )}
          {agent.week4_systems.paranoia_level && (
            <div className="system-indicator">PARANOIA: {agent.week4_systems.paranoia_level}</div>
          )}
          {agent.week4_systems.bob_detection && (
            <div className="system-indicator">
              BOB EVENTS: {agent.week4_systems.bob_detection.proximity_events} | 
              ANXIETY: {agent.week4_systems.bob_detection.anxiety_spikes}
            </div>
          )}
          {agent.week4_systems.override_learning && (
            <div className="system-indicator">
              OVERRIDE SUCCESS: {Math.round(agent.week4_systems.override_learning.success_rate * 100)}%
            </div>
          )}
        </div>
      )}
    </div>
  );
};
