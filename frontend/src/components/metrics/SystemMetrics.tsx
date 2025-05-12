// frontend/src/components/metrics/SystemMetrics.tsx

import React from 'react';
import NetworkMetric from './NetworkMetrics/NetworkMetric';
// Import other metrics components...

const SystemMetrics: React.FC = () => {
  return (
    <div className="system-metrics">
      {/* Other metrics */}
      <NetworkMetric 
        compact={false}
        showTabs={true}
      />
    </div>
  );
};

export default SystemMetrics;