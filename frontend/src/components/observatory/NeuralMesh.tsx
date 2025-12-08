// components/observatory/NeuralMesh.tsx
// 3D Neural mesh with agent nodes and particle effects
// Built by: Dell-Sonnet - November 20, 2025
// Enhanced: Cascade - December 7, 2025 - Added particle flow, dynamic positioning

import React, { useMemo, useRef } from 'react';
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
// BACKEND IS SOURCE OF TRUTH - Use exact agent_name from API (vic_20_sage, not vic_20_sage)
const AGENT_COLORS: Record<string, string> = {
  sir_hawkington: '#e6ac00',      // Hawkington gold
  vic_20_sage: '#06b6d4',          // VIC-20 cyan (backend: vic_20_sage)
  meth_snail: '#00d084',          // Terry's electric green
  the_stick: '#f97316',           // Stick coral
  hamsters: '#ff8c42',            // Hamster amber
  quantum_shadow_people: '#a855f7' // QSP violet
};

// Agent positions - dynamic, not hard-coded V formation
// BACKEND IS SOURCE OF TRUTH - Use exact agent_name from API
const AGENT_POSITIONS: Record<string, [number, number, number]> = {
  vic_20_sage: [0, 0, 0],                     // Center - orchestrator
  sir_hawkington: [-3, 3, 1],                // Upper left front
  the_stick: [3, 2, 0],                      // Upper right - logs everything
  meth_snail: [-4, -1, -1],                  // Mid left back
  hamsters: [0, -3, 2],                      // Lower center front
  quantum_shadow_people: [4, -1, -1]         // Mid right back
};

const AGENT_ICONS: Record<string, string> = {
  sir_hawkington: sirHawkingtonIcon,
  vic_20_sage: vic20SageIcon,                 // backend: vic_20_sage
  meth_snail: terryMethSnailIcon,
  the_stick: theStickIcon,
  hamsters: hamstersIcon,
  quantum_shadow_people: qspIcon
};

// Communication paths for particle flow
const COMM_PATHS: Array<{ from: string; to: string; color: string }> = [
  // Hawk → VIC-20 (commands)
  { from: 'sir_hawkington', to: 'vic_20_sage', color: '#e6ac00' },
  // VIC-20 → Specialists (coordination)
  { from: 'vic_20_sage', to: 'meth_snail', color: '#06b6d4' },
  { from: 'vic_20_sage', to: 'hamsters', color: '#06b6d4' },
  { from: 'vic_20_sage', to: 'quantum_shadow_people', color: '#06b6d4' },
  // Specialists → VIC-20 (reports)
  { from: 'meth_snail', to: 'vic_20_sage', color: '#00d084' },
  { from: 'hamsters', to: 'vic_20_sage', color: '#ff8c42' },
  { from: 'quantum_shadow_people', to: 'vic_20_sage', color: '#a855f7' },
  // Everyone → The Stick (logs)
  { from: 'sir_hawkington', to: 'the_stick', color: '#f97316' },
  { from: 'vic_20_sage', to: 'the_stick', color: '#f97316' },
  { from: 'meth_snail', to: 'the_stick', color: '#f97316' },
];

// Particle system for data flow visualization
const ParticleFlow: React.FC<{ paths: typeof COMM_PATHS }> = ({ paths }) => {
  const particlesRef = useRef<THREE.Points>(null);
  const particleCount = paths.length * 8; // 8 particles per path
  
  // Create particle geometry
  const { positions, colors, pathIndices, progress } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const pathIndices = new Float32Array(particleCount);
    const progress = new Float32Array(particleCount);
    
    for (let i = 0; i < particleCount; i++) {
      const pathIndex = Math.floor(i / 8);
      const path = paths[pathIndex];
      const color = new THREE.Color(path.color);
      
      // Initialize at start position
      const fromPos = AGENT_POSITIONS[path.from] || [0, 0, 0];
      positions[i * 3] = fromPos[0];
      positions[i * 3 + 1] = fromPos[1];
      positions[i * 3 + 2] = fromPos[2];
      
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
      
      pathIndices[i] = pathIndex;
      progress[i] = (i % 8) / 8; // Stagger particles along path
    }
    
    return { positions, colors, pathIndices, progress };
  }, [paths, particleCount]);
  
  // Animate particles along paths
  useFrame((state) => {
    if (!particlesRef.current) return;
    
    const time = state.clock.getElapsedTime();
    const positionAttr = particlesRef.current.geometry.attributes.position as THREE.BufferAttribute;
    
    for (let i = 0; i < particleCount; i++) {
      const pathIndex = pathIndices[i];
      const path = paths[pathIndex];
      const fromPos = AGENT_POSITIONS[path.from] || [0, 0, 0];
      const toPos = AGENT_POSITIONS[path.to] || [0, 0, 0];
      
      // Calculate progress along path (0-1, looping)
      const speed = 0.3 + (pathIndex % 3) * 0.1; // Vary speed per path
      const t = ((time * speed + progress[i]) % 1);
      
      // Interpolate position with slight arc
      const x = fromPos[0] + (toPos[0] - fromPos[0]) * t;
      const y = fromPos[1] + (toPos[1] - fromPos[1]) * t + Math.sin(t * Math.PI) * 0.5;
      const z = fromPos[2] + (toPos[2] - fromPos[2]) * t;
      
      positionAttr.setXYZ(i, x, y, z);
    }
    
    positionAttr.needsUpdate = true;
  });
  
  // Create geometry with buffer attributes
  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    return geo;
  }, [positions, colors]);
  
  return (
    <points ref={particlesRef} geometry={geometry}>
      <pointsMaterial
        size={0.15}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
};

interface NeuralMeshProps {
  onAgentClick?: (agentName: string) => void;
}

export const NeuralMesh: React.FC<NeuralMeshProps> = ({ onAgentClick }) => {
  const { agents } = useDistributedAgents();

  // Map agent data to renderable format
  const agentNodes = useMemo(() => {
    return agents.map(agent => ({
      name: agent.agent_name,
      position: (AGENT_POSITIONS[agent.agent_name] || [0, 0, 0]) as [number, number, number],
      color: AGENT_COLORS[agent.agent_name as keyof typeof AGENT_COLORS] || '#ffffff',
      isActive: agent.status === 'active' || agent.health === 'healthy',
      health: agent.health || 'unknown',
      iconUrl: AGENT_ICONS[agent.agent_name] || ''
    }));
  }, [agents]);

  return (
    <>
      {/* Ambient lighting */}
      <ambientLight intensity={0.3} />
      
      {/* Point lights for dramatic effect */}
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#06b6d4" />
      <pointLight position={[-10, -10, -10]} intensity={0.3} color="#a855f7" />
      
      {/* Particle flow between agents */}
      <ParticleFlow paths={COMM_PATHS} />
      
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
