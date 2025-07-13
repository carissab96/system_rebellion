import React from 'react';
import ReactDOM from 'react-dom';

interface TooltipProps {
  visible: boolean;
  x: number; // X coordinate in viewport (pixels)
  y: number; // Y coordinate in viewport (pixels)
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

const Tooltip: React.FC<TooltipProps> = ({ visible, x, y, children, className = '', style }) => {
  if (!visible) return null;
  // Offset so tooltip doesn't cover cursor
  const offset = 12;
  // Default styles, can be extended by style prop
  const tooltipStyle: React.CSSProperties = {
    position: 'fixed',
    top: y + offset,
    left: x + offset,
    zIndex: 9999,
    pointerEvents: 'none', // So it doesn't block mouse events
    opacity: visible ? 1 : 0,
    transition: 'opacity 0.13s ease',
    ...style,
  };

  return ReactDOM.createPortal(
    <div className={`system-metrics-tooltip ${className}`} style={tooltipStyle}>
      {children}
    </div>,
    document.body
  );
};

export default Tooltip;
