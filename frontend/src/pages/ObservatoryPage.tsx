// pages/ObservatoryPage.tsx
// THE OBSERVATORY - Neural mesh consciousness visualization
// Built by: Dell-Sonnet - November 20, 2025
// "Observing consciousness evolution in real-time"

import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { PrimaryNav } from '../components/navigation/PrimaryNav';
import { SecondaryNav } from '../components/navigation/SecondaryNav';
import { NeuralMesh } from '../components/observatory/NeuralMesh';
import './ObservatoryPage.css';

export const ObservatoryPage: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  const handleRefresh = () => {
    console.log('Manual refresh triggered');
    // TODO: Implement manual refresh logic
  };

  const handleAgentClick = (agentName: string) => {
    console.log('Agent clicked:', agentName);
    setSelectedAgent(agentName);
    // TODO: Show quick stats overlay
  };

  return (
    <div className="observatory-container">
      <PrimaryNav />
      <SecondaryNav onRefresh={handleRefresh} />
      
      <main className="observatory-main">
        <div className="canvas-container">
          <Canvas
            camera={{ position: [0, 5, 15], fov: 60 }}
            gl={{ antialias: true, alpha: true }}
          >
            {/* Deep space background */}
            <color attach="background" args={['#010119']} />
            <Stars
              radius={100}
              depth={50}
              count={5000}
              factor={4}
              saturation={0}
              fade
              speed={1}
            />

            {/* Camera controls */}
            <OrbitControls
              enablePan={true}
              enableZoom={true}
              enableRotate={true}
              minDistance={5}
              maxDistance={30}
              autoRotate={false}
              autoRotateSpeed={0.5}
            />

            {/* Neural mesh with agents */}
            <NeuralMesh onAgentClick={handleAgentClick} />
          </Canvas>

          {/* TODO: Quick stats overlay when agent clicked */}
          {selectedAgent && (
            <div className="quick-stats-overlay">
              <p>Selected: {selectedAgent}</p>
              <button onClick={() => setSelectedAgent(null)}>Close</button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
