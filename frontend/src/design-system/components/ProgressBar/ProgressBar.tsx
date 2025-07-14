import React from 'react';
import './ProgressBar.css';

export interface ProgressBarProps {
  value: number;
  max?: number;
  color?: string;
  label?: string;
  showPercentage?: boolean;
  height?: number;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  color = 'var(--color-primary)',
  label,
  showPercentage = true,
  height = 8,
  className = ''
}) => {
  const percentage = Math.min(Math.max(0, (value / max) * 100), 100);
  
  return (
    <div className={`progress-bar-container ${className}`}>
      {(label || showPercentage) && (
        <div className="progress-bar-labels">
          {label && <span className="progress-bar-label">{label}</span>}
          {showPercentage && (
            <span className="progress-bar-percentage">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      <div 
        className="progress-bar-background" 
        style={{ height: `${height}px` }}
      >
        <div 
          className="progress-bar-fill"
          style={{
            width: `${percentage}%`,
            backgroundColor: color,
            height: `${height}px`
          }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
