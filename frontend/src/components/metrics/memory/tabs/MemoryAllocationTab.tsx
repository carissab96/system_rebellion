import React, { useState } from 'react';
import { ProcessedMemoryData } from '../types';
import { formatBytes } from '../utils/formatters';
import { Card } from '@/design-system/components/Card';
import { PieChart } from '@/design-system/components/PieChart/PieChart';
import { ProgressBar } from '@/design-system/components/ProgressBar/ProgressBar';
import { InfoTooltip } from '@/design-system/components/InfoTooltip/InfoTooltip';
import { Badge } from '@/design-system/components/Badge';
import { Button } from '@/design-system/components/Button';

interface MemoryAllocationTabProps {
  data: ProcessedMemoryData;
}

export const MemoryAllocationTab: React.FC<MemoryAllocationTabProps> = ({ data }) => {
  const { allocation } = data;
  const [expandedRecommendation, setExpandedRecommendation] = useState<string | null>(null);
  
  // Generate colors for pie chart
  const getTypeColor = (type: string): string => {
    const colorMap: Record<string, string> = {
      'system': 'var(--color-primary)',
      'user': 'var(--color-success)',
      'service': 'var(--color-info)',
      'kernel': 'var(--color-warning)',
      'cache': 'var(--color-accent)',
      'other': 'var(--color-secondary)'
    };
    
    return colorMap[type.toLowerCase()] || 'var(--color-gray)';
  };
  
  // Prepare data for pie chart
  const pieChartData = allocation.byType.map(item => ({
    label: item.type,
    value: item.bytes,
    percentage: item.percentage,
    color: getTypeColor(item.type)
  }));
  
  // Get severity class for fragmentation
  const getFragmentationSeverityClass = () => {
    switch (allocation.fragmentation.rating) {
      case 'poor': return 'severity-critical';
      case 'moderate': return 'severity-warning';
      case 'good': return 'severity-good';
      default: return '';
    }
  };
  
  // Get impact badge color
  const getImpactColor = (impact: 'high' | 'medium' | 'low') => {
    switch (impact) {
      case 'high': return 'danger';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'secondary';
    }
  };
  
  const toggleRecommendation = (id: string) => {
    if (expandedRecommendation === id) {
      setExpandedRecommendation(null);
    } else {
      setExpandedRecommendation(id);
    }
  };
  
  return (
    <div className="memory-allocation">
      <div className="memory-allocation__grid">
        {/* Memory Allocation By Type */}
        <Card className="memory-allocation__by-type">
          <h3>Memory Allocation by Type</h3>
          
          <div className="memory-allocation-chart">
            <PieChart
              data={pieChartData}
              height={280}
              showLegend={true}
              showPercentages={true}
              donut={true}
              centerText={formatBytes(pieChartData.reduce((sum, item) => sum + item.value, 0))}
            />
          </div>
          
          <div className="memory-allocation-type-list">
            {allocation.byType.map(type => (
              <div key={type.type} className="memory-allocation-type-item">
                <div className="memory-allocation-type-item__header">
                  <div className="memory-allocation-type-color" style={{ backgroundColor: getTypeColor(type.type) }} />
                  <span className="memory-allocation-type-name">{type.type}</span>
                  <span className="memory-allocation-type-percentage">{type.percentage.toFixed(1)}%</span>
                </div>
                <span className="memory-allocation-type-bytes">{formatBytes(type.bytes)}</span>
              </div>
            ))}
          </div>
        </Card>
        
        {/* Memory Fragmentation */}
        <Card className={`memory-allocation__fragmentation ${getFragmentationSeverityClass()}`}>
          <h3>
            Memory Fragmentation
            <InfoTooltip content="Memory fragmentation occurs when memory becomes divided into small, non-contiguous blocks, making it difficult to allocate larger chunks." />
          </h3>
          
          <div className="fragmentation-index">
            <span className="fragmentation-index__label">Fragmentation Index:</span>
            <ProgressBar 
              value={allocation.fragmentation.index} 
              severity={allocation.fragmentation.rating === 'poor' ? 'critical' : 
                      (allocation.fragmentation.rating === 'moderate' ? 'warning' : 'normal')}
              label={`${allocation.fragmentation.index}%`}
            />
          </div>
          
          <div className="fragmentation-details">
            <div className="fragmentation-detail">
              <span className="fragmentation-detail__label">
                Largest Free Block:
                <InfoTooltip content="The size of the largest contiguous free memory block available." />
              </span>
              <span className="fragmentation-detail__value">
                {formatBytes(allocation.fragmentation.largestBlock)}
              </span>
            </div>
            
            <div className="fragmentation-detail">
              <span className="fragmentation-detail__label">
                Free Chunks:
                <InfoTooltip content="Number of separate free memory chunks. Higher values indicate more fragmentation." />
              </span>
              <span className="fragmentation-detail__value">
                {allocation.fragmentation.freeChunks}
              </span>
            </div>
          </div>
          
          <div className="fragmentation-assessment">
            {allocation.fragmentation.rating === 'poor' && (
              <p className="fragmentation-assessment--poor">
                <strong>High Fragmentation:</strong> Memory is highly fragmented, which may prevent allocation of large memory blocks
                and decrease system performance.
              </p>
            )}
            
            {allocation.fragmentation.rating === 'moderate' && (
              <p className="fragmentation-assessment--moderate">
                <strong>Moderate Fragmentation:</strong> Some memory fragmentation is present. While not critical,
                it may affect performance of memory-intensive applications.
              </p>
            )}
            
            {allocation.fragmentation.rating === 'good' && (
              <p className="fragmentation-assessment--good">
                <strong>Low Fragmentation:</strong> Memory is well-organized with minimal fragmentation.
              </p>
            )}
          </div>
        </Card>
        
        {/* Optimization Recommendations */}
        <Card className="memory-allocation__recommendations">
          <h3>Memory Optimization Recommendations</h3>
          
          {allocation.optimizationRecommendations.length === 0 ? (
            <div className="memory-recommendations-empty">
              <p>No optimization recommendations at this time. Your memory utilization appears optimal.</p>
            </div>
          ) : (
            <div className="memory-recommendations-list">
              {allocation.optimizationRecommendations.map(rec => (
                <div key={rec.id} className="memory-recommendation">
                  <div className="memory-recommendation__header" onClick={() => toggleRecommendation(rec.id)}>
                    <div className="memory-recommendation__title">
                      <h4>{rec.title}</h4>
                      <Badge type={getImpactColor(rec.impact)}>
                        {rec.impact.toUpperCase()} IMPACT
                      </Badge>
                    </div>
                    <span className="memory-recommendation__toggle">
                      {expandedRecommendation === rec.id ? '−' : '+'}
                    </span>
                  </div>
                  
                  {expandedRecommendation === rec.id && (
                    <div className="memory-recommendation__body">
                      <p>{rec.description}</p>
                      
                      {rec.actionable && (
                        <div className="memory-recommendation__action">
                          <Button variant="primary">
                            {rec.action || 'Apply Recommendation'}
                          </Button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};