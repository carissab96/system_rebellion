// src/components/agents/TheHamsters.tsx
import React from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { HamsterSolution } from '../../types/agents';

export const TheHamsters: React.FC = () => {
  const { isConnected, messages, error } = useWebSocket('ws://localhost:8086/hamsters');
  
  const hamsterMessages = messages.filter(
    (msg): msg is HamsterSolution => msg.type === 'hamster_solution'
  );

  return (
    <div className="rebellion-card hamster-panel">
      <div className="card-header">
        <h3 className="hamster-text">
          🐹🍺 The Hamsters - Beer-Powered Engineers
        </h3>
        <div className="d-flex align-center justify-between mt-2">
          <span className="hamster-badge">BEER-POWERED</span>
          <div className="status-indicator">
            <span className={`status-dot ${isConnected ? 'status-online' : 'status-error'}`}></span>
            <span className="text-sm">
              {isConnected ? 'DUCT TAPE READY' : 'BEER REFILL NEEDED'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <p className="text-sm text-dim mb-3">
          "Hold my beer while I show you this shit" - Engineering solutions 
          with slurred wisdom and premium duct tape.
        </p>
        
        <div className="space-y-2" style={{ maxHeight: '200px', overflowY: 'auto' }}>
          {hamsterMessages.slice(-5).map((msg, index) => (
            <div key={index} className="alert alert-warning">
              <div className="d-flex justify-between align-center mb-1">
                <span className="text-sm font-medium">
                  🍺 Beer Level: {msg.beer_consumption_level}
                </span>
                <span className="hamster-badge">
                  🥃 {msg.slurred_wisdom_factor}/10
                </span>
              </div>
              <p className="text-xs">
                <strong>Solution:</strong> {msg.engineering_solution}
              </p>
              {msg.duct_tape_required && (
                <p className="text-xs mt-1 hamster-text">
                  🛠️ *reaches for premium duct tape with engineering precision*
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};