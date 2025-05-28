// frontend/src/components/dashboard/Metrics/NetworkMetric/NetworkMetric.tsx

import React from 'react';
import NetworkMetric from '../../../metrics/Network/NetworkMetric';

const DashboardNetworkMetric: React.FC = () => {
  return (
    <NetworkMetric 
      compact={true} 
      dashboardMode={true}
      defaultTab="overview"
    />
  );
};

export default DashboardNetworkMetric;