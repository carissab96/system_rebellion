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
  type ConnectionPulse,
} from '../../store/slices/communicationSlice';
import styles from '../../styles/modules/TopologyMesh.module.css';

// Agent icons
import sirHawkingtonIcon from '../../assets/icons/agents/sir_hawkington.jpeg';
import vic20SageIcon from '../../assets/icons/agents/vic_20_sage.png';
import terryMethSnailIcon from '../../assets/icons/agents/terry_meth_snail.png';
import theStickIcon from '../../assets/icons/agents/the_stick.png';
import hamstersIcon from '../../assets/icons/agents/hamsters.png';
import qspIcon from '../../assets/icons/agents/qsp.png';

// Agent configuration - NO EMOJIS
const AGENT_CONFIG: Record<string, {
  displayName: string;
  icon: string;
  styleClass: string;
  color: string;
  role: string;
}> = {
  sir_hawkington: {
    displayName: 'Sir Hawkington',
    icon: sirHawkingtonIcon,
    styleClass: 'sirHawkington',
    color: '#e6ac00',
    role: 'System Monitor & Triage',
  },
  vic_20_sage: {
    displayName: 'VIC-20 Sage',
    icon: vic20SageIcon,
    styleClass: 'vic20Sage',
    color: '#06b6d4',
    role: 'Coordinator',
  },
  meth_snail: {
    displayName: 'Terry',
    icon: terryMethSnailIcon,
    styleClass: 'methSnail',
    color: '#00d084',
    role: 'Memory Specialist',
  },
  the_stick: {
    displayName: 'The Stick',
    icon: theStickIcon,
    styleClass: 'theStick',
    color: '#f97316',
    role: 'Universal Logger',
  },
  hamsters: {
    displayName: 'The Hamsters',
    icon: hamstersIcon,
    styleClass: 'hamsters',
    color: '#ff8c42',
    role: 'Consensus Engine',
  },
  quantum_shadow_people: {
    displayName: 'QSP',
    icon: qspIcon,
    styleClass: 'quantumShadowPeople',
    color: '#a855f7',
    role: 'Security & Anomaly',
  },
};

// Node positions (percentage-based for responsive layout)
const NODE_POSITIONS: Record<string, { x: number; y: number }> = {
  sir_hawkington: { x: 50, y: 12 },
  the_stick: { x: 75, y: 28 },
  vic_20_sage: { x: 50, y: 45 },
  meth_snail: { x: 20, y: 75 },
  hamsters: { x: 50, y: 80 },
  quantum_shadow_people: { x: 80, y: 75 },
};

// Connection definitions (who can talk to whom)
const CONNECTIONS: Array<{ from: string; to: string; type: 'command' | 'report' | 'log' }> = [
  // Hawk → VIC-20 (triage alerts)
  { from: 'sir_hawkington', to: 'vic_20_sage', type: 'command' },
  // Hawk → Stick (decision logs)
  { from: 'sir_hawkington', to: 'the_stick', type: 'log' },
  
  // VIC-20 → Specialists (coordination)
  { from: 'vic_20_sage', to: 'meth_snail', type: 'command' },
  { from: 'vic_20_sage', to: 'hamsters', type: 'command' },
  { from: 'vic_20_sage', to: 'quantum_shadow_people', type: 'command' },
  // VIC-20 → Stick (logs)
  { from: 'vic_20_sage', to: 'the_stick', type: 'log' },
  
  // Specialists → VIC-20 (reports)
  { from: 'meth_snail', to: 'vic_20_sage', type: 'report' },
  { from: 'hamsters', to: 'vic_20_sage', type: 'report' },
  { from: 'quantum_shadow_people', to: 'vic_20_sage', type: 'report' },
  
  // Specialists → Stick (logs)
  { from: 'meth_snail', to: 'the_stick', type: 'log' },
  { from: 'hamsters', to: 'the_stick', type: 'log' },
  { from: 'quantum_shadow_people', to: 'the_stick', type: 'log' },
];

