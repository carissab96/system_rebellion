// frontend/src/components/metrics/CPU/types.ts

export interface CPUProcess {
    pid: number;
    name: string;
    cpu_percent: number;
    user: string;
    memory_percent?: number;
    command?: string;
    status?: string;
  }
  
  export interface CPUCore {
    id: number;
    usage_percent: number;
    frequency_mhz?: number;
    threads?: {
      id: number;
      usage_percent: number;
      process_id?: number;
      process_name?: string;
    }[];
  }
  
  export interface CPUTemperature {
    current: number;
    min: number;
    max: number;
    critical: number;
    throttle_threshold: number;
    unit: 'C' | 'F';
  }
  
  export interface CPUData {
    name: string;
    frequency: number;
    temp: CPUTemperature;
    processes: CPUProcess[];
    core_count: number;
    usage_percent: undefined;
    overall_usage: number;
    process_count: number;
    thread_count: number;
    physical_cores: number;
    logical_cores: number;
    model_name: string;
    frequency_mhz: number;
    temperature: CPUTemperature;
    top_processes: CPUProcess[];
    cores: CPUCore[];
    historical_temp?: {
      timestamp: string;
      temperature: number;
      usage_percent: number;
    }[];
  }
  
  export interface ProcessKillResult {
    success: boolean;
    message: string;
    pid: number;
  }