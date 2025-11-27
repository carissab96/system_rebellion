// components/observatory/NeuralMesh.tsx
// 3D Neural mesh with agent nodes
// Built by: Dell-Sonnet - November 20, 2025
// Enhanced: Cascade - November 27, 2025 - Added connections and message flow

import React, { useMemo } from 'react';
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

  // Map agent data to renderable format
  const agentNodes = useMemo(() => {
    return agents.map(agent => ({
      name: agent.agent_name,
      position: (AGENT_POSITIONS[agent.agent_name] || [0, 0, 0]) as [number, number, number],
      color: AGENT_COLORS[agent.agent_name as keyof typeof AGENT_COLORS] || '#ffffff',
      isActive: agent.is_active,
      health: agent.health,
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
