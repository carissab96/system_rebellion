import React from 'react';

interface ErrorDisplayProps {
  message: string;
  details?: string;
  retry?: () => void;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ message, details, retry }) => {
  return (
    <div className="error-display">
      <div className="error-icon">⚠️</div>
      <h3>Error</h3>
      <p>{message}</p>
      {details && <p className="error-details">{details}</p>}
      {retry && (
        <button onClick={retry} className="retry-button">
          Retry
        </button>
      )}
    </div>
  );
};

export default ErrorDisplay;
