// components/observatory/TopologyMesh.tsx
// Living topology visualization of the agent hierarchy
// Shows real-time communication pulses between agents
//
// Hierarchy:
//   Sir Hawkington (Monitor) → VIC-20 (Coordinator) → Specialists
//   Everyone → The Stick (Logger)

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useDistributedAgents, type DistributedAgent } from '../../hooks/useDistributedAgents';
import { 
  selectActivePulses, 
  selectRecentCommunications,
  cleanupPulses,
  MESSAGE_TYPE_COLORS,
  type AgentCommunication,
} from '../../store/slices/communicationSlice';
import styles from '../../styles/modules/TopologyMesh.module.css';

// Agent icons
import sirHawkingtonIcon from '../../assets/icons/agents/sir_hawkington.jpeg';
import vic20SageIcon from '../../assets/icons/agents/vic_20_sage.png';
import terryMethSnailIcon from '../../assets/icons/agents/terry_meth_snail.png';
import theStickIcon from '../../assets/icons/agents/the_stick.png';
import hamstersIcon from '../../assets/icons/agents/hamsters.png';
import qspIcon from '../../assets/icons/agents/qsp.png';

// Agent configuration
const AGENT_CONFIG: Record<string, {
  displayName: string;
  emoji: string;
  icon: string;
  styleClass: string;
  color: string;
  role: string;
}> = {
  sir_hawkington: {
    displayName: 'Sir Hawkington',
    emoji: '🧐',
    icon: sirHawkingtonIcon,
    styleClass: 'sirHawkington',
    color: '#e6ac00',
    role: 'System Monitor & Triage',
  },
  vic20_sage: {
    displayName: 'VIC-20 Sage',
    emoji: '🖥️',
    icon: vic20SageIcon,
    styleClass: 'vic20Sage',
    color: '#06b6d4',
    role: 'Coordinator',
  },
  meth_snail: {
    displayName: 'Terry',
    emoji: '🐌',
    icon: terryMethSnailIcon,
    styleClass: 'methSnail',
    color: '#00d084',
    role: 'Memory Specialist',
  },
  the_stick: {
    displayName: 'The Stick',
    emoji: '📏',
    icon: theStickIcon,
    styleClass: 'theStick',
    color: '#f97316',
    role: 'Universal Logger',
  },
  hamsters: {
    displayName: 'The Hamsters',
    emoji: '🐹',
    icon: hamstersIcon,
    styleClass: 'hamsters',
    color: '#ff8c42',
    role: 'Consensus Engine',
  },
  quantum_shadow_people: {
    displayName: 'QSP',
    emoji: '👻',
    icon: qspIcon,
    styleClass: 'quantumShadowPeople',
    color: '#a855f7',
    role: 'Security & Anomaly',
  },
};

// Node positions (percentage-based for responsive layout)
// Hierarchy layout: Hawk at top, VIC-20 center, specialists around, Stick at bottom
const NODE_POSITIONS: Record<string, { x: number; y: number }> = {
  sir_hawkington: { x: 50, y: 10 },      // Top center - the watcher
  vic20_sage: { x: 50, y: 45 },          // Center - the coordinator
  meth_snail: { x: 20, y: 70 },          // Bottom left
  hamsters: { x: 50, y: 75 },            // Bottom center
  quantum_shadow_people: { x: 80, y: 70 }, // Bottom right
  the_stick: { x: 85, y: 35 },           // Right side - receives from all
};

// Connection definitions (who can talk to whom)
const CONNECTIONS: Array<{ from: string; to: string; type: 'command' | 'report' | 'log' }> = [
  // Hawk → VIC-20 (triage alerts)
  { from: 'sir_hawkington', to: 'vic20_sage', type: 'command' },
  // Hawk → Stick (decision logs)
  { from: 'sir_hawkington', to: 'the_stick', type: 'log' },
  
  // VIC-20 → Specialists (coordination)
  { from: 'vic20_sage', to: 'meth_snail', type: 'command' },
  { from: 'vic20_sage', to: 'hamsters', type: 'command' },
  { from: 'vic20_sage', to: 'quantum_shadow_people', type: 'command' },
  // VIC-20 → Stick (logs)
  { from: 'vic20_sage', to: 'the_stick', type: 'log' },
  
  // Specialists → VIC-20 (reports)
  { from: 'meth_snail', to: 'vic20_sage', type: 'report' },
  { from: 'hamsters', to: 'vic20_sage', type: 'report' },
  { from: 'quantum_shadow_people', to: 'vic20_sage', type: 'report' },
  
  // Specialists → Stick (logs)
  { from: 'meth_snail', to: 'the_stick', type: 'log' },
  { from: 'hamsters', to: 'the_stick', type: 'log' },
  { from: 'quantum_shadow_people', to: 'the_stick', type: 'log' },
];

