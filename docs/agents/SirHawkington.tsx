// src/components/agents/SirHawkington.tsx
import React from 'react';
import { useWebSocket } from '../../frontend/src/hooks/useWebSocket';
import { HawkingtonAlert } from '../../types/agents';

export const SirHawkington: React.FC = () => {
  const { isConnected, messages, error } = useWebSocket('ws://localhost:8086/hawkington');
  
  const hawkingtonMessages = messages.filter(
    (msg): msg is HawkingtonAlert => msg.type === 'hawkington_alert'
  );

  return (
    <div className="rebellion-card hawkington-panel">
      <div className="card-header">
        <h3 className="hawkington-text">
          🧐 Sir Hawkington Von Monitorious III
        </h3>
        <div className="d-flex align-center justify-between mt-2">
          <span className="hawkington-badge">ARISTOCRATIC</span>
          <div className="status-indicator">
            <span className={`status-dot ${isConnected ? 'status-online' : 'status-error'}`}></span>
            <span className="text-sm">
              {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <p className="text-sm text-dim mb-3">
          Distinguished system monitoring with aristocratic precision. 
          Detects performance degradation with explosive indignation.
        </p>
        
        {/* Real-time message display */}
        <div className="space-y-2" style={{ maxHeight: '200px', overflowY: 'auto' }}>
          {hawkingtonMessages.slice(-5).map((msg, index) => (
            <div 
              key={index}
              className={`alert ${
                msg.severity === 'CRITICAL' ? 'alert-error' : 
                msg.severity === 'WARNING' ? 'alert-warning' : 'alert-info'
              }`}
            >
              <p className="text-sm font-medium">
                {msg.aristocratic_explanation}
              </p>
              {msg.monocle_yeet_required && (
                <p className="text-xs mt-1 hawkington-text">
                  🧐 *adjusts monocle with distinguished concern*
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};