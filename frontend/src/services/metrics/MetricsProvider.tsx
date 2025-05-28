// frontend/src/services/metrics/MetricsProvider.tsx
import React, { useEffect, useRef } from 'react';
import { useAppDispatch } from '../../store/hooks';
import { updateMetrics, setConnectionStatus, setWebSocketError } from '../../store/slices/metricsSlice';
import { apiClient } from '../../utils/api';


/**
 * MetricsProvider component that handles fetching system metrics and updating the Redux store.
 * This component doesn't render anything visible but manages the data flow for metrics.
 */
const MetricsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const dispatch = useAppDispatch();
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isFirstFetch = useRef(true);

  // Function to fetch metrics from the backend
  const fetchMetrics = async () => {
    try {
      dispatch(setConnectionStatus('connecting'));
      const response = await apiClient.get('/metrics/system');
      
      if (response && response.data) {
        // Log the metrics data structure
        console.log('🔍 Metrics data structure:', {
          cpu: response.data.cpu_usage !== undefined ? 'present' : 'missing',
          memory: response.data.memory_usage !== undefined ? 'present' : 'missing',
          disk: response.data.disk_usage !== undefined ? 'present' : 'missing',
          network: response.data.network_io ? 'present' : 'missing',
          details: response.data.details ? 'present' : 'missing',
          process_count: response.data.process_count !== undefined ? 'present' : 'missing',
          timestamp: response.data.timestamp ? 'present' : 'missing'
        });
        
        // Log the detailed structure if available
        if (response.data.details) {
          console.log('🔍 Details structure:', {
            cpu: response.data.details.cpu ? 'present' : 'missing',
            memory: response.data.details.memory ? 'present' : 'missing',
            disk: response.data.details.disk ? 'present' : 'missing',
            network: response.data.details.network ? 'present' : 'missing'
          });
        }
        
        // Create a safe version of the data with all required fields
        const safeData = {
          cpu_usage: response.data.cpu_usage ?? 0,
          memory_usage: response.data.memory_usage ?? 0,
          disk_usage: response.data.disk_usage ?? 0,
          network_io: response.data.network_io ?? { sent: 0, recv: 0 },
          process_count: response.data.process_count ?? 0,
          timestamp: response.data.timestamp ?? new Date().toISOString(),
          details: response.data.details ?? {
            cpu: { percent: 0, cores: [], temperature: null, frequency: null },
            memory: { percent: 0, total: 0, available: 0, used: 0, free: 0 },
            disk: { percent: 0, total: 0, used: 0, free: 0, available: 0, partitions: [] },
            network: { bytes_sent: 0, bytes_recv: 0, packets_sent: 0, packets_recv: 0, interfaces: [] }
          }
        };
        
        // Transform the data to match what the components expect, but optimize for size
        const transformedData = {
          // Essential metrics only - avoid duplicating large data structures
          cpu_usage: safeData.cpu_usage,
          memory_percent: safeData.memory_usage,
          disk_percent: safeData.disk_usage,
          
          // Memory metrics
          memory_total: safeData.details.memory?.total ?? 0,
          memory_available: safeData.details.memory?.available ?? 0,
          memory_used: safeData.details.memory?.used ?? 0,
          memory_free: safeData.details.memory?.free ?? 0,
          memory_swap_percent: safeData.details.memory?.swap_percent ?? 0,
          memory_swap_free: safeData.details.memory?.swap_free ?? 0,
          
          // Disk metrics
          disk_total: safeData.details.disk?.total ?? 0,
          disk_used: safeData.details.disk?.used ?? 0,
          disk_free: safeData.details.disk?.free ?? 0,
          
          // Network metrics
          network_sent: safeData.network_io?.sent ?? 0,
          network_recv: safeData.network_io?.recv ?? 0,
          
          // Timestamp
          timestamp: safeData.timestamp,
          
          // Additional data - only include what's needed
          additional: {
            // Disk
            disk_partitions: safeData.details.disk?.partitions ?? [],
            disk_read_rate: safeData.details.disk?.read_rate ?? 0,
            disk_write_rate: safeData.details.disk?.write_rate ?? 0,
            
            // Memory
            top_memory_processes: safeData.details.memory?.top_processes ?? [],
            
            // CPU
            top_cpu_processes: safeData.details.cpu?.top_processes ?? [],
            cpu_cores: safeData.details.cpu?.cores ?? [],
            cpu_temperature: safeData.details.cpu?.temperature ?? 0,
            cpu_frequency: safeData.details.cpu?.frequency ?? 0,
            
            // Network
            connection_quality: safeData.details.network?.connection_quality ?? {
              average_latency: 0,
              packet_loss_percent: 0,
              connection_stability: 0,
              gateway_latency: 0,
              dns_latency: 0,
              internet_latency: 0,
              jitter: 0
            },
            network_interfaces: safeData.details.network?.interfaces ?? [],
            protocol_breakdown: safeData.details.network?.protocol_breakdown ?? {
              tcp: 0,
              udp: 0,
              http: 0,
              https: 0,
              dns: 0
            },
            top_bandwidth_processes: safeData.details.network?.top_bandwidth_processes ?? []
          }
        };
        
        // Update the metrics in the Redux store with the transformed data
        dispatch(updateMetrics(transformedData));
        dispatch(setConnectionStatus('connected'));
        
        // Log only on first successful fetch
        if (isFirstFetch.current) {
          console.log('🎯 Initial metrics fetched successfully:', transformedData);
          isFirstFetch.current = false;
        }
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
      dispatch(setWebSocketError('Failed to fetch metrics data'));
      dispatch(setConnectionStatus('error'));
    }
  };

  useEffect(() => {
    // Fetch metrics immediately on mount
    fetchMetrics();

    // Set up polling interval (every 5 seconds)
    pollingIntervalRef.current = setInterval(fetchMetrics, 5000);

    // Clean up on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // Just render children - this is a logic-only component
  return <>{children}</>;
};

export default MetricsProvider;