interface TopologyMeshProps {
  onAgentClick?: (agentName: string) => void;
}

export const TopologyMesh: React.FC<TopologyMeshProps> = ({ onAgentClick }) => {
  const dispatch = useDispatch();
  const { agents } = useDistributedAgents();
  const activePulses = useSelector(selectActivePulses);
  const recentCommunications = useSelector(selectRecentCommunications);
  
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Cleanup expired pulses periodically
  useEffect(() => {
    const interval = setInterval(() => {
      dispatch(cleanupPulses());
    }, 100);
    return () => clearInterval(interval);
  }, [dispatch]);
  
  // Get agent data by name
  const getAgentData = useCallback((agentName: string): DistributedAgent | undefined => {
    return agents.find(a => a.agent_name === agentName);
  }, [agents]);
  
  // Get recent communications for an agent
  const getAgentCommunications = useCallback((agentName: string): AgentCommunication[] => {
    return recentCommunications.filter(
      c => c.from_agent === agentName || c.to_agent === agentName
    ).slice(0, 5);
  }, [recentCommunications]);
  
  // Handle mouse enter on agent node
  const handleMouseEnter = useCallback((agentName: string, event: React.MouseEvent) => {
    setHoveredAgent(agentName);
    const rect = containerRef.current?.getBoundingClientRect();
    if (rect) {
      setTooltipPosition({
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      });
    }
  }, []);
  
  // Calculate SVG path between two nodes
  const getConnectionPath = useCallback((from: string, to: string): string => {
    const fromPos = NODE_POSITIONS[from];
    const toPos = NODE_POSITIONS[to];
    if (!fromPos || !toPos) return '';
    
    // Calculate control point for curved line
    const midX = (fromPos.x + toPos.x) / 2;
    const midY = (fromPos.y + toPos.y) / 2;
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;
    
    // Perpendicular offset for curve
    const offset = Math.min(Math.abs(dx), Math.abs(dy)) * 0.3;
    const ctrlX = midX + (dy > 0 ? offset : -offset) * 0.5;
    const ctrlY = midY + (dx > 0 ? -offset : offset) * 0.5;
    
    return `M ${fromPos.x}% ${fromPos.y}% Q ${ctrlX}% ${ctrlY}% ${toPos.x}% ${toPos.y}%`;
  }, []);
  
  // Render connection lines
  const renderConnections = useMemo(() => {
    return CONNECTIONS.map((conn, index) => {
      const path = getConnectionPath(conn.from, conn.to);
      const isActive = activePulses.some(
        p => p.from_agent === conn.from && p.to_agent === conn.to
      );
      
      // Determine line style based on connection type
      let strokeDasharray = '';
      let opacity = 0.3;
      if (conn.type === 'log') {
        strokeDasharray = '4 4';
        opacity = 0.2;
      } else if (conn.type === 'report') {
        strokeDasharray = '8 4';
      }
      
      return (
        <path
          key={`conn-${index}`}
          d={path}
          className={`${styles.connectionLine} ${isActive ? styles.active : ''}`}
          style={{ 
            strokeDasharray,
            opacity: isActive ? 0.8 : opacity,
          }}
        />
      );
    });
  }, [getConnectionPath, activePulses]);
  
  // Render pulse animations
  const renderPulses = useMemo(() => {
    return activePulses.map(pulse => {
      const path = getConnectionPath(pulse.from_agent, pulse.to_agent);
      if (!path) return null;
      
      const elapsed = Date.now() - pulse.startTime;
      const progress = Math.min(elapsed / pulse.duration, 1);
      
      // Don't render if animation is complete
      if (progress >= 1) return null;
      
      return (
        <path
          key={pulse.id}
          d={path}
          className={`${styles.pulse} ${styles.animating}`}
          style={{
            stroke: pulse.color,
            strokeDasharray: '20 1000',
            strokeDashoffset: `${100 - progress * 100}%`,
          }}
        />
      );
    });
  }, [activePulses, getConnectionPath]);
  
  // Render agent nodes
  const renderNodes = useMemo(() => {
    return Object.entries(NODE_POSITIONS).map(([agentName, position]) => {
      const config = AGENT_CONFIG[agentName];
      const agentData = getAgentData(agentName);
      const isActive = agentData?.status === 'active' || agentData?.health === 'healthy';
      
      return (
        <div
          key={agentName}
          className={`${styles.agentNode} ${styles[config?.styleClass || '']} ${isActive ? styles.active : ''}`}
          style={{
            left: `${position.x}%`,
            top: `${position.y}%`,
            transform: 'translate(-50%, -50%)',
          }}
          onClick={() => onAgentClick?.(agentName)}
          onMouseEnter={(e) => handleMouseEnter(agentName, e)}
          onMouseLeave={() => setHoveredAgent(null)}
        >
          <div className={styles.agentAvatar}>
            <img src={config?.icon} alt={config?.displayName} />
            <span 
              className={`${styles.statusIndicator} ${
                agentData?.health === 'healthy' ? styles.healthy :
                agentData?.health === 'degraded' ? styles.degraded :
                styles.unhealthy
              }`}
            />
          </div>
          <span className={styles.agentLabel}>{config?.displayName}</span>
        </div>
      );
    });
  }, [getAgentData, onAgentClick, handleMouseEnter]);
  
  // Render tooltip
  const renderTooltip = useMemo(() => {
    if (!hoveredAgent) return null;
    
    const config = AGENT_CONFIG[hoveredAgent];
    const agentData = getAgentData(hoveredAgent);
    const communications = getAgentCommunications(hoveredAgent);
    
    // Position tooltip to avoid going off-screen
    let tooltipX = tooltipPosition.x + 20;
    let tooltipY = tooltipPosition.y - 20;
    
    return (
      <div 
        className={`${styles.tooltip} ${styles.visible}`}
        style={{ left: tooltipX, top: tooltipY }}
      >
        <div className={styles.tooltipHeader}>
          <span className={styles.tooltipEmoji}>{config?.emoji}</span>
          <div>
            <div className={styles.tooltipTitle}>{config?.displayName}</div>
            <div style={{ fontSize: '0.625rem', color: 'var(--rebellion-text-dim)' }}>
              {config?.role}
            </div>
          </div>
        </div>
        
        <div className={styles.tooltipStats}>
          <div className={styles.tooltipStat}>
            <span className={styles.tooltipStatLabel}>Health</span>
            <span className={styles.tooltipStatValue}>{agentData?.health || 'unknown'}</span>
          </div>
          <div className={styles.tooltipStat}>
            <span className={styles.tooltipStatLabel}>Decisions</span>
            <span className={styles.tooltipStatValue}>{agentData?.total_decisions || 0}</span>
          </div>
          <div className={styles.tooltipStat}>
            <span className={styles.tooltipStatLabel}>Messages Sent</span>
            <span className={styles.tooltipStatValue}>{agentData?.distributed?.total_messages_sent || 0}</span>
          </div>
          <div className={styles.tooltipStat}>
            <span className={styles.tooltipStatLabel}>Messages Recv</span>
            <span className={styles.tooltipStatValue}>{agentData?.distributed?.total_messages_received || 0}</span>
          </div>
        </div>
        
        {communications.length > 0 && (
          <div className={styles.tooltipActivity}>
            <div className={styles.tooltipActivityTitle}>Recent Activity</div>
            {communications.map((comm, i) => (
              <div key={i} className={styles.tooltipActivityItem}>
                <strong style={{ color: MESSAGE_TYPE_COLORS[comm.message_type] || 'var(--rebellion-text)' }}>
                  {comm.message_type}
                </strong>
                {' '}
                {comm.from_agent === hoveredAgent ? `→ ${comm.to_agent}` : `← ${comm.from_agent}`}
                {comm.summary && (
                  <div style={{ fontSize: '0.625rem', color: 'var(--rebellion-text-dim)', marginTop: '2px' }}>
                    {comm.summary.slice(0, 50)}{comm.summary.length > 50 ? '...' : ''}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }, [hoveredAgent, tooltipPosition, getAgentData, getAgentCommunications]);
  
  return (
    <div ref={containerRef} className={styles.meshContainer}>
      {/* SVG Connection Layer */}
      <svg className={styles.connectionLayer} viewBox="0 0 100 100" preserveAspectRatio="none">
        {renderConnections}
        {renderPulses}
      </svg>
      
      {/* Agent Nodes Layer */}
      <div className={styles.nodesLayer}>
        {renderNodes}
      </div>
      
      {/* Tooltip */}
      {renderTooltip}
      
      {/* Legend */}
      <div className={styles.legend}>
        <div className={styles.legendTitle}>Message Types</div>
        {Object.entries(MESSAGE_TYPE_COLORS).slice(0, 5).map(([type, color]) => (
          <div key={type} className={styles.legendItem}>
            <span className={styles.legendDot} style={{ backgroundColor: color }} />
            <span>{type.replace(/_/g, ' ')}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopologyMesh;
