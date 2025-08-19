import React from 'react';
import { Box, Typography, CircularProgress, Tooltip } from '@mui/material';
import { useAppSelector } from '../../../hooks/redux';
import { selectCaffeineData } from '../../../store/slices/methSnailSlice';

const CaffeineGauge: React.FC = () => {
  // Get caffeine data using memoized selector
  const {
    caffeineMg,
    isHyper,
    isDecaf,
    energySource,
    timestamp
  } = useAppSelector(selectCaffeineData);
  
  // Convert mg to a 0-100 scale (assuming 400mg is max for 100%)
  const MAX_CAFFEINE_MG = 400;
  const caffeineLevel = (caffeineMg / MAX_CAFFEINE_MG) * 100;

  // Get color based on caffeine level and status
  const getCaffeineColor = (level: number) => {
    if (isDecaf) return 'var(--rebellion-text-dim)';
    if (isHyper) return 'var(--error)';
    if (level < 30) return 'var(--success)';
    if (level < 70) return 'var(--warning)';
    return 'var(--error)';
  };

  // Get status text and color
  const getStatus = () => {
    if (isDecaf) return { text: 'Decaf', color: 'var(--rebellion-text-dim)' };
    if (isHyper) return { text: 'Hyper!', color: 'var(--error)' };
    if (caffeineLevel < 30) return { text: 'Low', color: 'var(--success)' };
    if (caffeineLevel < 70) return { text: 'Optimal', color: 'var(--warning)' };
    return { text: 'High', color: 'var(--error)' };
  };
  
  // Format the timestamp for display
  const formatTimestamp = (isoString: string) => {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) throw new Error('Invalid timestamp');
    return date.toLocaleTimeString();
  };
  
  // Get energy source emoji
  const getEnergySourceEmoji = () => {
    const source = energySource.toLowerCase();
    if (source === 'adrenaline') return '⚡';
    if (source === 'panic') return '😱';
    if (source === 'determination') return '💪';
    if (source === 'sheer_will') return '🧠';
    if (source === 'caffeine') return '☕';
    throw new Error(`Unknown energy source: ${energySource}`);
  };

  const status = getStatus();
  const size = 120;
  const thickness = 12;

  return (
    <Box sx={{
      backgroundColor: 'var(--rebellion-surface)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-md)',
      border: '1px solid var(--rebellion-border)',
      marginBottom: 'var(--space-md)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      <Typography variant="subtitle2" sx={{ 
        color: 'var(--rebellion-text-dim)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        fontSize: '0.75rem',
        marginBottom: 'var(--space-sm)'
      }}>
        Caffeine Level
      </Typography>
      
      <Box sx={{ 
        position: 'relative',
        width: size,
        height: size,
        margin: '0 auto var(--space-sm)'
      }}>
        <CircularProgress
          variant="determinate"
          value={100}
          size={size}
          thickness={thickness}
          sx={{
            position: 'absolute',
            color: 'var(--rebellion-border)',
            top: 0,
            left: 0,
          }}
        />
        <CircularProgress
          variant="determinate"
          value={caffeineLevel}
          size={size}
          thickness={thickness}
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            color: getCaffeineColor(caffeineLevel),
            zIndex: 1,
            '& .MuiCircularProgress-circle': {
              strokeLinecap: 'round',
              transition: 'stroke-dashoffset 0.5s ease 0s',
            },
          }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: 'absolute',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Tooltip title={`${caffeineMg}mg ${isDecaf ? '(decaf)' : ''} | Source: ${energySource} ${getEnergySourceEmoji()}`}>
            <Typography variant="h4" sx={{ 
              fontWeight: 700,
              color: getCaffeineColor(caffeineLevel),
              lineHeight: 1,
              textShadow: isHyper ? '0 0 8px var(--error)' : 'none',
              transition: 'all 0.3s ease-in-out'
            }}>
              {Math.round(caffeineLevel)}%
            </Typography>
          </Tooltip>
          <Typography variant="caption" sx={{ 
            color: status.color,
            fontWeight: 600,
            fontSize: '0.7rem',
            marginTop: 'var(--space-xxs)'
          }}>
            {status.text}
          </Typography>
        </Box>
      </Box>
      
      <Box sx={{
        display: 'flex',
        justifyContent: 'space-between',
        width: '100%',
        fontSize: '0.7rem',
        color: 'var(--rebellion-text-dim)',
        marginTop: 'var(--space-xs)'
      }}>
        <span>0%</span>
        <span>100%</span>
      </Box>
      
      <Typography variant="caption" sx={{
        display: 'block',
        textAlign: 'center',
        color: 'var(--rebellion-text-dim)',
        fontSize: '0.65rem',
        marginTop: 'var(--space-xs)'
      }}>
        Updated: {formatTimestamp(timestamp)}
      </Typography>
    </Box>
  );
};

export default CaffeineGauge;