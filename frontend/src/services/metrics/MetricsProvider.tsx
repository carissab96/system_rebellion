// frontend/src/services/metrics/MetricsProvider.tsx
import React, { useEffect, useRef, useState } from 'react';
import { useAppDispatch } from '../../store/hooks';
import { updateMetrics, setConnectionStatus, setWebSocketError } from '../../store/slices/metricsSlice';
import { apiClient, checkBackendAvailability } from '../../utils/api';
import axios from 'axios';


/**
 * MetricsProvider component that handles fetching system metrics and updating the Redux store.
 * This component doesn't render anything visible but manages the data flow for metrics.
 */
const MetricsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const dispatch = useAppDispatch();
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isFirstFetch = useRef(true);

  // Track consecutive failures for circuit breaker-like behavior
  const [failureCount, setFailureCount] = useState(0);
  const [usingFallback, setUsingFallback] = useState(false);
  const maxFailures = 3; // Max failures before switching to fallback
  const resetTimeout = 30000; // 30 seconds before trying primary endpoint again
  const lastFailureTimeRef = useRef<number>(0);

  // Function to fetch metrics from the backend with fallback mechanisms
  const fetchMetrics = async () => {
    try {
      dispatch(setConnectionStatus('connecting'));
      
      // Check if we should try the primary endpoint again after failure
      const now = Date.now();
      const shouldResetFailureCount = usingFallback && (now - lastFailureTimeRef.current > resetTimeout);
      
      if (shouldResetFailureCount) {
        console.log('🔄 Resetting failure count and trying primary endpoint again');
        setFailureCount(0);
        setUsingFallback(false);
      }
      
      // Try to get metrics from the appropriate endpoint
      let response;
      
      if (!usingFallback) {
        try {
          // Try the primary endpoint through the proxy
          response = await apiClient.get('/metrics/system');
        } catch (primaryError) {
          console.warn('Primary endpoint failed:', primaryError);
          // Increment failure count
          const newFailureCount = failureCount + 1;
          setFailureCount(newFailureCount);
          
          // If we've reached max failures, switch to fallback
          if (newFailureCount >= maxFailures) {
            console.log(`⚠️ Reached ${maxFailures} consecutive failures, switching to fallback endpoint`);
            setUsingFallback(true);
            lastFailureTimeRef.current = now;
          }
          
          // Try the fallback endpoint directly
          response = await axios.get('http://localhost:8000/api/metrics/system', {
            withCredentials: true
          });
        }
      } else {
        // Using fallback endpoint directly
        response = await axios.get('http://localhost:8000/api/metrics/system', {
          withCredentials: true
        });
      }
      
      // If we got here, the request succeeded
      if (failureCount > 0) {
        setFailureCount(0); // Reset failure count on success
      }
      
      // Process the response if it exists and has data
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
        // Create a safe data object with all required fields for SystemMetric interface
        const safeData = {
          // Required fields with fallbacks
          id: response.data.id ?? `metric-${Date.now()}`,
          user_id: response.data.user_id ?? 'system-user',
          cpu_usage: response.data.cpu_usage ?? 0,
          memory_usage: response.data.memory_usage ?? 0,
          memory_percent: response.data.memory_percent ?? response.data.memory_usage ?? 0,
          disk_usage: response.data.disk_usage ?? 0,
          disk_percent: response.data.disk_percent ?? response.data.disk_usage ?? 0,
          memory_allocation: response.data.memory_allocation ?? 0,
          memory_total: response.data.memory_total ?? response.data.details?.memory?.total ?? 0,
          memory_available: response.data.memory_available ?? response.data.details?.memory?.available ?? 0,
          memory_used: response.data.memory_used ?? response.data.details?.memory?.used ?? 0,
          memory_free: response.data.memory_free ?? response.data.details?.memory?.free ?? 0,
          memory_buffer: response.data.memory_buffer ?? 0,
          memory_cache: response.data.memory_cache ?? 0,
          memory_swap: response.data.memory_swap ?? 0,
          memory_swap_total: response.data.memory_swap_total ?? 0,
          memory_swap_free: response.data.memory_swap_free ?? 0,
          memory_swap_used: response.data.memory_swap_used ?? 0,
          memory_swap_percent: response.data.memory_swap_percent ?? 0,
          disk_total: response.data.disk_total ?? response.data.details?.disk?.total ?? 0,
          disk_available: response.data.disk_available ?? response.data.details?.disk?.available ?? 0,
          disk_free: response.data.disk_free ?? response.data.details?.disk?.free ?? 0,
          disk_used: response.data.disk_used ?? response.data.details?.disk?.used ?? 0,
          network_total: response.data.network_total ?? 0,
          network_available: response.data.network_available ?? 0,
          network_free: response.data.network_free ?? 0,
          network_used: response.data.network_used ?? 0,
          network_percent: response.data.network_percent ?? 0,
          process_count: response.data.process_count ?? 0,
          timestamp: response.data.timestamp ?? new Date().toISOString(),
          
          // Network IO for backward compatibility
          network_io: response.data.network_io ?? { sent: 0, recv: 0 },
          
          // Detailed metrics
          details: response.data.details ?? {
            cpu: { 
              percent: 0, 
              cores: [], 
              temperature: 0, 
              frequency: 0,
              model_name: 'Unknown CPU',
              core_count: 1,
              thread_count: 1,
              physical_cores: 1,
              logical_cores: 1,
              top_processes: []
            },
            memory: { percent: 0, total: 0, available: 0, used: 0, free: 0, top_processes: [] },
            disk: { percent: 0, total: 0, used: 0, free: 0, available: 0, partitions: [] },
            network: { bytes_sent: 0, bytes_recv: 0, packets_sent: 0, packets_recv: 0, interfaces: [] }
          }
        };
        
        // Transform the data to match what the components expect, but optimize for size
        // Use type assertion to tell TypeScript this object conforms to SystemMetric
        const transformedData = {
          // Required fields from SystemMetric interface
          id: safeData.id || `metric-${Date.now()}`,
          user_id: safeData.user_id || 'system-user',
          cpu_usage: safeData.cpu_usage,
          memory_usage: safeData.memory_usage || safeData.memory_percent || 0,
          memory_allocation: safeData.memory_allocation || 0,
          memory_percent: safeData.memory_percent,
          disk_percent: safeData.disk_percent,
          memory_total: safeData.memory_total,
          memory_available: safeData.memory_available,
          memory_used: safeData.memory_used,
          memory_free: safeData.memory_free,
          memory_buffer: safeData.memory_buffer || 0,
          memory_cache: safeData.memory_cache || 0,
          memory_swap: safeData.memory_swap || 0,
          memory_swap_total: safeData.memory_swap_total || 0,
          memory_swap_percent: safeData.memory_swap_percent,
          memory_swap_free: safeData.memory_swap_free,
          memory_swap_used: safeData.memory_swap_used || 0,
          disk_usage: safeData.disk_usage || safeData.disk_percent || 0,
          disk_total: safeData.disk_total,
          disk_available: safeData.disk_available,
          disk_free: safeData.disk_free,
          disk_used: safeData.disk_used,
          network_total: safeData.network_total || 0,
          network_available: safeData.network_available || 0,
          network_free: safeData.network_free || 0,
          network_used: safeData.network_used || 0,
          network_percent: safeData.network_percent || 0,
          process_count: safeData.process_count || 0,
          timestamp: safeData.timestamp,
          
          // CPU data required by the interface
          cpu: {
            name: safeData.details?.cpu?.model_name || 'Unknown CPU',
            frequency: {
              current: safeData.details?.cpu?.frequency || 0,
              min: safeData.details?.cpu?.min_frequency || 0,
              max: safeData.details?.cpu?.max_frequency || 4000
            },
            temp: {
              current: safeData.details?.cpu?.temperature || 0,
              min: 0,
              max: 100,
              critical: 90,
              throttle_threshold: 85,
              unit: 'C'
            },
            processes: safeData.details?.cpu?.top_processes || [],
            core_count: safeData.details?.cpu?.core_count || 1,
            usage_percent: safeData.cpu_usage,
            overall_usage: safeData.cpu_usage,
            process_count: safeData.process_count || 0,
            thread_count: safeData.details?.cpu?.thread_count || 1,
            physical_cores: safeData.details?.cpu?.physical_cores || 1,
            logical_cores: safeData.details?.cpu?.logical_cores || 1,
            model_name: safeData.details?.cpu?.model_name || 'Unknown CPU',
            frequency_mhz: safeData.details?.cpu?.frequency || 0,
            temperature: {
              current: safeData.details?.cpu?.temperature || 0,
              min: 0,
              max: 100,
              critical: 90,
              throttle_threshold: 85,
              unit: 'C'
            },
            top_processes: safeData.details?.cpu?.top_processes || [],
            cores: safeData.details?.cpu?.cores || []
          },
          
          // Additional data - only include what's needed
          additional: {
            // Disk
            disk_partitions: safeData.details?.disk?.partitions ?? [],
            disk_read_rate: safeData.details?.disk?.read_rate ?? 0,
            disk_write_rate: safeData.details?.disk?.write_rate ?? 0,
            
            // Memory
            top_memory_processes: safeData.details?.memory?.top_processes ?? [],
            
            // CPU
            top_cpu_processes: safeData.details?.cpu?.top_processes ?? [],
            cpu_cores: safeData.details?.cpu?.cores ?? [],
            cpu_temperature: safeData.details?.cpu?.temperature ?? 0,
            cpu_frequency: safeData.details?.cpu?.frequency ?? 0,
            
            // Network
            connection_quality: safeData.details?.network?.connection_quality ?? {
              average_latency: 0,
              packet_loss_percent: 0,
              connection_stability: 0,
              gateway_latency: 0,
              dns_latency: 0,
              internet_latency: 0,
              jitter: 0
            },
            network_interfaces: safeData.details?.network?.interfaces ?? [],
            protocol_breakdown: safeData.details?.network?.protocol_breakdown ?? {
              tcp: 0,
              udp: 0,
              http: 0,
              https: 0,
              dns: 0
            },
            top_bandwidth_processes: safeData.details?.network?.top_bandwidth_processes ?? []
          }
        };
        
        // Update the metrics in the Redux store with the transformed data
        // Use type assertion to ensure TypeScript recognizes this as a SystemMetric
        dispatch(updateMetrics(transformedData as unknown as import('../../types/metrics').SystemMetric));
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
      
      // Create a fallback metrics object with default values
      const fallbackMetrics = {
        // Required fields from SystemMetric interface
        id: `fallback-${Date.now()}`,
        user_id: 'system-user',
        cpu_usage: 0,
        memory_usage: 0,
        memory_allocation: 0,
        memory_percent: 0,
        disk_percent: 0,
        memory_total: 8 * 1024 * 1024 * 1024, // 8GB as fallback
        memory_available: 4 * 1024 * 1024 * 1024,
        memory_used: 4 * 1024 * 1024 * 1024,
        memory_free: 4 * 1024 * 1024 * 1024,
        memory_buffer: 0,
        memory_cache: 0,
        memory_swap: 0,
        memory_swap_total: 4 * 1024 * 1024 * 1024,
        memory_swap_percent: 0,
        memory_swap_free: 2 * 1024 * 1024 * 1024,
        memory_swap_used: 2 * 1024 * 1024 * 1024,
        disk_usage: 0,
        disk_total: 100 * 1024 * 1024 * 1024, // 100GB as fallback
        disk_available: 50 * 1024 * 1024 * 1024,
        disk_free: 50 * 1024 * 1024 * 1024,
        disk_used: 50 * 1024 * 1024 * 1024,
        network_total: 1000 * 1024 * 1024, // 1000 MB as fallback
        network_available: 800 * 1024 * 1024,
        network_free: 800 * 1024 * 1024,
        network_used: 200 * 1024 * 1024,
        network_percent: 0,
        process_count: 0,
        timestamp: new Date().toISOString(),
        
        // CPU data required by the interface
        cpu: {
          name: 'Fallback CPU Model',
          frequency: {
            current: 0,
            min: 0,
            max: 4000
          },
          temp: {
            current: 0,
            min: 0,
            max: 100,
            critical: 90,
            throttle_threshold: 85,
            unit: 'C'
          },
          processes: [],
          core_count: 1,
          usage_percent: 0,
          overall_usage: 0,
          process_count: 0,
          thread_count: 1,
          physical_cores: 1,
          logical_cores: 1,
          model_name: 'Fallback CPU Model',
          frequency_mhz: 0,
          temperature: {
            current: 0,
            min: 0,
            max: 100,
            critical: 90,
            throttle_threshold: 85,
            unit: 'C'
          },
          top_processes: [],
          cores: []
        },
        
        additional: {
          disk_partitions: [],
          disk_read_rate: 0,
          disk_write_rate: 0,
          top_memory_processes: [],
          top_cpu_processes: [],
          cpu_cores: [],
          cpu_temperature: 0,
          cpu_frequency: 0,
          connection_quality: {
            average_latency: 0,
            packet_loss_percent: 0,
            connection_stability: 0,
            gateway_latency: 0,
            dns_latency: 0,
            internet_latency: 0,
            jitter: 0
          },
          network_interfaces: [],
          protocol_breakdown: {
            tcp: 0,
            udp: 0,
            http: 0,
            https: 0,
            dns: 0
          },
          top_bandwidth_processes: []
        }
      };
      
      // Update the store with fallback data to prevent UI errors
      // Use type assertion to ensure TypeScript recognizes this as a SystemMetric
      dispatch(updateMetrics(fallbackMetrics as unknown as import('../../types/metrics').SystemMetric));
      dispatch(setWebSocketError('Failed to fetch metrics data: ' + 
        (error instanceof Error ? error.message : 'Unknown error')));
      dispatch(setConnectionStatus('error'));
      
      // Increment failure count for circuit breaker behavior
      const newFailureCount = failureCount + 1;
      setFailureCount(newFailureCount);
      
      // If we've reached max failures, switch to fallback endpoint
      if (newFailureCount >= maxFailures && !usingFallback) {
        console.log(`⚠️ Reached ${maxFailures} consecutive failures, switching to fallback endpoint`);
        setUsingFallback(true);
        lastFailureTimeRef.current = Date.now();
      }
    }
  };

  useEffect(() => {
    // Check backend availability first
    const checkAvailability = async () => {
      const isAvailable = await checkBackendAvailability(true);
      if (!isAvailable) {
        console.warn('⚠️ Backend not available, will retry with fallback mechanisms');
        dispatch(setConnectionStatus('error'));
        dispatch(setWebSocketError('Backend server not available'));
      }
      
      // Fetch metrics immediately on mount regardless of availability check
      // Our fetchMetrics has fallback mechanisms built in
      fetchMetrics();
    };
    
    checkAvailability();

    // Set up polling interval (every 5 seconds)
    pollingIntervalRef.current = setInterval(fetchMetrics, 5000);

    // Clean up on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);
  
  // This effect handles changes to the usingFallback state
  useEffect(() => {
    if (usingFallback) {
      console.log('🔄 Now using fallback endpoint for metrics');
      dispatch(setConnectionStatus('fallback'));
    } else if (failureCount === 0) {
      // Only update to connected if we're not in a failure state
      dispatch(setConnectionStatus('connected'));
    }
  }, [usingFallback, failureCount, dispatch]);

  // Just render children - this is a logic-only component
  return <>{children}</>;
};

export default MetricsProvider;
