// src/components/agents/TheStick.tsx
import React from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { StickCompliance } from '../../types/agents';

export const TheStick: React.FC = () => {
  const { isConnected, messages, error } = useWebSocket('ws://localhost:8086/stick');
  
  const stickMessages = messages.filter(
    (msg): msg is StickCompliance => msg.type === 'stick_compliance'
  );

  return (
    <div className="rebellion-card stick-panel">
      <div className="card-header">
        <h3 className="stick-text">
          📏 The Stick - Compliance & Configuration Master
        </h3>
        <div className="d-flex align-center justify-between mt-2">
          <span className="stick-badge">TRAUMA-AWARE</span>
          <div className="status-indicator">
            <span className={`status-dot ${isConnected ? 'status-online' : 'status-error'}`}></span>
            <span className="text-sm">
              {isConnected ? 'PAPER BAG READY' : 'HYPERVENTILATING'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <p className="text-sm text-dim mb-3">
          Channels PTSD/OCD/ADHD into perfect system compliance. 
          Trauma survivor turned compliance genius with paper bag protocols.
        </p>
        
        <div className="space-y-2" style={{ maxHeight: '200px', overflowY: 'auto' }}>
          {stickMessages.slice(-5).map((msg, index) => (
            <div 
              key={index} 
              className={`alert ${
                msg.anxiety_level === 'HIGH' ? 'alert-error' : 
                msg.anxiety_level === 'MEDIUM' ? 'alert-warning' : 'alert-success'
              }`}
            >
              <div className="d-flex justify-between align-center mb-1">
                <span className="text-sm font-medium">
                  📋 Compliance: {msg.compliance_percentage}%
                </span>
                <span className="stick-badge">
                  😰 Anxiety: {msg.anxiety_level}
                </span>
              </div>
              <p className="text-xs">
                <strong>Status:</strong> {msg.compliance_status}
              </p>
              {msg.paper_bag_protocol_active && (
                <p className="text-xs mt-1 stick-text">
                  📄 *breathing into paper bag with systematic precision*
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};