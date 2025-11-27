// components/observatory/NeuralMesh.tsx
// 3D Neural mesh with agent nodes
// Built by: Dell-Sonnet - November 20, 2025
// Enhanced: Cascade - November 27, 2025 - Added connections and message flow

import React, { useMemo, useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { AgentNode } from './AgentNode';
import { useDistributedAgents } from '../../hooks/useDistributedAgents';
import sirHawkingtonIcon from '../../assets/icons/agents/sir_hawkington.jpeg';
import vic20SageIcon from '../../assets/icons/agents/vic_20_sage.png';
import terryMethSnailIcon from '../../assets/icons/agents/terry_meth_snail.png';
import theStickIcon from '../../assets/icons/agents/the_stick.png';
import hamstersIcon from '../../assets/icons/agents/hamsters.png';
import qspIcon from '../../assets/icons/agents/qsp.png';

// Agent colors from design system
// BACKEND IS SOURCE OF TRUTH - Use exact agent_name from API
const AGENT_COLORS: Record<string, string> = {
  sir_hawkington: '#e6ac00',      // Hawkington gold
  vic_20_sage: '#06b6d4',         // VIC-20 cyan
  meth_snail: '#00d084',          // Terry's electric green (backend uses meth_snail)
  the_stick: '#f97316',           // Stick coral
  hamsters: '#ff8c42',            // Hamster amber (backend uses hamsters)
  quantum_shadow_people: '#a855f7' // QSP violet
};

// Agent positions (VIC-20 at center, others orbit)
// BACKEND IS SOURCE OF TRUTH - Use exact agent_name from API
const AGENT_POSITIONS: Record<string, [number, number, number]> = {
  vic_20_sage: [0, 0, 0],                    // Center - orchestrator
  sir_hawkington: [-4, 2, 0],                // Upper left
  meth_snail: [4, 2, 0],                     // Upper right (backend: meth_snail)
  the_stick: [0, -3, 2],                     // Lower center front
  hamsters: [-3, -2, -2],                    // Lower left back (backend: hamsters)
  quantum_shadow_people: [3, -2, -2]         // Lower right back
};

const AGENT_ICONS: Record<string, string> = {
  sir_hawkington: sirHawkingtonIcon,
  vic_20_sage: vic20SageIcon,
  meth_snail: terryMethSnailIcon,            // backend: meth_snail
  the_stick: theStickIcon,
  hamsters: hamstersIcon,                    // backend: hamsters
  quantum_shadow_people: qspIcon
};

interface NeuralMeshProps {
  onAgentClick?: (agentName: string) => void;
}

export const NeuralMesh: React.FC<NeuralMeshProps> = ({ onAgentClick }) => {
  const { agents } = useDistributedAgents();
  const [messageFlows, setMessageFlows] = useState<Array<{
    id: string;
    from: string;
    to: string;
    progress: number;
  }>>([]);

  // Map agent data to renderable format
  const agentNodes = useMemo(() => {
    return agents.map(agent => ({
      name: agent.agent_name,
      position: (AGENT_POSITIONS[agent.agent_name] || [0, 0, 0]) as [number, number, number],
      color: AGENT_COLORS[agent.agent_name as keyof typeof AGENT_COLORS] || '#ffffff',
      isActive: agent.is_active,
      health: agent.health,
      iconUrl: AGENT_ICONS[agent.agent_name] || '',
      messagesSent: agent.distributed?.total_messages_sent || 0
    }));
  }, [agents]);

  // Watch for new messages and create flow effects
  const prevMessageCounts = useRef<Map<string, number>>(new Map());
  
  useEffect(() => {
    agentNodes.forEach(agent => {
      const prevCount = prevMessageCounts.current.get(agent.name) || 0;
      if (agent.messagesSent > prevCount) {
        // New message sent! Create flow effect to VIC-20 (coordinator)
        if (agent.name !== 'vic_20_sage') {
          const flowId = `${agent.name}-${Date.now()}`;
          setMessageFlows(prev => [...prev, {
            id: flowId,
            from: agent.name,
            to: 'vic_20_sage',
            progress: 0
          }]);
          
          // Remove after animation completes
          setTimeout(() => {
            setMessageFlows(prev => prev.filter(f => f.id !== flowId));
          }, 2000);
        }
      }
      prevMessageCounts.current.set(agent.name, agent.messagesSent);
    });
  }, [agentNodes]);

  // Define connections (all agents connect to VIC-20 at center)
  const connections = useMemo(() => {
    return agentNodes
      .filter(agent => agent.name !== 'vic_20_sage')
      .map(agent => ({
        from: agent.position,
        to: AGENT_POSITIONS['vic_20_sage'],
        color: agent.color,
        fromName: agent.name
      }));
  }, [agentNodes]);

  return (
    <>
      {/* Ambient lighting */}
      <ambientLight intensity={0.3} />
      
      {/* Point lights for dramatic effect */}
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#06b6d4" />
      <pointLight position={[-10, -10, -10]} intensity={0.3} color="#a855f7" />
      
      {/* Connection lines between agents */}
      {connections.map((conn, i) => (
        <ConnectionLine
          key={i}
          start={conn.from}
          end={conn.to}
          color={conn.color}
        />
      ))}

      {/* Message flow effects */}
      {messageFlows.map(flow => {
        const fromPos = AGENT_POSITIONS[flow.from];
        const toPos = AGENT_POSITIONS[flow.to];
        if (!fromPos || !toPos) return null;
        
        return (
          <MessageParticle
            key={flow.id}
            start={fromPos}
            end={toPos}
            color={AGENT_COLORS[flow.from] || '#ffffff'}
          />
        );
      })}
      
      {/* Agent nodes */}
      {agentNodes.map(agent => (
        <AgentNode
          key={agent.name}
          agentName={agent.name}
          position={agent.position}
          color={agent.color}
          isActive={agent.isActive}
          health={agent.health}
          iconUrl={agent.iconUrl}
          onClick={() => onAgentClick?.(agent.name)}
        />
      ))}
    </>
  );
};

// Connection line component
interface ConnectionLineProps {
  start: [number, number, number];
  end: [number, number, number];
  color: string;
}

const ConnectionLine: React.FC<ConnectionLineProps> = ({ start, end, color }) => {
  const lineRef = useRef<THREE.Line>(null);
  
  // Pulsing opacity effect
  useFrame((state) => {
    if (lineRef.current && lineRef.current.material) {
      const material = lineRef.current.material as THREE.LineBasicMaterial;
      material.opacity = 0.2 + Math.sin(state.clock.elapsedTime * 2) * 0.1;
    }
  });

  // Create line geometry
  const points = useMemo(() => {
    return [new THREE.Vector3(...start), new THREE.Vector3(...end)];
  }, [start, end]);

  const geometry = useMemo(() => {
    const geom = new THREE.BufferGeometry().setFromPoints(points);
    return geom;
  }, [points]);

  return (
    <primitive object={new THREE.Line(geometry, new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.2 }))} ref={lineRef} />
  );
};

// Message particle that travels along connection
interface MessageParticleProps {
  start: [number, number, number];
  end: [number, number, number];
  color: string;
}

const MessageParticle: React.FC<MessageParticleProps> = ({ start, end, color }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const startTime = useRef(Date.now());

  useFrame(() => {
    if (meshRef.current) {
      const elapsed = (Date.now() - startTime.current) / 2000; // 2 second journey
      const progress = Math.min(elapsed, 1);
      
      // Interpolate position
      meshRef.current.position.x = start[0] + (end[0] - start[0]) * progress;
      meshRef.current.position.y = start[1] + (end[1] - start[1]) * progress;
      meshRef.current.position.z = start[2] + (end[2] - start[2]) * progress;
      
      // Fade out as it reaches destination
      const material = meshRef.current.material as THREE.MeshBasicMaterial;
      material.opacity = 1 - progress;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.1, 8, 8]} />
      <meshBasicMaterial color={color} transparent opacity={1} />
    </mesh>
  );
};
