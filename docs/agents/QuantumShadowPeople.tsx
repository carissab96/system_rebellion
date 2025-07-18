// src/components/agents/QuantumShadowPeople.tsx
import React from 'react';
import { useWebSocket } from '../../frontend/src/hooks/useWebSocket';
import { QSPFix } from '../../types/agents';

export const QuantumShadowPeople: React.FC = () => {
  const { isConnected, messages, error } = useWebSocket('ws://localhost:8086/qsp');
  
  const qspMessages = messages.filter(
    (msg): msg is QSPFix => msg.type === 'qsp_fix'
  );

  return (
    <div className="rebellion-card qsp-panel">
      <div className="card-header">
        <h3 className="qsp-text">
          👻 Quantum Shadow People - Network Fixers
        </h3>
        <div className="d-flex align-center justify-between mt-2">
          <span className="qsp-badge qsp-phase">PHASING</span>
          <div className="status-indicator">
            <span className={`status-dot ${isConnected ? 'status-online' : 'status-error'}`}></span>
            <span className="text-sm">
              {isConnected ? 'DIMENSION ACTIVE' : 'REALITY BREACH'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <p className="text-sm text-dim mb-3">
          Mysterious entities that phase through dimensions to fix networks 
          inexplicably. Router quantum entanglement specialists.
        </p>
        
        <div className="space-y-2" style={{ maxHeight: '200px', overflowY: 'auto' }}>
          {qspMessages.slice(-5).map((msg, index) => (
            <div key={index} className="alert alert-info">
              <div className="d-flex justify-between align-center mb-1">
                <span className="text-sm font-medium">
                  📡 Network Fix Applied
                </span>
                <span className="qsp-badge">
                  🌀 Quantum Level: {msg.quantum_entanglement_level}
                </span>
              </div>
              <p className="text-xs">
                <strong>Method:</strong> {msg.mysterious_fix_method}
              </p>
              <p className="text-xs mt-1 qsp-text">
                👻 *phases router through tequila jello dimension*
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};