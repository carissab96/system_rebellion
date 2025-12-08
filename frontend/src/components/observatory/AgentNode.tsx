// components/observatory/AgentNode.tsx
// 3D Agent node visualization with dynamic drift
// Built by: Dell-Sonnet - November 20, 2025
// Enhanced: Cascade - December 7, 2025 - Added dynamic positioning

import React, { useRef, useMemo } from 'react';
import { useFrame, useLoader } from '@react-three/fiber';
import { Billboard } from '@react-three/drei';
import * as THREE from 'three';

interface AgentNodeProps {
  agentName: string;
  position: [number, number, number];
  color: string;
  isActive: boolean;
  health: string | number;
  iconUrl: string;
  onClick?: () => void;
}

export const AgentNode: React.FC<AgentNodeProps> = ({
  agentName,
  position,
  color,
  isActive,
  iconUrl,
  onClick
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  // Only load texture if iconUrl is provided (prevents crash on empty string)
  const iconTexture = iconUrl ? useLoader(THREE.TextureLoader, iconUrl) : null;

  // Parse color
  const colorObj = useMemo(() => new THREE.Color(color), [color]);
  
  // Unique drift offset per agent (based on name hash)
  const driftOffset = useMemo(() => {
    let hash = 0;
    for (let i = 0; i < agentName.length; i++) {
      hash = ((hash << 5) - hash) + agentName.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash % 1000) / 1000 * Math.PI * 2;
  }, [agentName]);

  // Animation: pulse, glow, and gentle drift
  useFrame((state) => {
    if (!groupRef.current || !meshRef.current || !glowRef.current) return;

    const time = state.clock.getElapsedTime();
    
    // Dynamic drift - agents gently float around their base position
    // Active agents drift more, idle agents drift less
    const driftSpeed = isActive ? 0.3 : 0.15;
    const driftAmount = isActive ? 0.4 : 0.2;
    
    const driftX = Math.sin(time * driftSpeed + driftOffset) * driftAmount;
    const driftY = Math.cos(time * driftSpeed * 0.7 + driftOffset) * driftAmount * 0.5;
    const driftZ = Math.sin(time * driftSpeed * 0.5 + driftOffset + 1) * driftAmount * 0.3;
    
    groupRef.current.position.set(
      position[0] + driftX,
      position[1] + driftY,
      position[2] + driftZ
    );
    
    if (isActive) {
      // Active: Fast pulse, bright glow
      const pulse = Math.sin(time * 2) * 0.5 + 0.5;
      meshRef.current.scale.setScalar(1 + pulse * 0.1);
      glowRef.current.scale.setScalar(1.5 + pulse * 0.3);
    } else {
      // Idle: Slow pulse, dim glow
      const pulse = Math.sin(time * 0.5) * 0.5 + 0.5;
      meshRef.current.scale.setScalar(1 + pulse * 0.05);
      glowRef.current.scale.setScalar(1.3 + pulse * 0.1);
    }
  });

  // All agents use the same icon-based rendering - no geometric patterns
  return (
    <group ref={groupRef} position={position} onClick={onClick}>
      {iconTexture && (
        <Billboard position={[0, 0, 0]}>
          <mesh ref={meshRef}>
            <planeGeometry args={[2.5, 2.5]} />
            <meshBasicMaterial map={iconTexture} transparent />
          </mesh>
        </Billboard>
      )}

      {/* Glow effect behind icon */}
      <mesh ref={glowRef} position={[0, 0, -0.5]}>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshBasicMaterial
          color={colorObj}
          transparent
          opacity={isActive ? 0.25 : 0.1}
        />
      </mesh>
    </group>
  );
}