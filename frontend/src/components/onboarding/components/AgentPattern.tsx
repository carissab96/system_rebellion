// components/onboarding/components/AgentPattern.tsx
import React from 'react';

interface AgentPatternProps {
  agentId: string;
  className?: string;
}

export const AgentPattern: React.FC<AgentPatternProps> = ({ agentId, className = '' }) => {
  switch (agentId) {
    case 'hawkington':
      return (
        <div className={`agent-pattern hawkington-pattern ${className}`}>
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
        </div>
      );
    
    case 'stick':
      return (
        <div className={`agent-pattern stick-pattern ${className}`}>
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
        </div>
      );
    
    case 'hamsters':
      return (
        <div className={`agent-pattern hamsters-pattern ${className}`}>
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
        </div>
      );
    
    case 'snail':
      return (
        <div className={`agent-pattern snail-pattern ${className}`}>
          <svg viewBox="0 0 80 80">
            <path
              className="snail-spiral"
              d="M40,40 Q50,30 40,20 T20,20 Q10,30 10,40 T20,60 Q30,70 40,70 T60,60 Q70,50 70,40 T60,20"
            />
          </svg>
        </div>
      );
    
    case 'qsp':
      return (
        <div className={`agent-pattern qsp-pattern ${className}`}>
          <div className="pattern-element" />
          <div className="pattern-element" />
        </div>
      );
    
    case 'vic20':
      return (
        <div className={`agent-pattern vic20-pattern ${className}`}>
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
          <div className="pattern-element" />
        </div>
      );
    
    default:
      return null;
  }
};