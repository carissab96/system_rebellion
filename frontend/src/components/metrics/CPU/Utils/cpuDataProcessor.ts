// frontend/src/components/metrics/CPU/utils/cpuDataProcessor.ts

import { SystemMetric } from '../../../../types/metrics';
import { CPUData, CPUCore, CPUProcess, CPUTemperature } from '../types';

/**
 * Process CPU data from system metrics
 */
export function processCPUData(currentMetric: SystemMetric | null): {
  cpuData: CPUData | null;
  error: string | null;
} {
  if (!currentMetric) {
    return { cpuData: null, error: 'No metrics data available' };
  }
  
  // Try to find CPU data in the metric
  const rawCpuData = currentMetric.cpu || currentMetric.additional?.cpu_details;
  
  if (!rawCpuData) {
    return { cpuData: null, error: 'No CPU data found in metrics' };
  }
  
  try {
    // Check for required fields
    if (rawCpuData.usage_percent === undefined) {
      throw new Error('Missing CPU usage data');
    }
    
    // Build the CPU data structure
    const processedData: CPUData = {
        overall_usage: rawCpuData.usage_percent,
        process_count: rawCpuData.process_count || 0,
        thread_count: rawCpuData.thread_count || 0,
        physical_cores: rawCpuData.physical_cores || rawCpuData.core_count || 1,
        logical_cores: rawCpuData.logical_cores || rawCpuData.core_count || 1,
        model_name: rawCpuData.model_name || rawCpuData.name || 'Unknown CPU',
        frequency_mhz: rawCpuData.frequency_mhz || rawCpuData.frequency || 0,
        temperature: processCPUTemperature(rawCpuData.temperature || rawCpuData.temp),
        top_processes: processCPUProcesses(rawCpuData.top_processes || rawCpuData.processes),
        cores: processCPUCores(rawCpuData.cores),
        historical_temp: rawCpuData.historical_temp || [],
        usage_percent: undefined,
        core_count: 0,
        name: '',
        frequency: 0,
        temp: processCPUTemperature(rawCpuData.temperature || rawCpuData.temp),
        processes: []
    };
    
    return { cpuData: processedData, error: null };
  } catch (err) {
    console.error('Error processing CPU data:', err);
    return {
      cpuData: null,
      error: `Failed to process CPU data: ${err instanceof Error ? err.message : 'Unknown error'}`
    };
  }
}

/**
 * Process CPU temperature data
 */
function processCPUTemperature(tempData: any): CPUTemperature {
  if (!tempData) {
    // Default values if temperature data is missing
    return {
      current: 0,
      min: 0,
      max: 100,
      critical: 90,
      throttle_threshold: 80,
      unit: 'C'
    };
  }
  
  return {
    current: tempData.current || tempData.value || 0,
    min: tempData.min || 0,
    max: tempData.max || 100,
    critical: tempData.critical || tempData.critical_temp || 90,
    throttle_threshold: tempData.throttle_threshold || tempData.throttle || 80,
    unit: tempData.unit || 'C'
  };
}

/**
 * Process CPU processes data
 */
function processCPUProcesses(processesData: any[]): CPUProcess[] {
  if (!processesData || !Array.isArray(processesData)) {
    return [];
  }
  
  return processesData.map(proc => ({
    pid: proc.pid,
    name: proc.name,
    cpu_percent: proc.cpu_percent || proc.cpu_usage || 0,
    user: proc.user || proc.username || 'Unknown',
    memory_percent: proc.memory_percent || proc.mem_usage,
    command: proc.command || proc.cmd,
    status: proc.status
  }));
}

/**
 * Process CPU cores data
 */
function processCPUCores(coresData: any[]): CPUCore[] {
  if (!coresData || !Array.isArray(coresData)) {
    return [];
  }
  
  return coresData.map((core, index) => ({
    id: core.id || index,
    usage_percent: core.usage_percent || core.usage || 0,
    frequency_mhz: core.frequency_mhz || core.frequency,
    threads: processThreads(core.threads)
  }));
}

/**
 * Process CPU threads data
 */
function processThreads(threadsData: any[]) {
  if (!threadsData || !Array.isArray(threadsData)) {
    return [];
  }
  
  return threadsData.map((thread, index) => ({
    id: thread.id || index,
    usage_percent: thread.usage_percent || thread.usage || 0,
    process_id: thread.process_id || thread.pid,
    process_name: thread.process_name
  }));
}

/**
 * Extract historical CPU data from metrics
 */
export function processHistoricalCPUData(historicalMetrics: SystemMetric[]) {
  if (!historicalMetrics || historicalMetrics.length === 0) {
    return [];
  }
  
  return historicalMetrics.map(metric => {
    const cpuData = metric.cpu || metric.additional?.cpu_details;
    
    if (!cpuData) {
      return {
        timestamp: metric.timestamp,
        usage_percent: 0,
        temperature: 0
      };
    }
    
    return {
      timestamp: metric.timestamp,
      usage_percent: cpuData.usage_percent || 0,
      temperature: cpuData.temperature?.current || cpuData.temp?.current || 0
    };
  });
}