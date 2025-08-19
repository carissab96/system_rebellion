import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Tooltip } from '@mui/material';
import { useAppSelector } from '../../../hooks/redux';
import { selectShellData } from '../../../store/slices/methSnailSlice';

const ShellSpinIndicator: React.FC = () => {
  // Get shell spin data using memoized selector - will throw if data is missing
  const { spinCount, spinProbability } = useAppSelector(selectShellData);

  // Track previous spin count for animation triggers
  const prevSpinCountRef = useRef(spinCount);

  // Track spin state and timing
  const [spinState, setSpinState] = useState({
    isSpinning: false,
    lastSpinTime: '',
    spinInProgress: false
  });

  // Animation state
  const [isAnimating, setIsAnimating] = useState(false);

  // Validate probability value
  if (spinProbability < 0 || spinProbability > 1) {
    throw new Error(`Invalid spin probability: ${spinProbability}. Must be between 0 and 1.`);
  }

  // Format probability as percentage with validation
  const formatProbability = (probability: number) => {
    if (probability < 0 || probability > 1) {
      throw new Error(`Invalid probability value: ${probability}. Must be between 0 and 1.`);
    }
    const percentage = Math.round(probability * 100);
    if (isNaN(percentage)) {
      throw new Error(`Failed to calculate percentage from probability: ${probability}`);
    }
    return `${percentage}%`;
  };
  
  // Format the probability for display
  const probabilityDisplay = formatProbability(spinProbability);

  // Handle spin detection and animation
  useEffect(() => {
    // Check for new spins and trigger animation
    if (spinCount > prevSpinCountRef.current) {
      // New spin detected, trigger animation
      const spinTime = new Date().toISOString();
      if (isNaN(new Date(spinTime).getTime())) {
        throw new Error('Invalid spin timestamp');
      }

      // Update spin state with all required properties
      setSpinState({
        isSpinning: true,
        lastSpinTime: spinTime,
        spinInProgress: true
      });

      // Reset spinning state after animation duration
      const timer = setTimeout(() => {
        setSpinState(prev => ({
          ...prev,
          isSpinning: false,
          spinInProgress: false
        }));
      }, 2000); // Match this with your CSS animation duration

      // Set a timeout to stop the animation
      const animationTimer = setTimeout(() => {
        setIsAnimating(false);
      }, 1000);

      // Update the ref for next comparison
      prevSpinCountRef.current = spinCount;

      return () => {
        clearTimeout(timer);
        clearTimeout(animationTimer);
      };
    }
  }, [spinCount]);

  // Get color based on spin probability
  const getProbabilityColor = (probability: number) => {
    if (probability < 0) throw new Error('Probability cannot be negative');
    if (probability > 1) throw new Error('Probability cannot be greater than 1');

    if (probability < 0.3) return 'var(--success)';
    if (probability < 0.7) return 'var(--warning)';
    return 'var(--error)';
  };

  // Get status text based on spin probability
  const getStatusText = (probability: number) => {
    if (probability < 0.2) return 'Low';
    if (probability < 0.6) return 'Medium';
    if (probability < 0.9) return 'High';
    if (probability < 60) return 'Medium';
    if (probability < 90) return 'High';
    return 'Critical';
  };
  
  // Get status color based on spin state and probability
  const getStatusColor = () => {
    if (spinState.isSpinning) return 'var(--warning)';
    if (spinState.spinInProgress) return 'var(--success)';
    return getProbabilityColor(spinProbability);
  };
  
  // Format the last spin time for display
  const formatLastSpinTime = (isoString: string) => {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    return date.toLocaleTimeString();
  };

  return (
    <Box sx={{
      backgroundColor: 'var(--rebellion-surface)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-md)',
      border: '1px solid var(--rebellion-border)',
      marginBottom: 'var(--space-md)'
    }}>
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--space-md)'
      }}>
        <Typography variant="subtitle2" sx={{ 
          color: 'var(--rebellion-text-dim)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          fontSize: '0.75rem'
        }}>
          Shell Spins
        </Typography>
        
        <Tooltip title={spinState.spinInProgress ? 'Spin in progress...' : 'Ready for next spin'}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center',
            backgroundColor: 'var(--rebellion-void)',
            borderRadius: '9999px',
            padding: 'var(--space-xxs) var(--space-sm)',
            border: `1px solid ${getStatusColor()}`,
            transition: 'all 0.3s ease-in-out'
          }}>
            <Box sx={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: spinState.spinInProgress ? 'var(--success)' : 'var(--rebellion-text-dim)',
              marginRight: 'var(--space-xs)',
              boxShadow: spinState.spinInProgress ? '0 0 8px var(--success)' : 'none',
              transition: 'all 0.3s ease-in-out'
            }} />
            <Typography variant="caption" sx={{ 
              color: 'var(--rebellion-text-bright)',
              fontSize: '0.7rem',
              fontWeight: 600
            }}>
              {spinState.spinInProgress ? 'Active' : 'Idle'}
            </Typography>
          </Box>
        </Tooltip>
      </Box>
      
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 'var(--space-md)'
      }}>
        <Tooltip title={isAnimating ? "Spinning!" : "Ready"}>
          <Box sx={{
            fontSize: '3.5rem',
            lineHeight: 1,
            transform: isAnimating ? 'rotate(360deg)' : 'rotate(0deg)',
            transition: isAnimating ? 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)' : 'none',
            display: 'inline-block',
            position: 'relative',
            '&::after': {
              content: '""',
              position: 'absolute',
              bottom: '-4px',
              left: '50%',
              transform: 'translateX(-50%)',
              width: '60%',
              height: '4px',
              backgroundColor: 'var(--rebellion-border)',
              borderRadius: '2px',
              opacity: 0.5
            }
          }}>
            🐚
            {spinCount > 0 && (
              <Box sx={{
                position: 'absolute',
                top: '-4px',
                right: '-4px',
                backgroundColor: 'var(--warning)',
                color: 'var(--rebellion-void)',
                borderRadius: '50%',
                width: '20px',
                height: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.7rem',
                fontWeight: 'bold',
                border: '2px solid var(--rebellion-surface)'
              }}>
                {spinCount}
              </Box>
            )}
          </Box>
        </Tooltip>
      </Box>
      
      <Box sx={{ marginBottom: 'var(--space-sm)' }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          marginBottom: 'var(--space-xxs)'
        }}>
          <Typography variant="caption" sx={{ 
            color: 'var(--rebellion-text-dim)',
            fontSize: '0.7rem'
          }}>
            Next Spin Probability
          </Typography>
          <Typography variant="body2" sx={{ 
            color: getStatusColor(),
            fontWeight: 500,
            marginLeft: 'var(--space-xs)'
          }}>
            {getStatusText(spinProbability)} ({probabilityDisplay})
          </Typography>
        </Box>
        <Box sx={{
          height: '6px',
          backgroundColor: 'var(--rebellion-border)',
          borderRadius: '3px',
          overflow: 'hidden'
        }}>
          <Box sx={{
            width: `${spinProbability}%`,
            height: '100%',
            backgroundColor: getProbabilityColor(spinProbability),
            transition: 'width 0.3s ease, background-color 0.3s ease',
            borderRadius: '3px'
          }} />
        </Box>
      </Box>
      
      <Typography variant="caption" sx={{
        display: 'block',
        textAlign: 'right',
        color: 'var(--rebellion-text-dim)',
        fontSize: '0.65rem',
        marginTop: 'var(--space-xs)'
      }}>
        {spinState.lastSpinTime 
          ? `Last spin: ${formatLastSpinTime(spinState.lastSpinTime)}` 
          : 'No spins recorded'}
      </Typography>
    </Box>
  );
};

export default ShellSpinIndicator;