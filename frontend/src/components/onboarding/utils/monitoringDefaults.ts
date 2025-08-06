/**
 * Default monitoring preferences for the system
 */

export interface MonitoringPreferences {
  cpu_stress_weight: number;
  memory_stress_weight: number;
  disk_stress_weight: number;
  cpu_compliance_threshold: number;
  memory_compliance_threshold: number;
  temperature_paranoia_threshold: number;
  disk_cleanup_threshold: number;
  disk_emergency_threshold: number;
  fragmentation_threshold: number;
  latency_gaming_threshold: number;
  latency_streaming_threshold: number;
  latency_critical_threshold: number;
  packet_loss_intervention: number;
  alert_frequency: 'low' | 'balanced' | 'high';
  enable_3am_operations: boolean;
  quantum_interventions_allowed: boolean;
  cross_agent_collaboration: boolean;
}

export const defaultMonitoringPreferences: MonitoringPreferences = {
  cpu_stress_weight: 25,
  memory_stress_weight: 35,
  disk_stress_weight: 40,
  cpu_compliance_threshold: 80,
  memory_compliance_threshold: 85,
  temperature_paranoia_threshold: 75,
  disk_cleanup_threshold: 70,
  disk_emergency_threshold: 90,
  fragmentation_threshold: 20,
  latency_gaming_threshold: 20,
  latency_streaming_threshold: 50,
  latency_critical_threshold: 5,
  packet_loss_intervention: 1,
  alert_frequency: 'balanced',
  enable_3am_operations: true,
  quantum_interventions_allowed: true,
  cross_agent_collaboration: true
};

/**
 * Adjusts monitoring preferences based on system profile
 * @param systemProfile The system profile containing hardware/software information
 * @returns Adjusted monitoring preferences
 */
export const adjustMonitoringDefaults = (
  systemProfile: Partial<{
    total_ram_gb: number;
    cpu_cores: number;
    storage_type: string;
    network_type: string;
    is_virtual: boolean;
  }>
): MonitoringPreferences => {
  const monitoring = { ...defaultMonitoringPreferences };
  
  try {
    // RAM-based monitoring adjustments
    const ramGb = systemProfile.total_ram_gb || 8;
    if (ramGb <= 4) {
      monitoring.memory_stress_weight = 40;
      monitoring.memory_compliance_threshold = 75;
    } else if (ramGb >= 32) {
      monitoring.memory_stress_weight = 30;
      monitoring.memory_compliance_threshold = 90;
    }
    
    // CPU core adjustments
    const cpuCores = systemProfile.cpu_cores || 4;
    if (cpuCores <= 2) {
      monitoring.cpu_stress_weight = 30;
      monitoring.cpu_compliance_threshold = 75;
    } else if (cpuCores >= 8) {
      monitoring.cpu_stress_weight = 20;
      monitoring.cpu_compliance_threshold = 90;
    }
    
    // Storage adjustments
    if (systemProfile.storage_type === 'hdd') {
      monitoring.disk_stress_weight = 45;
      monitoring.disk_cleanup_threshold = 60;
      monitoring.fragmentation_threshold = 15;
    } else if (systemProfile.storage_type === 'ssd' || systemProfile.storage_type === 'nvme') {
      monitoring.disk_stress_weight = 35;
      monitoring.disk_cleanup_threshold = 75;
      monitoring.fragmentation_threshold = 25;
    }
    
    // Network environment adjustments
    const networkType = systemProfile.network_type?.toLowerCase() || 'home';
    if (networkType.includes('enterprise') || networkType.includes('corporate')) {
      monitoring.alert_frequency = 'high';
      monitoring.latency_critical_threshold = 3;
    } else if (networkType.includes('gaming') || networkType.includes('low_latency')) {
      monitoring.latency_gaming_threshold = 15;
      monitoring.latency_streaming_threshold = 30;
      monitoring.latency_critical_threshold = 2;
    }
    
    // Virtual machine adjustments
    if (systemProfile.is_virtual) {
      monitoring.temperature_paranoia_threshold = 85;
      monitoring.enable_3am_operations = false;
    }
    
    return monitoring;
  } catch (error) {
    console.error('Error adjusting monitoring preferences:', error);
    return defaultMonitoringPreferences;
  }
};
