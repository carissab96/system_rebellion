// components/agent-theater/MetricsChart.tsx
import React from 'react';

interface MetricsChartProps {
  metrics: { [key: string]: number | string };
  color: string;
}

export const MetricsChart: React.FC<MetricsChartProps> = ({ metrics, color }) => {
  // Extract numeric values for visualization
  const numericMetrics = Object.entries(metrics)
    .filter(([_, value]) => typeof value === 'number')
    .slice(0, 4); // Show max 4 metrics

  if (numericMetrics.length === 0) return null;

  // Normalize values to 0-100 scale for visualization
  const maxValue = Math.max(...numericMetrics.map(([_, v]) => v as number), 1);
  
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: `repeat(${numericMetrics.length}, 1fr)`,
      gap: 'var(--space-sm)',
      padding: 'var(--space-md)',
      background: 'var(--rebellion-void)',
      borderRadius: 'var(--radius-md)',
      border: `1px solid ${color}20`
    }}>
      {numericMetrics.map(([label, value]) => {
        const numValue = value as number;
        const percentage = (numValue / maxValue) * 100;
        
        return (
          <div key={label} style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 'var(--space-xs)'
          }}>
            {/* Bar chart */}
            <div style={{
              width: '100%',
              height: '80px',
              background: 'var(--rebellion-surface)',
              borderRadius: 'var(--radius-sm)',
              position: 'relative',
              overflow: 'hidden',
              border: `1px solid var(--rebellion-border)`
            }}>
              <div style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: `${percentage}%`,
                background: `linear-gradient(180deg, ${color}, ${color}80)`,
                transition: 'height 0.5s ease',
                boxShadow: `0 0 10px ${color}40`
              }} />
              {/* Value label */}
              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                color: 'var(--rebellion-text-bright)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.875rem',
                fontWeight: '700',
                textShadow: '0 0 4px rgba(0,0,0,0.8)'
              }}>
                {numValue.toFixed(0)}
              </div>
            </div>
            
            {/* Label */}
            <span style={{
              fontSize: '0.625rem',
              color: 'var(--rebellion-text-dim)',
              fontFamily: 'var(--font-mono)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              textAlign: 'center',
              lineHeight: 1.2
            }}>
              {label.replace(/_/g, ' ')}
            </span>
          </div>
        );
      })}
    </div>
  );
};
