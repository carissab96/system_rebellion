// SirHawkingtonDashboardWidget.tsx
import React from 'react';
import { useAppSelector } from '../../../store/hooks';
import { Link } from 'react-router-dom';

interface SirHawkingtonWidgetProps {}

export const SirHawkingtonDashboardWidget: React.FC<SirHawkingtonWidgetProps> = () => {
  // Get Sir Hawkington's data from the websocket
  const hawkingtonData = useAppSelector(state => state.metrics.current?.sir_hawkington);
  
  const agentProcessing = useAppSelector(state => state.metrics.current?.agent_processing);
  const getMonocleStatus = () => {
    if (!hawkingtonData) return 'adjusting';
    if (hawkingtonData.error) return 'fogged';
    return hawkingtonData.decision_type === 'alert' ? 'popped' : 'polished';
  };

  const getDecisionColor = () => {
    if (!hawkingtonData) return 'normal';
    if (hawkingtonData.error) return 'critical';
    return hawkingtonData.decision_type === 'alert' ? 'critical' : 
           hawkingtonData.decision_type === 'concern' ? 'warning' : 'normal';
  };

  return (
    <div className="sr-card sr-card--cyber">
      <div className="sr-card__header">
        <h2>🧐 Sir Hawkington's Analysis</h2>
        <Link to="/metrics" className="sr-card__action">
          Full Analysis
        </Link>
      </div>
      
      <div className="sr-agent-status">
        <div className="sr-agent-status__header">
          <div className="sr-agent-status__avatar">
            🧐
          </div>
          <div className="sr-agent-status__info">
            <h3>Sir Hawkington</h3>
            <p>System Analyst</p>
          </div>
          <div className={`sr-agent-status__badge sr-agent-status__badge--${getMonocleStatus()}`}>
            {getMonocleStatus() === 'polished' ? '✨ Polished' :
             getMonocleStatus() === 'fogged' ? '😵 Fogged' :
             getMonocleStatus() === 'popped' ? '💥 Popped' : '🔧 Adjusting'}
          </div>
        </div>
        
        {hawkingtonData && (
          <div className="sr-agent-analysis">
            <div className={`sr-agent-analysis__decision sr-agent-analysis__decision--${getDecisionColor()}`}>
              {hawkingtonData.decision_type?.toUpperCase() || 'ANALYZING'}
            </div>
            <p className="sr-agent-analysis__message">
              {hawkingtonData.message || 'Adjusting monocle for optimal analysis...'}
            </p>
            <div className="sr-agent-analysis__confidence">
              <span>Confidence: {((hawkingtonData.confidence || 0) * 100).toFixed(1)}%</span>
              <div className="sr-progress-bar">
                <div 
                  className="sr-progress-bar__fill" 
                  style={{ width: `${(hawkingtonData.confidence || 0) * 100}%` }}
                />
              </div>
            </div>
            <div className="sr-agent-analysis__meta">
              <small>
                {agentProcessing?.successful_agents?.some((agent: { agent_name: string; }) => agent.agent_name === 'sir_hawkington') ? 
                  `✅ Analyzed in ${(agentProcessing?.successful_agents?.find((agent: { agent_name: string; }) => agent.agent_name === 'sir_hawkington')?.processing_time_seconds || 0) * 1000}ms` : 
                  '❌ Analysis failed'
                }
                {hawkingtonData.agent_version && ` • v${hawkingtonData.agent_version}`}
              </small>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};