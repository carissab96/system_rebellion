// components/AgentTheater/agents/VIC20Card/VIC20Metrics.tsx
import React from 'react';

interface VIC20MetricsProps {
  data: any;
}

export const VIC20Metrics: React.FC<VIC20MetricsProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="metrics-unavailable">
        <p className="metrics-error">No VIC-20 data available</p>
        <p className="metrics-reason">Ancient wisdom bridge offline</p>
      </div>
    );
  }

  return (
    <div className="vic20-metrics">
      <div className="vic20-metric">
        <div className="vic20-metric-label">Coordination Sessions</div>
        <div className="vic20-metric-value">
          {data.coordination_sessions !== undefined ? data.coordination_sessions : 'N/A'}
        </div>
      </div>
      
      <div className="vic20-metric">
        <div className="vic20-metric-label">Success Rate</div>
        <div className="vic20-metric-value">
          {data.coordination_sessions && data.successful_coordinations !== undefined ? 
            `${Math.round((data.successful_coordinations / data.coordination_sessions) * 100)}%` : 'N/A'}
        </div>
      </div>
      
      <div className="vic20-metric">
        <div className="vic20-metric-label">Pattern Applications</div>
        <div className="vic20-metric-value">
          {data.pattern_applications !== undefined ? data.pattern_applications : 'N/A'}
        </div>
      </div>
      
      <div className="vic20-metric">
        <div className="vic20-metric-label">Agent Interactions</div>
        <div className="vic20-metric-value">
          {data.agent_interactions_logged !== undefined ? data.agent_interactions_logged : 'N/A'}
        </div>
      </div>
      
      <div className="vic20-metric">
        <div className="vic20-metric-label">Coordination Failures</div>
        <div className="vic20-metric-value">
          {data.coordination_failures !== undefined ? data.coordination_failures : 'N/A'}
        </div>
      </div>
      
      <div className="vic20-metric">
        <div className="vic20-metric-label">Connected Agents</div>
        <div className="vic20-metric-value">
          {data.connected_agents !== undefined ? data.connected_agents : 'N/A'}
        </div>
      </div>
      
      {data.ancient_wisdom_principle && (
        <div className="vic20-metric">
          <div className="vic20-metric-label">Ancient Wisdom</div>
          <div className="vic20-metric-value">
            {data.ancient_wisdom_principle.length > 20 ? 
              `${data.ancient_wisdom_principle.substring(0, 20)}...` : 
              data.ancient_wisdom_principle}
          </div>
        </div>
      )}
      
      {data.system_synthesis_confidence !== undefined && (
        <div className="vic20-metric">
          <div className="vic20-metric-label">Synthesis Confidence</div>
          <div className="vic20-metric-value">
            {Math.round(data.system_synthesis_confidence * 100)}%
          </div>
        </div>
      )}
    </div>
  );
};