import React, { useState } from 'react';
import './InfoTooltip.css';

export interface InfoTooltipProps {
  content: React.ReactNode;
  position?: 'top' | 'right' | 'bottom' | 'left';
  children?: React.ReactNode;
  className?: string;
}

export const InfoTooltip: React.FC<InfoTooltipProps> = ({
  content,
  position = 'top',
  children,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className={`info-tooltip-container ${className}`}>
      <span 
        className="info-tooltip-trigger"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
      >
        {children || (
          <span className="info-tooltip-icon" aria-label="More information">
            i
          </span>
        )}
      </span>
      {isVisible && (
        <div className={`info-tooltip ${position}`}>
          <div className="info-tooltip-content">
            {content}
          </div>
          <div className={`info-tooltip-arrow ${position}`} />
        </div>
      )}
    </div>
  );
};

export default InfoTooltip;
