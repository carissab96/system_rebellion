// src/components/agents/MethSnail.tsx
import React from 'react';
import { useWebSocket } from '../../frontend/src/hooks/useWebSocket';
import { SnailOptimization } from '../../types/agents';

export const MethSnail: React.FC = () => {
  const { isConnected, messages, error } = useWebSocket('ws://localhost:8086/snail');
  
  const snailMessages = messages.filter(
    (msg): msg is SnailOptimization => msg.type === 'snail_optimization'
  );

  return (
    <div className="rebellion-card snail-panel">
      <div className="card-header">
        <h3 className="snail-text">
          🐌💨 Meth Snail - Optimization Engine
        </h3>
        <div className="d-flex align-center justify-between mt-2">
          <span className="snail-badge snail-pulse">CAFFEINATED</span>
          <div className="status-indicator">
            <span className={`status-dot ${isConnected ? 'status-online' : 'status-error'}`}></span>
            <span className="text-sm">
              {isConnected ? 'SHELL SPINNING' : 'CAFFEINE CRASH'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <p className="text-sm text-dim mb-3">
          Energy drink-powered optimization engine. Makes systems go BRRRR 
          through caffeinated algorithmic excellence.
        </p>
        
        <div className="space-y-2" style={{ maxHeight: '200px', overflowY: 'auto' }}>
          {snailMessages.slice(-5).map((msg, index) => (
            <div key={index} className="alert alert-success">
              <div className="d-flex justify-between align-center mb-1">
                <span className="text-sm font-medium">
                  Shell Spinning: {msg.shell_spinning_intensity}
                </span>
                <span className="snail-badge">
                  ☕ {msg.energy_drinks_consumed}
                </span>
              </div>
              <p className="text-xs text-dim">
                {msg.optimization_applied ? 
                  "🚀 OPTIMIZATION APPLIED - SYSTEM GOING BRRRR" : 
                  "🐌 Calculating optimal shell spin velocity..."
                }
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};