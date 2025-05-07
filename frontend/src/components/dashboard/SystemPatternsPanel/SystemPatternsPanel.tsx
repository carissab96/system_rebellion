import React from 'react';
import { useAppSelector, useAppDispatch } from '../../../store/hooks';
import { fetchPatterns } from '../../../store/slices/autoTunerSlice';
import { MethSnail } from '../../common/CharacterIcons';
import { Button } from '../../../design-system/components';
import './SystemPatternsPanel.css';

interface SystemPatternsPanelProps {
  maxPatterns?: number;
}

export const SystemPatternsPanel: React.FC<SystemPatternsPanelProps> = ({
  maxPatterns
}) => {
  const dispatch = useAppDispatch();
  const patterns = useAppSelector((state) => state.autoTuner.patterns);
  const patternsStatus = useAppSelector((state) => state.autoTuner.status);
  const error = useAppSelector((state) => state.autoTuner.error);
  
  // Fetch patterns on component mount
  React.useEffect(() => {
    console.log('SystemPatternsPanel: Fetching patterns...');
    dispatch(fetchPatterns());
    
    // Set up polling for patterns
    const intervalId = setInterval(() => {
      console.log('SystemPatternsPanel: Polling for patterns...');
      dispatch(fetchPatterns());
    }, 60000); // Poll every minute
    
    return () => clearInterval(intervalId);
  }, [dispatch]);
  
  // Log patterns for debugging
  React.useEffect(() => {
    console.log('SystemPatternsPanel: Current patterns:', patterns);
    console.log('SystemPatternsPanel: Patterns status:', patternsStatus);
    console.log('SystemPatternsPanel: Error:', error);
  }, [patterns, patternsStatus, error]);
  
  // Function to reload patterns
  const handleReloadPatterns = () => {
    console.log('SystemPatternsPanel: Manually reloading patterns...');
    dispatch(fetchPatterns());
  };

  // Filter patterns if maxPatterns is provided
  const displayPatterns = maxPatterns ? patterns.slice(0, maxPatterns) : patterns;

  return (
    <div className="system-patterns">
      <div className="patterns-card-header">
        <h2>Detected System Patterns</h2>
        <div className="meth-snail-icon">
          <MethSnail className="snail-icon" />
          <div className="character-tooltip">
            <p>"The Meth Snail is analyzing your system patterns... slowly but thoroughly!"</p>
          </div>
        </div>
      </div>
      
      {patternsStatus === 'loading' ? (
        <div className="patterns-loading">
          <p>Loading patterns... The Meth Snail is thinking...</p>
          <div className="loading-animation"></div>
        </div>
      ) : !patterns || patterns.length === 0 ? (
        <div className="patterns-empty">
          <p>No patterns detected yet</p>
          <Button 
            variant="cyber" 
            size="sm" 
            onClick={handleReloadPatterns}
            glow
          >
            Poke the Snail
          </Button>
        </div>
      ) : (
        <div className="patterns-list">
          {displayPatterns.map((pattern, index) => (
            <div key={index} className="pattern-card">
              <div className="pattern-header">
                <h3>{pattern.type}</h3>
                <div className="pattern-confidence">
                  Confidence: {(pattern.confidence * 100).toFixed(0)}%
                </div>
              </div>
              <div className="pattern-details">
                <div className="pattern-description">{pattern.pattern}</div>
                <div className="pattern-info">
                  {Object.entries(pattern.details).map(([key, value]) => (
                    <div key={key} className="pattern-detail-item">
                      <span className="detail-key">{key}:</span> {JSON.stringify(value)}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
          
          {patterns.length > displayPatterns.length && (
            <div className="more-patterns">
              <p>{patterns.length - displayPatterns.length} more patterns available</p>
              <Button 
                variant="secondary" 
                size="sm" 
                onClick={handleReloadPatterns}
              >
                View All Patterns
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SystemPatternsPanel;
