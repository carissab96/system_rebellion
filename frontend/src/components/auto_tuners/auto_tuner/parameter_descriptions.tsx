import React from 'react';

interface ParameterDescriptionProps {
  parameter: string;
}

/**
 * Component that provides detailed descriptions of auto-tuner parameters
 */
export const ParameterDescription: React.FC<ParameterDescriptionProps> = ({ parameter }) => {
  const descriptions: Record<string, { description: string, impactMeaning: string }> = {
    'process_priority': {
      description: 'Controls the CPU scheduling priority of processes. Lower values (negative numbers) give higher priority to processes, allowing them to get more CPU time. Higher values give lower priority.',
      impactMeaning: 'Impact score indicates how much this change will affect overall system responsiveness. Higher impact means more noticeable performance changes.'
    },
    'cpu_governor': {
      description: 'Controls how the CPU frequency scaling is managed. Options like "performance" maximize speed, while "powersave" prioritizes energy efficiency. "ondemand" and "conservative" balance between the two.',
      impactMeaning: 'Impact score indicates the expected effect on performance vs. battery life. Higher impact means more significant changes to system behavior.'
    },
    'io_scheduler': {
      description: 'Determines how disk I/O requests are handled. Different schedulers optimize for different workloads - "deadline" for low latency, "cfq" for fairness between processes, and "noop" for SSDs.',
      impactMeaning: 'Impact score indicates how much this change will affect disk performance. Higher impact means more noticeable changes to file operations.'
    },
    'memory_pressure': {
      description: 'Controls how aggressively the system reclaims memory. Settings like "normal", "moderate", and "critical" determine when the system starts freeing up memory from caches and buffers.',
      impactMeaning: 'Impact score indicates how much this change will affect memory-intensive applications. Higher impact means more noticeable changes to application performance.'
    },
    'swap_tendency': {
      description: 'Determines how likely the system is to use swap space. Lower values make the system less likely to swap, keeping more in RAM. Higher values increase swap usage, potentially saving RAM but reducing performance.',
      impactMeaning: 'Impact score indicates how much this change will affect system responsiveness. Higher impact means more noticeable changes to performance when memory is constrained.'
    },
    'cache_pressure': {
      description: 'Controls how aggressively the system reclaims memory from the page cache. Higher values make the system more aggressive in reclaiming memory, potentially reducing file system performance.',
      impactMeaning: 'Impact score indicates how much this change will affect file system performance. Higher impact means more noticeable changes to file operations.'
    },
    'disk_read_ahead': {
      description: 'Controls how much data is read ahead when accessing files. Higher values can improve sequential read performance but may waste memory for random access patterns.',
      impactMeaning: 'Impact score indicates how much this change will affect file read performance. Higher impact means more noticeable changes to file operations.'
    },
    'network_buffer': {
      description: 'Controls the size of network buffers. Larger buffers can improve throughput for large transfers but may increase latency for small transfers.',
      impactMeaning: 'Impact score indicates how much this change will affect network performance. Higher impact means more noticeable changes to network operations.'
    }
  };

  // Default description for unknown parameters
  const defaultDescription = {
    description: 'A system tuning parameter that affects system performance.',
    impactMeaning: 'Impact score indicates how much this change will affect system performance. Higher impact means more noticeable changes.'
  };

  const { description, impactMeaning } = descriptions[parameter] || defaultDescription;

  return (
    <div className="parameter-description">
      <h4>What is {parameter}?</h4>
      <p>{description}</p>
      <h4>About Impact Score and Confidence</h4>
      <p>{impactMeaning}</p>
      <p>The <strong>confidence score</strong> (e.g., 75%) indicates how certain the system is that this recommendation will be beneficial. Higher confidence means the system has stronger evidence that this change will help.</p>
    </div>
  );
};

/**
 * Component that explains what the auto-tuner values mean
 */
export const AutoTunerHelp: React.FC = () => {
  return (
    <div className="auto-tuner-help">
      <h3>Understanding Auto-Tuner Values</h3>
      
      <h4>Current vs. Recommended Values</h4>
      <p>The <strong>Current</strong> value shows the existing setting on your system. The <strong>Recommended</strong> value is what System Rebellion suggests for optimal performance based on your usage patterns and system metrics.</p>
      
      <h4>Impact Score</h4>
      <p>Impact scores range from 0.0 to 1.0 and indicate how significant the effect of a change will be:</p>
      <ul>
        <li><strong>0.1-0.3:</strong> Minor impact - subtle improvements</li>
        <li><strong>0.4-0.6:</strong> Moderate impact - noticeable improvements</li>
        <li><strong>0.7-1.0:</strong> Major impact - significant improvements</li>
      </ul>
      
      <h4>Confidence Score</h4>
      <p>Confidence scores (shown as percentages) indicate how certain the system is about its recommendation:</p>
      <ul>
        <li><strong>30-50%:</strong> Low confidence - experimental recommendation</li>
        <li><strong>51-75%:</strong> Moderate confidence - likely beneficial</li>
        <li><strong>76-100%:</strong> High confidence - strongly recommended</li>
      </ul>
      
      <h4>Real-time Data</h4>
      <p>All recommendations are based on real-time analysis of your system's current state and historical usage patterns. The system continuously monitors your performance metrics to provide the most relevant suggestions.</p>
    </div>
  );
};
