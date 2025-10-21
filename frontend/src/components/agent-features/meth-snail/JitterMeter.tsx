import React from 'react';
import { Box, Typography, LinearProgress, Tooltip } from '@mui/material';
import { useAppSelector } from '../../../hooks/redux';
import { selectJitterData } from '../../../store/slices/methSnailSlice';

const JitterMeter: React.FC = () => {
  // Get jitter data using memoized selector
  const {
    currentJitter,
    peakJitter,
    baselineJitter,
    jitterTrend,
    timestamp
  } = useAppSelector(selectJitterData);
  
  // Calculate normalized jitter level (0-100)
  const jitterLevel = currentJitter * 100;
  const peakJitterLevel = peakJitter * 100;
  const baselineJitterLevel = baselineJitter * 100;

  // Get color based on jitter level
  const getJitterColor = (level: number) => {
    if (level < 30) return 'var(--success)';
    if (level < 70) return 'var(--warning)';
    return 'var(--error)';
  };

  // Get trend icon and color
  const getTrend = () => {
    const trend = jitterTrend.toLowerCase();
    if (trend.includes('increas')) return { icon: '↑', color: 'var(--error)' };
    if (trend.includes('decreas')) return { icon: '↓', color: 'var(--success)' };
    if (trend.includes('high') || trend.includes('elevated')) return { icon: '⚠️', color: 'var(--error)' };
    return { icon: '→', color: 'var(--warning)' };
  };
  
  // Format the timestamp for display
  const formatTimestamp = (isoString: string) => {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) throw new Error('Invalid timestamp');
    return date.toLocaleTimeString();
  };

  const trend = getTrend();

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
        marginBottom: 'var(--space-sm)'
      }}>
        <Typography variant="subtitle2" sx={{ 
          color: 'var(--rebellion-text-dim)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          fontSize: '0.75rem'
        }}>
          Jitter Level
        </Typography>
        <Tooltip title={`Peak: ${peakJitterLevel.toFixed(1)}% | Baseline: ${baselineJitterLevel.toFixed(1)}%`}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6" sx={{ mr: 1, fontWeight: 700, color: 'var(--rebellion-text-bright)' }}>
              {jitterLevel.toFixed(1)}%
            </Typography>
            <Box sx={{ 
              color: trend.color,
              fontWeight: 700,
              fontSize: '1.2rem',
              lineHeight: 1,
              transform: 'translateY(-1px)'
            }}>
              {trend.icon}
            </Box>
          </Box>
        </Tooltip>
      </Box>
      
      <LinearProgress 
        variant="determinate"
        value={jitterLevel}
        sx={{
          height: 6,
          borderRadius: 3,
          backgroundColor: 'var(--rebellion-border)',
          '& .MuiLinearProgress-bar': {
            backgroundColor: getJitterColor(jitterLevel),
            transition: 'all 0.3s ease-in-out',
          },
          marginBottom: 'var(--space-xs)'
        }}
      />
      
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        fontSize: '0.7rem',
        color: 'var(--rebellion-text-dim)'
      }}>
        <span>0%</span>
        <span>50%</span>
        <span>100%</span>
      </Box>
      
      <Typography variant="caption" sx={{
        display: 'block',
        textAlign: 'right',
        color: 'var(--rebellion-text-dim)',
        fontSize: '0.65rem',
        marginTop: 'var(--space-xs)'
      }}>
        Updated: {formatTimestamp(timestamp)}
      </Typography>
    </Box>
  );
};

export default JitterMeter;