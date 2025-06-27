// DashboardMetricWrapper.tsx - Now with 100% less CSS chaos!

import React from 'react';
import { Link } from 'react-router-dom';

interface DashboardMetricProps {
  title: string;
  value: number | string;
  unit?: string;
  linkTo: string;
  linkState?: any;
  status?: 'normal' | 'warning' | 'critical';
  showProgressBar?: boolean;
}

export const DashboardMetricWrapper: React.FC<DashboardMetricProps> = ({
  title,
  value,
  unit = '',
  linkTo,
  linkState,
  status = 'normal',
  showProgressBar = true
}) => {
  const numericValue = typeof value === 'string' ? parseFloat(value) : value;
  
  // Handle edge cases like a boss
  const safeValue = isNaN(numericValue) ? 0 : numericValue;
  const displayValue = safeValue.toFixed(1);
  const progressWidth = Math.min(Math.max(safeValue, 0), 100);
  
  return (
    <div className="sr-card sr-card--metric">
      <div className="sr-card__header">
        <h3 className="sr-card__title">{title}</h3>
        <Link to={linkTo} state={linkState} className="sr-card__action">
          Details
        </Link>
      </div>
      
      <div className="sr-metric">
        <div className="sr-metric__value">
          {displayValue}{unit}
        </div>
        
        <div className="sr-metric__label">
          {title}
        </div>
        
        {showProgressBar && (
          <div className="sr-metric__progress">
            <div 
              className="sr-metric__progress-fill" 
              style={{ width: `${progressWidth}%` }}
            />
          </div>
        )}
        
        <div className="sr-metric__status">
          <span className={`sr-metric__status-dot sr-metric__status-dot--${status}`}></span>
          <span>
            {status === 'normal' ? '✅ Healthy' : 
             status === 'warning' ? '⚠️ High' : 
             '🚨 Critical'}
          </span>
        </div>
      </div>
    </div>
  );
};