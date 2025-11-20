// components/observatory/NeuralMesh.tsx
// 3D Neural mesh with agent nodes
// Built by: Dell-Sonnet - November 20, 2025

import React, { useMemo } from 'react';
import { AgentNode } from './AgentNode';
import { useDistributedAgents } from '../../hooks/useDistributedAgents';

// Agent colors from design system
const AGENT_COLORS = {
  sir_hawkington: '#e6ac00',      // Hawkington gold
  vic_20_sage: '#06b6d4',         // VIC-20 cyan
  meth_snail: '#00d084',          // Snail electric
  the_stick: '#f97316',           // Stick coral
  hamsters: '#ff8c42',            // Hamster amber
  quantum_shadow_people: '#a855f7' // QSP violet
};

// Agent positions (VIC-20 at center, others orbit)
const AGENT_POSITIONS: Record<string, [number, number, number]> = {
  vic_20_sage: [0, 0, 0],                    // Center - orchestrator
  sir_hawkington: [-4, 2, 0],                // Upper left
  meth_snail: [4, 2, 0],                     // Upper right
  the_stick: [0, -3, 2],                     // Lower center front
  hamsters: [-3, -2, -2],                    // Lower left back
  quantum_shadow_people: [3, -2, -2]         // Lower right back
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
      isActive: agent.is_active,
      health: agent.health
    }));
  }, [agents]);

  return (
    <>
      {/* Ambient lighting */}
      <ambientLight intensity={0.3} />
      
      {/* Point lights for dramatic effect */}
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#06b6d4" />
      <pointLight position={[-10, -10, -10]} intensity={0.3} color="#a855f7" />
      
      {/* Agent nodes */}
      {agentNodes.map(agent => (
        <AgentNode
          key={agent.name}
          agentName={agent.name}
          position={agent.position}
          color={agent.color}
          isActive={agent.isActive}
          health={agent.health}
          onClick={() => onAgentClick?.(agent.name)}
        />
      ))}

      {/* TODO: Add connections between agents */}
      {/* TODO: Add message flow effects */}
    </>
  );
};
