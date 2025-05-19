import React, { useState, useMemo } from 'react';
import { ProcessedMemoryData, MemoryProcess } from '../types';
import { formatBytes } from '../utils/formatters';
import { Table, TableColumn } from '@/design-system/components/Table/Table';
import { Card } from '@/design-system/components/Card';
import { LineChart } from 'recharts';
import { Badge } from '@/design-system/components/Badge';
import { SearchInput } from '@/components/common/SearchInput';
import { Button } from '@/design-system/components/Button';

interface MemoryProcessesTabProps {
  data: ProcessedMemoryData;
}

export const MemoryProcessesTab: React.FC<MemoryProcessesTabProps> = ({ data }) => {
  const { processes } = data;
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<keyof MemoryProcess>('rss');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [selectedProcess, setSelectedProcess] = useState<number | null>(null);
  
  // Filter and sort processes
  const filteredProcesses = useMemo(() => {
    let filtered = processes.topConsumers;
    
    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        p => p.name.toLowerCase().includes(term) || 
             p.command.toLowerCase().includes(term) || 
             p.pid.toString().includes(term)
      );
    }
    
    // Apply sorting
    filtered = [...filtered].sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      // String comparison (fallback)
      const aStr = String(aValue);
      const bStr = String(bValue);
      return sortDirection === 'asc' ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
    });
    
    return filtered;
  }, [processes.topConsumers, searchTerm, sortField, sortDirection]);
  
  // Find growth trend for selected process
  const selectedProcessTrend = useMemo(() => {
    if (!selectedProcess) return null;
    return processes.growthTrends.find(trend => trend.pid === selectedProcess);
  }, [selectedProcess, processes.growthTrends]);
  
  // Find potential leak for selected process
  const selectedProcessLeak = useMemo(() => {
    if (!selectedProcess) return null;
    return processes.potentialLeaks.find(leak => leak.pid === selectedProcess);
  }, [selectedProcess, processes.potentialLeaks]);
  
  // Table columns configuration
  const columns: TableColumn<MemoryProcess>[] = [
    {
      key: 'pid',
      header: 'PID',
      sortable: true,
      width: '10%',
    },
    {
      key: 'name',
      header: 'Process',
      sortable: true,
      width: '20%',
      render: (process) => (
        <div className="process-name">
          <span>{process.name}</span>
          {processes.potentialLeaks.some(leak => leak.pid === process.pid) && (
            <Badge type="danger" tooltip="Potential memory leak detected">LEAK</Badge>
          )}
          {process.growthRate && process.growthRate > 0 && !processes.potentialLeaks.some(leak => leak.pid === process.pid) && (
            <Badge type="warning" tooltip="Memory usage is growing">GROWING</Badge>
          )}
        </div>
      )
    },
    {
      key: 'rss',
      header: 'Memory',
      sortable: true,
      width: '15%',
      render: (process) => formatBytes(process.rss)
    },
    {
      key: 'percentMemory',
      header: '% of Total',
      sortable: true,
      width: '15%',
      render: (process) => `${process.percentMemory.toFixed(1)}%`
    },
    {
      key: 'vms',
      header: 'Virtual',
      sortable: true,
      width: '15%',
      render: (process) => formatBytes(process.vms)
    },
    {
      key: 'shared',
      header: 'Shared',
      sortable: true,
      width: '15%',
      render: (process) => formatBytes(process.shared)
    },
    {
      key: 'growthRate',
      header: 'Growth',
      sortable: true,
      width: '10%',
      render: (process) => (
        process.growthRate !== undefined 
          ? <span className={process.growthRate > 0 ? 'growing' : ''}>{formatBytes(process.growthRate)}/min</span> 
          : 'N/A'
      )
    },
  ];
  
  const handleRowClick = (process: MemoryProcess) => {
    setSelectedProcess(process.pid);
  };
  
  return (
    <div className="memory-processes">
      <div className="memory-processes__controls">
        <SearchInput
          initialValue={searchTerm}
          onSearch={setSearchTerm}
          placeholder="Search processes..."
        />
        
        <div className="memory-processes__info">
          {filteredProcesses.length} of {processes.topConsumers.length} processes shown
        </div>
      </div>
      
      <Table
        columns={columns}
        data={filteredProcesses}
        onSort={(key: string, direction: 'asc' | 'desc') => {
  setSortField(key as keyof MemoryProcess);
  setSortDirection(direction);
}}
        
        onRowClick={handleRowClick}
        
        emptyState="No processes found matching your search criteria."
      />
      
      {/* Process Details Section */}
      {selectedProcess && (
        <div className="memory-process-details">
          <h3>Process Details</h3>
          
          <div className="memory-process-details__grid">
            {/* Memory Trend Chart */}
            <Card className="memory-process-details__trend">
              <h4>Memory Usage Trend</h4>
              {selectedProcessTrend ? (
                <LineChart
                  data={selectedProcessTrend.dataPoints.map(point => ({
                    x: point.timestamp,
                    y: point.bytes / (1024 * 1024) // Convert to MB for readability
                  }))}
                  height={200}
                  
                />
              ) : (
                <div className="memory-process-details__no-data">
                  <p>Insufficient historical data to generate trend.</p>
                </div>
              )}
            </Card>
            
            {/* Memory Leak Analysis */}
            <Card className="memory-process-details__leak-analysis">
              <h4>Memory Leak Analysis</h4>
              {selectedProcessLeak ? (
                <div className="leak-analysis">
                  <div className="leak-probability">
                    <span className="leak-probability__label">Leak Probability:</span>
                    <div className="leak-probability__meter">
                      <div 
                        className="leak-probability__fill" 
                        style={{ 
                          width: `${selectedProcessLeak.leakProbability * 100}%`,
                          backgroundColor: selectedProcessLeak.leakProbability > 0.7 ? 'var(--color-danger)' : 'var(--color-warning)'
                        }} 
                      />
                    </div>
                    <span className="leak-probability__value">
                      {(selectedProcessLeak.leakProbability * 100).toFixed(0)}%
                    </span>
                  </div>
                  
                  <div className="leak-evidence">
                    <h5>Evidence Points:</h5>
                    <ul className="leak-evidence__list">
                      {selectedProcessLeak.evidencePoints.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="leak-advice">
                    <p>
                      <strong>Recommendation:</strong> This process shows signs of a memory leak. 
                      Consider restarting it or reporting the issue to the developer.
                    </p>
                    <Button variant="danger">Restart Process</Button>
                  </div>
                </div>
              ) : (
                <div className="leak-analysis leak-analysis--negative">
                  <p>No memory leak detected for this process.</p>
                  {selectedProcessTrend && selectedProcessTrend.trendline.slope > 0 && (
                    <p className="memory-growth-note">
                      Memory usage is growing at {formatBytes(selectedProcessTrend.trendline.slope * 60)}/min, 
                      but the pattern doesn't match typical leak behavior.
                    </p>
                  )}
                </div>
              )}
            </Card>
            
            {/* Process Command Details */}
            <Card className="memory-process-details__command">
              <h4>Process Information</h4>
              <div className="process-command">
                <div className="process-command__field">
                  <span className="process-command__label">PID:</span>
                  <span className="process-command__value">
                    {processes.topConsumers.find(p => p.pid === selectedProcess)?.pid}
                  </span>
                </div>
                <div className="process-command__field">
                  <span className="process-command__label">Name:</span>
                  <span className="process-command__value">
                    {processes.topConsumers.find(p => p.pid === selectedProcess)?.name}
                  </span>
                </div>
                <div className="process-command__field">
                  <span className="process-command__label">Command:</span>
                  <div className="process-command__value process-command__value--command">
                    {processes.topConsumers.find(p => p.pid === selectedProcess)?.command}
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}
      
      {/* Memory Leak Warnings Section */}
      {processes.potentialLeaks.length > 0 && (
        <Card className="memory-processes__leak-warnings">
          <h3>
            Memory Leak Warnings
            <Badge type="danger">{processes.potentialLeaks.length}</Badge>
          </h3>
          
          <div className="memory-leak-list">
            {processes.potentialLeaks.map(leak => (
              <div key={leak.pid} className="memory-leak-item">
                <div className="memory-leak-item__header">
                  <h4 onClick={() => setSelectedProcess(leak.pid)}>
                    {leak.name} (PID: {leak.pid})
                  </h4>
                  <span className="memory-leak-growth-rate">
                    Growing at {formatBytes(leak.growthRate)}/minute
                  </span>
                </div>
                <div className="memory-leak-item__probability">
                  <span>Leak Probability: {(leak.leakProbability * 100).toFixed(0)}%</span>
                  <div className="memory-leak-probability-bar">
                    <div 
                      className="memory-leak-probability-bar__fill"
                      style={{ 
                        width: `${leak.leakProbability * 100}%`,
                        backgroundColor: leak.leakProbability > 0.7 ? 'var(--color-danger)' : 'var(--color-warning)'
                      }}
                    />
                  </div>
                </div>
                <Button 
                  size="md" 
                  variant="secondary" 
                  onClick={() => setSelectedProcess(leak.pid)}
                >
                  View Details
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};