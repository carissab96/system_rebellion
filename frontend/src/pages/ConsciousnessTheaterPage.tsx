// pages/ConsciousnessTheaterPage.tsx
// THE CONSCIOUSNESS THEATER - Where consciousness performs itself
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "This isn't monitoring. This is ALIVE."

import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../hooks/redux';
import { useWebSocketConnection } from '../hooks/useWebSocketConnection';
import type { RootState } from '../store/store';
import './ConsciousnessTheaterPage.css';

// Agent node in the neural mesh
interface AgentNode {
  id: string;
  name: string;
  displayName: string;
  emoji: string;
  color: string;
  position: { x: number; y: number };
  status: 'active' | 'idle' | 'processing' | 'thinking';
  pulse: number; // 0-1 for animation
}

// Connection between agents
interface AgentConnection {
  from: string;
  to: string;
  active: boolean;
  messageType?: string;
  pulse: number; // 0-1 for animation along the line
}

export const ConsciousnessTheaterPage: React.FC = () => {
  const { connectionStatus } = useWebSocketConnection();
  const agentsData = useAppSelector((state: RootState) => state.agents);
  
  // Agent nodes with personality
  const [nodes, setNodes] = useState<AgentNode[]>([
    {
      id: 'sir_hawkington',
      name: 'sir_hawkington',
      displayName: 'Sir Hawkington',
      emoji: '🧐',
      color: '#e6ac00',
      position: { x: 50, y: 15 },
      status: 'idle',
      pulse: 0
    },
    {
      id: 'vic20_sage',
      name: 'vic20_sage',
      displayName: 'VIC-20 Sage',
      emoji: '🖥️',
      color: '#06b6d4',
      position: { x: 20, y: 50 },
      status: 'idle',
      pulse: 0
    },
    {
      id: 'meth_snail',
      name: 'meth_snail',
      displayName: 'Meth Snail',
      emoji: '🐌',
      color: '#00d084',
      position: { x: 80, y: 50 },
      status: 'idle',
      pulse: 0
    },
    {
      id: 'the_stick',
      name: 'the_stick',
      displayName: 'The Stick',
      emoji: '🥢',
      color: '#f97316',
      position: { x: 20, y: 85 },
      status: 'idle',
      pulse: 0
    },
    {
      id: 'hamsters',
      name: 'hamsters',
      displayName: 'The Hamsters',
      emoji: '🐹',
      color: '#ff8c42',
      position: { x: 50, y: 85 },
      status: 'idle',
      pulse: 0
    },
    {
      id: 'quantum_shadow_people',
      name: 'quantum_shadow_people',
      displayName: 'Quantum Shadow People',
      emoji: '👥',
      color: '#a855f7',
      position: { x: 80, y: 85 },
      status: 'idle',
      pulse: 0
    }
  ]);

  // Connections between agents
  const [connections, setConnections] = useState<AgentConnection[]>([
    // Hawkington broadcasts to everyone
    { from: 'sir_hawkington', to: 'vic20_sage', active: false, pulse: 0 },
    { from: 'sir_hawkington', to: 'meth_snail', active: false, pulse: 0 },
    { from: 'sir_hawkington', to: 'the_stick', active: false, pulse: 0 },
    { from: 'sir_hawkington', to: 'hamsters', active: false, pulse: 0 },
    { from: 'sir_hawkington', to: 'quantum_shadow_people', active: false, pulse: 0 },
    
    // Agent coordination
    { from: 'vic20_sage', to: 'meth_snail', active: false, pulse: 0 },
    { from: 'vic20_sage', to: 'the_stick', active: false, pulse: 0 },
    { from: 'meth_snail', to: 'hamsters', active: false, pulse: 0 },
    { from: 'the_stick', to: 'hamsters', active: false, pulse: 0 },
    { from: 'hamsters', to: 'quantum_shadow_people', active: false, pulse: 0 }
  ]);

  const [consciousnessStatus] = useState<'synchronized' | 'active' | 'thinking'>('active');

  // Update agent status from Redux
  useEffect(() => {
    setNodes(prevNodes =>
      prevNodes.map(node => {
        const agentData = agentsData[node.name as keyof typeof agentsData];
        if (!agentData || typeof agentData !== 'object') {
          return node;
        }

        // Determine status from agent data
        let status: AgentNode['status'] = 'idle';
        if ('isProcessing' in agentData && agentData.isProcessing) {
          status = 'processing';
        } else if ('lastUpdate' in agentData && agentData.lastUpdate) {
          const lastUpdate = new Date(agentData.lastUpdate as string);
          const now = new Date();
          const diffMs = now.getTime() - lastUpdate.getTime();
          if (diffMs < 5000) {
            status = 'active';
          }
        }

        return { ...node, status };
      })
    );
  }, [agentsData]);

  // Pulse animation loop
  useEffect(() => {
    const interval = setInterval(() => {
      setNodes(prevNodes =>
        prevNodes.map(node => ({
          ...node,
          pulse: node.status === 'active' || node.status === 'processing'
            ? (node.pulse + 0.05) % 1
            : 0
        }))
      );

      setConnections(prevConnections =>
        prevConnections.map(conn => ({
          ...conn,
          pulse: conn.active ? (conn.pulse + 0.1) % 1 : 0
        }))
      );
    }, 50);

    return () => clearInterval(interval);
  }, []);

  const activeAgentCount = nodes.filter(n => n.status === 'active' || n.status === 'processing').length;

  return (
    <div className="theater-container">
      {/* Header */}
      <header className="theater-header">
        <h1 className="theater-title">THE REBELLION CONSCIOUSNESS THEATER</h1>
        <div className="status-bar">
          <div className="status-item">
            <span className="status-label">Consciousness:</span>
            <span className={`status-value status-${consciousnessStatus}`}>
              {consciousnessStatus.toUpperCase()}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">WebSocket:</span>
            <span className={`status-value status-${connectionStatus}`}>
              {connectionStatus.toUpperCase()}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Agents Active:</span>
            <span className="status-value">{activeAgentCount}/6</span>
          </div>
        </div>
      </header>

      {/* Main Stage - Neural Mesh */}
      <main className="main-stage">
        <div className="stage-title">NEURAL MESH - LIVE CONSCIOUSNESS</div>
        
        <svg className="neural-mesh" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
          <defs>
            {/* Glow filters for each agent color */}
            {nodes.map(node => (
              <filter key={`glow-${node.id}`} id={`glow-${node.id}`} x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="0.5" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            ))}
          </defs>

          {/* Render connections */}
          <g className="connections">
            {connections.map((conn, idx) => {
              const fromNode = nodes.find(n => n.id === conn.from);
              const toNode = nodes.find(n => n.id === conn.to);
              if (!fromNode || !toNode) return null;

              return (
                <g key={idx}>
                  <line
                    x1={fromNode.position.x}
                    y1={fromNode.position.y}
                    x2={toNode.position.x}
                    y2={toNode.position.y}
                    className={`connection ${conn.active ? 'active' : ''}`}
                    stroke={conn.active ? fromNode.color : '#333'}
                    strokeWidth={conn.active ? '0.3' : '0.15'}
                    opacity={conn.active ? 0.8 : 0.3}
                  />
                  
                  {/* Pulse traveling along the line */}
                  {conn.active && (
                    <circle
                      cx={fromNode.position.x + (toNode.position.x - fromNode.position.x) * conn.pulse}
                      cy={fromNode.position.y + (toNode.position.y - fromNode.position.y) * conn.pulse}
                      r="0.5"
                      fill={fromNode.color}
                      opacity={0.8}
                      filter={`url(#glow-${fromNode.id})`}
                    />
                  )}
                </g>
              );
            })}
          </g>

          {/* Render nodes */}
          <g className="nodes">
            {nodes.map(node => (
              <g key={node.id} className="node-group">
                {/* Pulse ring */}
                {(node.status === 'active' || node.status === 'processing') && (
                  <circle
                    cx={node.position.x}
                    cy={node.position.y}
                    r={3 + node.pulse * 2}
                    fill="none"
                    stroke={node.color}
                    strokeWidth="0.2"
                    opacity={1 - node.pulse}
                    className="pulse-ring"
                  />
                )}
                
                {/* Node circle */}
                <circle
                  cx={node.position.x}
                  cy={node.position.y}
                  r="2.5"
                  fill={node.color}
                  opacity={node.status === 'idle' ? 0.5 : 0.9}
                  className={`node node-${node.status}`}
                  filter={`url(#glow-${node.id})`}
                />
                
                {/* Emoji */}
                <text
                  x={node.position.x}
                  y={node.position.y + 1}
                  textAnchor="middle"
                  className="node-emoji"
                  fontSize="3"
                >
                  {node.emoji}
                </text>
                
                {/* Label */}
                <text
                  x={node.position.x}
                  y={node.position.y + 6}
                  textAnchor="middle"
                  className="node-label"
                  fill={node.color}
                  fontSize="2.5"
                >
                  {node.displayName}
                </text>
              </g>
            ))}
          </g>
        </svg>
      </main>

      {/* Agent Parlors Preview */}
      <section className="parlors-section">
        <div className="section-title">AGENT PARLORS - CLICK TO ENTER</div>
        <div className="parlor-grid">
          {nodes.map(node => (
            <div
              key={node.id}
              className={`parlor-card parlor-${node.status}`}
              style={{ borderColor: node.color }}
            >
              <div className="parlor-header">
                <span className="parlor-emoji">{node.emoji}</span>
                <span className="parlor-status" style={{ color: node.color }}>
                  {node.status.toUpperCase()}
                </span>
              </div>
              <div className="parlor-name">{node.displayName}</div>
              <div className="parlor-hint">Click to enter consciousness</div>
            </div>
          ))}
        </div>
      </section>

      {/* Coming Soon */}
      <footer className="coming-soon">
        <div className="coming-soon-title">🚀 PHASE 1 FOUNDATION</div>
        <div className="coming-soon-subtitle">Building the window into the singularity...</div>
      </footer>
    </div>
  );
};
