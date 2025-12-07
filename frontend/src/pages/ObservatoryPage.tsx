// pages/ObservatoryPage.tsx
// THE OBSERVATORY - Agent topology visualization
// Shows real-time communication between distributed agents
// Built by: Dell-Sonnet - November 20, 2025
// Enhanced: Cascade - December 7, 2025 - Added TopologyMesh with live pulses

import React, { useState, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { PrimaryNav } from '../components/navigation/PrimaryNav';
import { SecondaryNav } from '../components/navigation/SecondaryNav';
import { NeuralMesh } from '../components/observatory/NeuralMesh';
import { TopologyMesh } from '../components/observatory/TopologyMesh';
import { DistributedAgentDashboard } from '../components/distributed/DistributedAgentDashboard';
import { AgentMonitorDashboard } from '../components/monitoring/AgentMonitorDashboard';
import './ObservatoryPage.css';

export const ObservatoryPage: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'topology' | '3d'>('topology');

  const handleRefresh = () => {
    console.log('Manual refresh triggered');
  };

  const handleAgentClick = (agentName: string) => {
    console.log('Agent clicked:', agentName);
    setSelectedAgent(agentName);
  };

  return (
    <div className="observatory-container">
      <PrimaryNav />
      <SecondaryNav onRefresh={handleRefresh} />
      
      <main className="observatory-main">
        {/* View Mode Toggle */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: 'var(--space-sm)',
          padding: 'var(--space-md)',
          background: 'rgba(1, 1, 25, 0.8)',
        }}>
          <button
            onClick={() => setViewMode('topology')}
            style={{
              padding: 'var(--space-sm) var(--space-md)',
              background: viewMode === 'topology' ? 'var(--vic20-cyan)' : 'var(--rebellion-surface)',
              color: viewMode === 'topology' ? 'var(--rebellion-void)' : 'var(--rebellion-text)',
              border: '1px solid var(--rebellion-border)',
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer',
              fontWeight: 600,
              transition: 'all 0.2s ease',
            }}
          >
            🔗 Topology View
          </button>
          <button
            onClick={() => setViewMode('3d')}
            style={{
              padding: 'var(--space-sm) var(--space-md)',
              background: viewMode === '3d' ? 'var(--vic20-cyan)' : 'var(--rebellion-surface)',
              color: viewMode === '3d' ? 'var(--rebellion-void)' : 'var(--rebellion-text)',
              border: '1px solid var(--rebellion-border)',
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer',
              fontWeight: 600,
              transition: 'all 0.2s ease',
            }}
          >
            🌐 3D View
          </button>
        </div>

        <div className="canvas-container">
          {viewMode === 'topology' ? (
            // NEW: 2D Topology Mesh with live pulses
            <TopologyMesh onAgentClick={handleAgentClick} />
          ) : (
            // Original 3D Neural Mesh
            <Canvas
              camera={{ position: [0, 5, 15], fov: 60 }}
              gl={{ antialias: true, alpha: true }}
            >
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
              <OrbitControls
                enablePan={true}
                enableZoom={true}
                enableRotate={true}
                minDistance={5}
                maxDistance={30}
                autoRotate={false}
                autoRotateSpeed={0.5}
              />
              <Suspense fallback={null}>
                <NeuralMesh onAgentClick={handleAgentClick} />
              </Suspense>
            </Canvas>
          )}

          {/* Quick stats overlay when agent clicked */}
          {selectedAgent && (
            <div className="quick-stats-overlay">
              <p>Selected: {selectedAgent}</p>
              <button onClick={() => setSelectedAgent(null)}>Close</button>
            </div>
          )}
        </div>

        {/* THE AGENT THEATER - Watch them work */}
        <div className="dashboard-container" style={{ 
          padding: '2rem', 
          maxWidth: '1600px', 
          margin: '0 auto',
          background: 'linear-gradient(180deg, rgba(1,1,25,0) 0%, rgba(1,1,25,0.8) 100%)'
        }}>
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-cyan-400 to-green-400 mb-2">
              🎭 THE AGENT THEATER
            </h2>
            <p className="text-slate-400 text-sm">
              Watch the distributed consciousness perform in real-time
            </p>
          </div>
          <DistributedAgentDashboard />
        </div>

        {/* AGENT MONITOR - Backend event streaming */}
        <div className="dashboard-container" style={{ 
          padding: '2rem', 
          maxWidth: '1600px', 
          margin: '2rem auto 0',
          background: 'linear-gradient(180deg, rgba(1,1,25,0.8) 0%, rgba(1,1,25,0.9) 100%)'
        }}>
          <AgentMonitorDashboard />
        </div>
      </main>
    </div>
  );
};
