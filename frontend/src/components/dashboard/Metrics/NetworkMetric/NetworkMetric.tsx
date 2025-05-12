// frontend/src/components/dashboard/Metrics/NetworkMetric/NetworkMetric.tsx

import React from 'react';
import NetworkMetric from '../../../metrics/NetworkMetrics/NetworkMetric';

const DashboardNetworkMetric: React.FC = () => {
  return (
    <NetworkMetric 
      compact={true} 
      showTabs={false} 
      initialTab="overview"
    />
  );
};

export default DashboardNetworkMetric;