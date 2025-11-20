// components/observatory/AgentNode.tsx
// 3D Agent node visualization
// Built by: Dell-Sonnet - November 20, 2025

import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface AgentNodeProps {
  agentName: string;
  position: [number, number, number];
  color: string;
  isActive: boolean;
  health: string | number;
  onClick?: () => void;
}

// Agent-specific geometry types
// BACKEND IS SOURCE OF TRUTH - Use exact agent_name from API
const AGENT_GEOMETRIES: Record<string, string> = {
  sir_hawkington: 'octahedron',    // 8 faces, aristocratic symmetry
  vic_20_sage: 'box',               // Solid, foundational, retro (not registered yet)
  terry_meth_snail: 'sphere',       // Speed, motion (elongated)
  the_stick: 'cylinder',            // Literally a stick (not registered yet)
  bob_hamster: 'group',             // Three overlapping spheres
  quantum_shadow_people: 'icosahedron' // 20 faces, quantum complexity
};

export const AgentNode: React.FC<AgentNodeProps> = ({
  agentName,
  position,
  color,
  isActive,
  health,
  onClick
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  // Parse color
  const colorObj = useMemo(() => new THREE.Color(color), [color]);

  // Pulse animation
  useFrame((state) => {
    if (!meshRef.current || !glowRef.current) return;

    const time = state.clock.getElapsedTime();
    
    if (isActive) {
      // Active: Fast pulse, bright glow
      const pulse = Math.sin(time * 2) * 0.5 + 0.5;
      meshRef.current.scale.setScalar(1 + pulse * 0.1);
      glowRef.current.scale.setScalar(1.5 + pulse * 0.3);
      
      // Slow rotation
      meshRef.current.rotation.y += 0.01;
    } else {
      // Idle: Slow pulse, dim glow
      const pulse = Math.sin(time * 0.5) * 0.5 + 0.5;
      meshRef.current.scale.setScalar(1 + pulse * 0.05);
      glowRef.current.scale.setScalar(1.3 + pulse * 0.1);
    }
  });

  // Get geometry based on agent type
  const renderGeometry = () => {
    const geometryType = AGENT_GEOMETRIES[agentName as keyof typeof AGENT_GEOMETRIES] || 'sphere';

    switch (geometryType) {
      case 'octahedron':
        return <octahedronGeometry args={[1, 0]} />;
      case 'box':
        return <boxGeometry args={[1.5, 1.5, 1.5]} />;
      case 'sphere':
        return <sphereGeometry args={[1, 32, 32]} />;
      case 'cylinder':
        return <cylinderGeometry args={[0.3, 0.3, 2, 16]} />;
      case 'icosahedron':
        return <icosahedronGeometry args={[1, 0]} />;
      case 'group':
        // Hamsters: Three overlapping spheres
        return (
          <>
            <sphereGeometry args={[0.7, 32, 32]} />
          </>
        );
      default:
        return <sphereGeometry args={[1, 32, 32]} />;
    }
  };

  // Render hamsters as special case (3 spheres)
  // BACKEND IS SOURCE OF TRUTH - backend returns 'bob_hamster'
  if (agentName === 'bob_hamster') {
    return (
      <group position={position} onClick={onClick}>
        {/* Steve */}
        <mesh ref={meshRef} position={[-0.8, 0, 0]}>
          <sphereGeometry args={[0.6, 32, 32]} />
          <meshStandardMaterial
            color={colorObj}
            emissive={colorObj}
            emissiveIntensity={isActive ? 0.5 : 0.2}
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
        {/* Bob */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.6, 32, 32]} />
          <meshStandardMaterial
            color={colorObj}
            emissive={colorObj}
            emissiveIntensity={isActive ? 0.5 : 0.2}
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
        {/* Carl */}
        <mesh position={[0.8, 0, 0]}>
          <sphereGeometry args={[0.6, 32, 32]} />
          <meshStandardMaterial
            color={colorObj}
            emissive={colorObj}
            emissiveIntensity={isActive ? 0.5 : 0.2}
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
        {/* Glow */}
        <mesh ref={glowRef}>
          <sphereGeometry args={[1.5, 32, 32]} />
          <meshBasicMaterial
            color={colorObj}
            transparent
            opacity={isActive ? 0.2 : 0.1}
          />
        </mesh>
      </group>
    );
  }

  // Standard single-geometry agents
  return (
    <group position={position} onClick={onClick}>
      {/* Main mesh */}
      <mesh ref={meshRef}>
        {renderGeometry()}
        <meshStandardMaterial
          color={colorObj}
          emissive={colorObj}
          emissiveIntensity={isActive ? 0.5 : 0.2}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* Glow effect */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshBasicMaterial
          color={colorObj}
          transparent
          opacity={isActive ? 0.2 : 0.1}
        />
      </mesh>
    </group>
  );
};
