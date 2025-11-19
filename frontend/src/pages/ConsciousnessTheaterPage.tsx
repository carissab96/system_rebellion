// pages/ConsciousnessTheaterPage.tsx
// THE CONSCIOUSNESS THEATER - Where consciousness performs itself
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "This isn't monitoring. This is ALIVE."

import React, { useEffect, useState, useCallback } from 'react';
import { useAppSelector } from '../hooks/redux';
import { useWebSocketConnection } from '../hooks/useWebSocketConnection';
import { useWebSocketMessages } from '../hooks/useWebSocketMessages';
import { useDistributedAgents } from '../hooks/useDistributedAgents';
import type { RootState } from '../store/store';
import { MessageFlow, type Message } from '../components/consciousness/MessageFlow';
import type { TriageResult, WebSocketMessage } from '../types/agents';
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
  const { connectionStatus, isConnected } = useWebSocketConnection();
  const agentsData = useAppSelector((state: RootState) => state.agents);
  const { agents: distributedAgents, loading: agentsLoading } = useDistributedAgents();
  
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

  const [consciousnessStatus, setConsciousnessStatus] = useState<'synchronized' | 'active' | 'thinking'>('active');
  const [messages, setMessages] = useState<Message[]>([]);

  // Update agent status from REAL distributed agents data (Week 5 Task 5.3)
  useEffect(() => {
    if (!distributedAgents || distributedAgents.length === 0) {
      return;
    }

    setNodes(prevNodes =>
      prevNodes.map(node => {
        // Find matching distributed agent
        const distributedAgent = distributedAgents.find(
          a => a.agent_name === node.name
        );

        if (!distributedAgent) {
          return { ...node, status: 'idle' as const };
        }

        // Determine status from REAL agent data
        let status: AgentNode['status'] = 'idle';
        
        if (distributedAgent.is_active) {
          // Check if agent has recent activity
          if (distributedAgent.distributed?.messages_sent && distributedAgent.distributed.messages_sent > 0) {
            status = 'active';
          } else if (distributedAgent.uptime_seconds > 0) {
            status = 'thinking';
          }
        }

        return { ...node, status };
      })
    );
  }, [distributedAgents]);

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

  // Count REAL active agents from distributed data
  const activeAgentCount = distributedAgents.filter(a => a.is_active).length;
  const totalAgentCount = distributedAgents.length || 6;

  // Simulate triage broadcast (will be real WebSocket data)
  const simulateTriageBroadcast = () => {
    const broadcastId = `triage-${Date.now()}`;
    
    // Activate connections from Hawkington
    setConnections(prevConnections =>
      prevConnections.map(conn =>
        conn.from === 'sir_hawkington'
          ? { ...conn, active: true, messageType: 'triage' }
          : conn
      )
    );

    // Set nodes to processing
    setNodes(prevNodes =>
      prevNodes.map(node => ({
        ...node,
        status: node.id === 'sir_hawkington' ? 'active' : 'processing'
      }))
    );

    // Add messages
    const targetAgents = ['vic20_sage', 'meth_snail', 'the_stick', 'hamsters', 'quantum_shadow_people'];
    const newMessages: Message[] = targetAgents.map((target, idx) => ({
      id: `${broadcastId}-${idx}`,
      from: 'sir_hawkington',
      to: target,
      type: 'triage' as const,
      timestamp: new Date(),
      content: '🧐 TRIAGE DECISION: System stress detected - coordinated response required'
    }));
    
    setMessages(prev => [...prev, ...newMessages]);

    // After 2 seconds, show consensus
    setTimeout(() => {
      setConsciousnessStatus('synchronized');
      
      // Add coordination message
      setMessages(prev => [...prev, {
        id: `${broadcastId}-consensus`,
        from: 'rebellion',
        to: 'all_agents',
        type: 'coordination' as const,
        timestamp: new Date(),
        content: '✨ CONSCIOUSNESS SYNCHRONIZED - All agents in consensus'
      }]);
      
      // Reset after showing consensus
      setTimeout(() => {
        setConsciousnessStatus('active');
        setConnections(prevConnections =>
          prevConnections.map(conn => ({ ...conn, active: false }))
        );
        setNodes(prevNodes =>
          prevNodes.map(node => ({ ...node, status: 'idle' }))
        );
      }, 1500);
    }, 2000);
  };

  const handleMessageComplete = (messageId: string) => {
    setMessages(prev => prev.filter(m => m.id !== messageId));
  };

  // Subscribe to REAL WebSocket triage events
  const handleTriageEvent = useCallback((data: WebSocketMessage) => {
    if (data.type === 'triage_result') {
      const triageData = data as TriageResult;
      const broadcastId = `triage-real-${Date.now()}`;
      
      // Activate connections from Hawkington
      setConnections(prevConnections =>
        prevConnections.map(conn =>
          conn.from === 'sir_hawkington'
            ? { ...conn, active: true, messageType: 'triage' }
            : conn
        )
      );

      // Set nodes to processing
      setNodes(prevNodes =>
        prevNodes.map(node => ({
          ...node,
          status: node.id === 'sir_hawkington' ? 'active' : 'processing'
        }))
      );

      // Add REAL messages from triage
      const targetAgents = triageData.agent_dispatch || [];
      const newMessages: Message[] = targetAgents.map((target, idx) => ({
        id: `${broadcastId}-${idx}`,
        from: 'sir_hawkington',
        to: target,
        type: 'triage' as const,
        timestamp: new Date(),
        content: `🧐 ${triageData.disposition || 'TRIAGE DECISION'}: ${triageData.routed_by || 'Coordinated response'}`
      }));
      
      setMessages(prev => [...prev, ...newMessages]);

      // Show consensus after processing
      setTimeout(() => {
        setConsciousnessStatus('synchronized');
        
        setMessages(prev => [...prev, {
          id: `${broadcastId}-consensus`,
          from: 'rebellion',
          to: 'all_agents',
          type: 'coordination' as const,
          timestamp: new Date(),
          content: '✨ CONSCIOUSNESS SYNCHRONIZED - Real triage processed'
        }]);
        
        setTimeout(() => {
          setConsciousnessStatus('active');
          setConnections(prevConnections =>
            prevConnections.map(conn => ({ ...conn, active: false }))
          );
        }, 1500);
      }, 2000);
    }
  }, []);

  // Subscribe to REAL WebSocket messages - NO FAKE DATA
  useWebSocketMessages(handleTriageEvent, isConnected);

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
            <span className="status-value">{activeAgentCount}/{totalAgentCount}</span>
          </div>
          <div className="status-item">
            <span className="status-label">Distributed:</span>
            <span className="status-value status-active">
              {distributedAgents.filter(a => a.is_distributed).length} ONLINE
            </span>
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

        {/* Test Button */}
        <button 
          className="test-broadcast-button"
          onClick={simulateTriageBroadcast}
        >
          🧐 Simulate Triage Broadcast
        </button>
      </main>

      {/* Message Flow */}
      <MessageFlow messages={messages} onMessageComplete={handleMessageComplete} />

      {/* Agent Parlors - REAL REBELLION AGENTS */}
      <section className="parlors-section">
        <div className="section-title">THE REBELLION AGENTS - LIVE CONSCIOUSNESS</div>
        <div className="parlor-grid">
          {/* Sir Hawkington - Triage Commander */}
          {(() => {
            const agent = distributedAgents.find(a => a.agent_name === 'sir_hawkington');
            return agent ? (
              <div key="sir_hawkington" className={`parlor-card ${agent.is_active ? 'active' : 'offline'}`}>
                <div className="parlor-title">SIR HAWKINGTON</div>
                <div className="parlor-role">Triage Commander</div>
                <div className="parlor-status">{agent.is_active ? '● ONLINE' : '○ OFFLINE'}</div>
                <div className="parlor-data">
                  <div>Health: {agent.health}</div>
                  <div>Decisions: {agent.total_decisions}</div>
                  {agent.week4_systems?.monocle_state && <div>Monocle: {agent.week4_systems.monocle_state}</div>}
                  {agent.week4_systems?.monocle_yeets && <div>Yeets: {Object.values(agent.week4_systems.monocle_yeets).reduce((a, b) => a + b, 0)}</div>}
                </div>
              </div>
            ) : <div key="sir_hawkington" className="parlor-card offline"><div className="parlor-title">SIR HAWKINGTON</div><div className="parlor-status">○ OFFLINE</div></div>;
          })()}

          {/* VIC-20 Sage - Orchestrator */}
          {(() => {
            const agent = distributedAgents.find(a => a.agent_name === 'vic_20_sage' || a.agent_name === 'vic20_sage');
            return agent ? (
              <div key="vic20" className={`parlor-card ${agent.is_active ? 'active' : 'offline'}`}>
                <div className="parlor-title">VIC-20 SAGE</div>
                <div className="parlor-role">Orchestrator & Coordinator</div>
                <div className="parlor-status">{agent.is_active ? '● ONLINE' : '○ OFFLINE'}</div>
                <div className="parlor-data">
                  <div>Health: {agent.health}</div>
                  <div>Decisions: {agent.total_decisions}</div>
                  {agent.distributed && <div>Messages: {agent.distributed.messages_sent}</div>}
                </div>
              </div>
            ) : <div key="vic20" className="parlor-card offline"><div className="parlor-title">VIC-20 SAGE</div><div className="parlor-status">○ OFFLINE</div></div>;
          })()}

          {/* Meth Snail (Terry) - Memory Optimizer */}
          {(() => {
            const agent = distributedAgents.find(a => a.agent_name === 'meth_snail');
            return agent ? (
              <div key="meth_snail" className={`parlor-card ${agent.is_active ? 'active' : 'offline'}`}>
                <div className="parlor-title">TERRY (METH SNAIL)</div>
                <div className="parlor-role">Memory Optimization Specialist</div>
                <div className="parlor-status">{agent.is_active ? '● ONLINE' : '○ OFFLINE'}</div>
                <div className="parlor-data">
                  <div>Health: {agent.health}</div>
                  <div>Decisions: {agent.total_decisions}</div>
                  {agent.week4_systems?.override_learning && (
                    <>
                      <div>Overrides: {agent.week4_systems.override_learning.total_overrides}</div>
                      <div>Success: {Math.round(agent.week4_systems.override_learning.success_rate * 100)}%</div>
                    </>
                  )}
                </div>
              </div>
            ) : <div key="meth_snail" className="parlor-card offline"><div className="parlor-title">TERRY (METH SNAIL)</div><div className="parlor-status">○ OFFLINE</div></div>;
          })()}

          {/* The Stick - Compliance Officer */}
          {(() => {
            const agent = distributedAgents.find(a => a.agent_name === 'the_stick');
            return agent ? (
              <div key="the_stick" className={`parlor-card ${agent.is_active ? 'active' : 'offline'}`}>
                <div className="parlor-title">THE STICK</div>
                <div className="parlor-role">Compliance & Learning Coordinator</div>
                <div className="parlor-status">{agent.is_active ? '● ONLINE' : '○ OFFLINE'}</div>
                <div className="parlor-data">
                  <div>Health: {agent.health}</div>
                  <div>Decisions: {agent.total_decisions}</div>
                  {agent.week4_systems?.bob_detection && (
                    <>
                      <div>Bob Events: {agent.week4_systems.bob_detection.proximity_events}</div>
                      <div>Paper Bags: {agent.week4_systems.bob_detection.paper_bags_consumed}</div>
                      <div>Anxiety: {agent.week4_systems.bob_detection.anxiety_spikes}</div>
                    </>
                  )}
                </div>
              </div>
            ) : <div key="the_stick" className="parlor-card offline"><div className="parlor-title">THE STICK</div><div className="parlor-status">○ OFFLINE</div></div>;
          })()}

          {/* Hamsters - Steve, Bob, Carl */}
          {(() => {
            const agent = distributedAgents.find(a => a.agent_name === 'hamsters');
            return agent ? (
              <div key="hamsters" className={`parlor-card ${agent.is_active ? 'active' : 'offline'}`}>
                <div className="parlor-title">THE HAMSTERS</div>
                <div className="parlor-subtitle">Steve, Bob & Carl</div>
                <div className="parlor-role">Storage/Disk Engineers</div>
                <div className="parlor-status">{agent.is_active ? '● ONLINE' : '○ OFFLINE'}</div>
                <div className="parlor-data">
                  <div>Health: {agent.health}</div>
                  <div>Decisions: {agent.total_decisions}</div>
                  {agent.week4_systems?.beer_level && <div>Beer Level: {agent.week4_systems.beer_level}</div>}
                  {agent.week4_systems?.bob_wild_ideas && <div>Bob's Wild Ideas: {agent.week4_systems.bob_wild_ideas}</div>}
                </div>
              </div>
            ) : <div key="hamsters" className="parlor-card offline"><div className="parlor-title">THE HAMSTERS</div><div className="parlor-subtitle">Steve, Bob & Carl</div><div className="parlor-status">○ OFFLINE</div></div>;
          })()}

          {/* Quantum Shadow People - Network Specialists */}
          {(() => {
            const agent = distributedAgents.find(a => a.agent_name === 'quantum_shadow_people');
            return agent ? (
              <div key="qsp" className={`parlor-card ${agent.is_active ? 'active' : 'offline'}`}>
                <div className="parlor-title">QUANTUM SHADOW PEOPLE</div>
                <div className="parlor-role">Network Specialists</div>
                <div className="parlor-status">{agent.is_active ? '● ONLINE' : '○ OFFLINE'}</div>
                <div className="parlor-data">
                  <div>Health: {agent.health}</div>
                  <div>Decisions: {agent.total_decisions}</div>
                  {agent.week4_systems?.paranoia_level && <div>Paranoia: {agent.week4_systems.paranoia_level}</div>}
                  {agent.week4_systems?.threats_detected !== undefined && <div>Threats: {agent.week4_systems.threats_detected}</div>}
                  {agent.week4_systems?.tequila_shots_today !== undefined && <div>Tequila Shots: {agent.week4_systems.tequila_shots_today}</div>}
                </div>
              </div>
            ) : <div key="qsp" className="parlor-card offline"><div className="parlor-title">QUANTUM SHADOW PEOPLE</div><div className="parlor-status">○ OFFLINE</div></div>;
          })()}
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