// Connection type colors
const CONNECTION_TYPE_COLORS: Record<string, string> = {
  command: '#e6ac00',   // Hawkington gold
  report: '#00d084',    // Snail electric
  log: '#f97316',       // Stick coral
};

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
  
  // Force re-render for pulse animations
  const [, setTick] = useState(0);
  
  // Cleanup expired pulses and trigger re-renders for animations
  useEffect(() => {
    const interval = setInterval(() => {
      dispatch(cleanupPulses());
      setTick(t => t + 1); // Force re-render for smooth animations
    }, 50); // 20fps for smooth pulse travel
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
  
  // Check if an agent is currently involved in any communication
  const isAgentCommunicating = useCallback((agentName: string): boolean => {
    return activePulses.some(
      p => p.from_agent === agentName || p.to_agent === agentName
    );
  }, [activePulses]);
  
  // Get active pulse for a specific connection
  const getActivePulseForConnection = useCallback((from: string, to: string): ConnectionPulse | undefined => {
    return activePulses.find(
      p => p.from_agent === from && p.to_agent === to
    );
  }, [activePulses]);
  
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
    
    const midX = (fromPos.x + toPos.x) / 2;
    const midY = (fromPos.y + toPos.y) / 2;
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;
    
    const offset = Math.min(Math.abs(dx), Math.abs(dy)) * 0.3;
    const ctrlX = midX + (dy > 0 ? offset : -offset) * 0.5;
    const ctrlY = midY + (dx > 0 ? -offset : offset) * 0.5;
    
    return `M ${fromPos.x} ${fromPos.y} Q ${ctrlX} ${ctrlY} ${toPos.x} ${toPos.y}`;
  }, []);
  
  // Calculate position along a quadratic bezier curve
  const getPointOnPath = useCallback((from: string, to: string, t: number): { x: number; y: number } | null => {
    const fromPos = NODE_POSITIONS[from];
    const toPos = NODE_POSITIONS[to];
    if (!fromPos || !toPos) return null;
    
    const midX = (fromPos.x + toPos.x) / 2;
    const midY = (fromPos.y + toPos.y) / 2;
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;
    
    const offset = Math.min(Math.abs(dx), Math.abs(dy)) * 0.3;
    const ctrlX = midX + (dy > 0 ? offset : -offset) * 0.5;
    const ctrlY = midY + (dx > 0 ? -offset : offset) * 0.5;
    
    // Quadratic bezier formula: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
    const x = Math.pow(1 - t, 2) * fromPos.x + 2 * (1 - t) * t * ctrlX + Math.pow(t, 2) * toPos.x;
    const y = Math.pow(1 - t, 2) * fromPos.y + 2 * (1 - t) * t * ctrlY + Math.pow(t, 2) * toPos.y;
    
    return { x, y };
  }, []);
  
  // Render connection lines with active state
  const renderConnections = useMemo(() => {
    return CONNECTIONS.map((conn, index) => {
      const path = getConnectionPath(conn.from, conn.to);
      const activePulse = getActivePulseForConnection(conn.from, conn.to);
      const isActive = !!activePulse;
      
      // Base styles by connection type
      let strokeDasharray = '';
      let baseOpacity = 0.3;
      let strokeColor = CONNECTION_TYPE_COLORS[conn.type];
      
      if (conn.type === 'log') {
        strokeDasharray = '2 4';
        baseOpacity = 0.2;
      } else if (conn.type === 'report') {
        strokeDasharray = '6 3';
      }
      
      // Active state overrides
      const finalOpacity = isActive ? 1 : baseOpacity;
      const finalStrokeWidth = isActive ? 4 : 2;
      const finalColor = isActive ? activePulse!.color : strokeColor;
      const glowFilter = isActive ? `drop-shadow(0 0 6px ${activePulse!.color})` : 'none';
      
      return (
        <path
          key={`conn-${index}`}
          d={path}
          className={`${styles.connectionLine} ${isActive ? styles.active : ''}`}
          style={{ 
            strokeDasharray,
            opacity: finalOpacity,
            stroke: finalColor,
            strokeWidth: finalStrokeWidth,
            filter: glowFilter,
          }}
          fill="none"
        />
      );
    });
  }, [getConnectionPath, getActivePulseForConnection]);
  
  // Render traveling pulse dots
  const renderTravelingPulses = useMemo(() => {
    const now = Date.now();
    
    return activePulses.map(pulse => {
      const elapsed = now - pulse.startTime;
      const progress = Math.min(elapsed / pulse.duration, 1);
      
      // Don't render if animation is complete
      if (progress >= 1) return null;
      
      const point = getPointOnPath(pulse.from_agent, pulse.to_agent, progress);
      if (!point) return null;
      
      return (
        <circle
          key={pulse.id}
          cx={point.x}
          cy={point.y}
          r={1.5}
          fill={pulse.color}
          className={styles.travelingPulse}
          style={{
            filter: `drop-shadow(0 0 8px ${pulse.color}) drop-shadow(0 0 16px ${pulse.color})`,
          }}
        />
      );
    });
  }, [activePulses, getPointOnPath]);
  
  // Render agent nodes with communicating state
  const renderNodes = useMemo(() => {
    return Object.entries(NODE_POSITIONS).map(([agentName, position]) => {
      const config = AGENT_CONFIG[agentName];
      const agentData = getAgentData(agentName);
      const isActive = agentData?.status === 'active' || agentData?.health === 'healthy';
      const isCommunicating = isAgentCommunicating(agentName);
      
      const nodeClasses = [
        styles.agentNode,
        config?.styleClass ? styles[config.styleClass] : '',
        isActive ? styles.active : '',
        isCommunicating ? styles.communicating : '',
      ].filter(Boolean).join(' ');
      
      return (
        <div
          key={agentName}
          className={nodeClasses}
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
  }, [getAgentData, isAgentCommunicating, onAgentClick, handleMouseEnter]);
  
  // Render tooltip
  const renderTooltip = useMemo(() => {
    if (!hoveredAgent) return null;
    
    const config = AGENT_CONFIG[hoveredAgent];
    const agentData = getAgentData(hoveredAgent);
    const communications = getAgentCommunications(hoveredAgent);
    
    let tooltipX = tooltipPosition.x + 20;
    let tooltipY = tooltipPosition.y - 20;
    
    return (
      <div 
        className={`${styles.tooltip} ${styles.visible}`}
        style={{ left: tooltipX, top: tooltipY }}
      >
        <div className={styles.tooltipHeader}>
          <img 
            src={config?.icon} 
            alt={config?.displayName} 
            className={styles.tooltipIcon}
          />
          <div>
            <div className={styles.tooltipTitle}>{config?.displayName}</div>
            <div style={{ fontSize: '0.625rem', color: 'var(--rebellion-text-dim)' }}>
              {config?.role}
            </div>
          </div>
        </div>
        
        <div className={styles.tooltipStats}>
          {agentData?.health && (
            <div className={styles.tooltipStat}>
              <span className={styles.tooltipStatLabel}>Health</span>
              <span className={styles.tooltipStatValue}>{agentData.health}</span>
            </div>
          )}
          {agentData?.total_decisions !== undefined && (
            <div className={styles.tooltipStat}>
              <span className={styles.tooltipStatLabel}>Decisions</span>
              <span className={styles.tooltipStatValue}>{agentData.total_decisions}</span>
            </div>
          )}
          {agentData?.distributed?.total_messages_sent !== undefined && (
            <div className={styles.tooltipStat}>
              <span className={styles.tooltipStatLabel}>Msgs Sent</span>
              <span className={styles.tooltipStatValue}>{agentData.distributed.total_messages_sent}</span>
            </div>
          )}
          {agentData?.distributed?.total_messages_received !== undefined && (
            <div className={styles.tooltipStat}>
              <span className={styles.tooltipStatLabel}>Msgs Recv</span>
              <span className={styles.tooltipStatValue}>{agentData.distributed.total_messages_received}</span>
            </div>
          )}
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
        {renderTravelingPulses}
      </svg>
      
      {/* Agent Nodes Layer */}
      <div className={styles.nodesLayer}>
        {renderNodes}
      </div>
      
      {/* Tooltip */}
      {renderTooltip}
      
      {/* Legend */}
      <div className={styles.legend}>
        <div className={styles.legendTitle}>Connection Types</div>
        <div className={styles.legendItem}>
          <span className={styles.legendLine} style={{ backgroundColor: 'var(--hawkington-gold)' }} />
          <span>Command</span>
        </div>
        <div className={styles.legendItem}>
          <span 
            className={styles.legendLine} 
            style={{ 
              background: `repeating-linear-gradient(90deg, var(--snail-electric) 0, var(--snail-electric) 6px, transparent 6px, transparent 9px)` 
            }} 
          />
          <span>Report</span>
        </div>
        <div className={styles.legendItem}>
          <span 
            className={styles.legendLine} 
            style={{ 
              background: `repeating-linear-gradient(90deg, var(--stick-coral) 0, var(--stick-coral) 2px, transparent 2px, transparent 6px)` 
            }} 
          />
          <span>Log</span>
        </div>
      </div>
    </div>
  );
};

export default TopologyMesh;