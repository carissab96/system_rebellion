// components/AgentTheater/NeuralActivityViz.tsx
import React from 'react';
import './NeuralActivityViz.css';

interface NeuralActivityVizProps {
  neuralActivity: {
    processing: number;
    patternRecognition: number;
    decisionMaking: number;
  };
  accentColor: string;
}

export const NeuralActivityViz: React.FC<NeuralActivityVizProps> = ({ 
  neuralActivity, 
  accentColor 
}) => {
  return (
    <div className="neural-activity">
      <div className="neural-header">Neural Activity:</div>
      <div className="neural-metrics">
        <div className="neural-metric">
          <div className="metric-label">Processing:</div>
          <div className="metric-bar">
            <div 
              className="metric-fill processing"
              style={{ 
                width: `${neuralActivity.processing}%`,
                backgroundColor: accentColor 
              }}
            />
          </div>
          <div className="metric-value">{neuralActivity.processing}%</div>
        </div>
        
        <div className="neural-metric">
          <div className="metric-label">Pattern Recognition:</div>
          <div className="metric-bar">
            <div 
              className="metric-fill pattern-recognition"
              style={{ 
                width: `${neuralActivity.patternRecognition}%`,
                backgroundColor: accentColor 
              }}
            />
          </div>
          <div className="metric-value">{neuralActivity.patternRecognition}%</div>
        </div>
        
        <div className="neural-metric">
          <div className="metric-label">Decision Making:</div>
          <div className="metric-bar">
            <div 
              className="metric-fill decision-making"
              style={{ 
                width: `${neuralActivity.decisionMaking}%`,
                backgroundColor: accentColor 
              }}
            />
          </div>
          <div className="metric-value">{neuralActivity.decisionMaking}%</div>
        </div>
      </div>
    </div>
  );
};