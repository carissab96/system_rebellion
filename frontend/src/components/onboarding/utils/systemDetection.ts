import type { AgentPreferences } from "./agentDefaults";
import { defaultAgentPreferences } from "./agentDefaults";
import { defaultMonitoringPreferences, type MonitoringPreferences } from "./monitoringDefaults";

// System profile interface based on OnboardingContext.tsx
export interface SystemProfile {
  os_type: string;
  os_version: string;
  total_ram_gb: number;
  storage_type: string;
  total_storage_gb: number;
  cpu_cores: number;
  is_virtual: boolean;
  network_type: string;
  admin_access: string;
  mdm_controlled: boolean;
  custom_restrictions: string[];
}

/**
 * Adjusts agent preferences based on system profile
 * @param systemProfile The system profile containing hardware/software information
 * @returns Adjusted agent preferences
 */
export const adjustAgentDefaults = (systemProfile: Partial<SystemProfile>): AgentPreferences => {
  // Start with default preferences
  const preferences = { ...defaultAgentPreferences };
  
  // Log any missing critical fields
  const missingFields = [
    'total_ram_gb',
    'storage_type',
    'cpu_cores',
    'is_virtual',
    'network_type',
    'admin_access',
    'mdm_controlled'
  ].filter(field => systemProfile[field as keyof SystemProfile] === undefined);
  
  if (missingFields.length > 0) {
    console.warn(`Missing system profile fields: ${missingFields.join(', ')}. Using defaults.`);
  }
  
  // Adjust based on available system information
  try {
    // RAM-based adjustments
    const ramGb = systemProfile.total_ram_gb || 8; // Default to 8GB if not provided
    if (ramGb <= 4) {
      // Very low memory system
      preferences.snail_optimization_aggression = 2;
      preferences.hamster_3am_activity_boost = 2;
      preferences.hamster_disk_intervention_threshold = 50;
    } else if (ramGb <= 8) {
      // Low memory system
      preferences.snail_optimization_aggression = 3;
      preferences.hamster_3am_activity_boost = 3;
      preferences.hamster_disk_intervention_threshold = 60;
    } else if (ramGb >= 32) {
      // High memory system
      preferences.snail_optimization_aggression = 7;
      preferences.hamster_3am_activity_boost = 7;
      preferences.hamster_disk_intervention_threshold = 80;
    }
    
    // Storage type adjustments
    if (systemProfile.storage_type === 'hdd') {
      preferences.hamster_disk_intervention_threshold = Math.min(
        preferences.hamster_disk_intervention_threshold || 100,
        60
      );
      preferences.hamster_beer_optimal_level = 4;
    } else if (systemProfile.storage_type === 'ssd' || systemProfile.storage_type === 'nvme') {
      preferences.hamster_disk_intervention_threshold = 80;
      preferences.hamster_beer_optimal_level = 6;
    }
    
    // Virtual machine adjustments
    if (systemProfile.is_virtual) {
      preferences.hawkington_analysis_thoroughness = Math.max(
        (preferences.hawkington_analysis_thoroughness || 5) - 1,
        1
      );
      preferences.qsp_phase_shift_threshold = 7;
    }
    
    // Network environment adjustments
    const networkType = systemProfile.network_type?.toLowerCase() || 'home';
    if (networkType.includes('enterprise') || networkType.includes('corporate')) {
      preferences.hawkington_triage_emergency_threshold = 90;
      preferences.hamster_bob_wildness_factor = 5;
      preferences.qsp_phase_shift_threshold = 7;
    } else if (networkType.includes('public') || networkType.includes('untrusted')) {
      preferences.hawkington_analysis_thoroughness = 8;
      preferences.stick_base_anxiety = 35;
    }
    
    // Admin access level adjustments
    const adminAccess = systemProfile.admin_access?.toLowerCase() || 'standard';
    if (adminAccess === 'none' || adminAccess === 'limited') {
      preferences.agent_interaction_frequency = 3;
      preferences.cross_agent_memory_sharing = 1;
      preferences.hamster_bob_wildness_factor = Math.min(
        preferences.hamster_bob_wildness_factor || 5,
        3
      );
    } else if (adminAccess === 'administrator' || adminAccess === 'root') {
      preferences.agent_interaction_frequency = 7;
      preferences.cross_agent_memory_sharing = 7;
    }
    
    // MDM/restrictions adjustments
    if (systemProfile.mdm_controlled) {
      preferences.hawkington_triage_emergency_threshold = 90;
      preferences.hamster_bob_wildness_factor = Math.min(
        preferences.hamster_bob_wildness_factor || 5,
        4
      );
      preferences.qsp_phase_shift_threshold = 8;
    }
    
    // Apply any custom restrictions
    const restrictions = systemProfile.custom_restrictions || [];
    if (restrictions.includes('no_3am_operations')) {
      preferences.hamster_3am_activity_boost = 0;
    }
    if (restrictions.includes('low_resource_mode')) {
      preferences.snail_optimization_aggression = Math.max(
        (preferences.snail_optimization_aggression || 5) - 2,
        1
      );
      preferences.hamster_3am_activity_boost = 2;
    }
    
    return preferences;
  } catch (error) {
    console.error('Error adjusting agent preferences:', error);
    return defaultAgentPreferences;
  }
};

/**
 * Adjusts monitoring preferences based on system profile
 * @param systemProfile The system profile containing hardware/software information
 * @returns Adjusted monitoring preferences
 */
export const adjustMonitoringDefaults = (
  systemProfile: Partial<SystemProfile>
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

/**
 * Detects the operating system using modern User-Agent Client Hints API when available,
 * with fallback to the legacy approach.
 * @returns Detected OS type (windows, macos, linux, or unknown)
 */
export const detectOperatingSystem = async (): Promise<string> => {
  try {
    // Try to use User-Agent Client Hints API first (modern approach)
    if ('userAgentData' in navigator) {
      const uaData = (navigator as any).userAgentData;
      if (uaData && uaData.platform) {
        const platform = uaData.platform.toLowerCase();
        if (platform.includes('windows')) return 'windows';
        if (platform.includes('macos') || platform.includes('mac')) return 'macos';
        if (platform.includes('linux')) return 'linux';
      }
      
      // If platform isn't available in userAgentData, try the highEntropyValues
      try {
        const highEntropyValues = await (navigator as any).userAgentData.getHighEntropyValues(['platform']);
        if (highEntropyValues.platform) {
          const platform = highEntropyValues.platform.toLowerCase();
          if (platform.includes('windows')) return 'windows';
          if (platform.includes('macos') || platform.includes('mac')) return 'macos';
          if (platform.includes('linux')) return 'linux';
        }
      } catch (e) {
        console.debug('High-entropy values not available:', e);
      }
    }
    
    // Fallback to more reliable userAgent parsing
    const userAgent = navigator.userAgent.toLowerCase();
    
    // Windows detection
    if (userAgent.includes('win')) return 'windows';
    
    // macOS detection
    if (userAgent.includes('mac') || userAgent.includes('iphone') || userAgent.includes('ipad')) {
      // Check for iOS devices that identify as Mac
      if (/ipad|iphone|ipod/.test(userAgent) && !(window as any).MSStream) {
        return 'ios';
      }
      return 'macos';
    }
    
    // Android detection (which reports as Linux in userAgent)
    if (userAgent.includes('android')) return 'android';
    
    // Linux detection (must come after Android check)
    if (userAgent.includes('linux') || userAgent.includes('x11') || userAgent.includes('x86_64')) {
      // Check for Chrome OS
      if (userAgent.includes('cros')) return 'chromeos';
      return 'linux';
    }
    
    // iOS detection (for older browsers)
    if (userAgent.includes('iphone') || userAgent.includes('ipad') || userAgent.includes('ipod')) {
      return 'ios';
    }
    
    return 'unknown';
  } catch (error) {
    console.error('Error detecting operating system:', error);
    return 'unknown';
  }
};

/**
 * Gets installation instructions for a specific OS
 * @param os The target operating system
 * @returns Installation instructions as a string
 */
export const getInstallInstructions = (os: string): string => {
  const instructions: Record<string, string> = {
    windows: 'Download the Windows installer from our website and run it with administrator privileges.',
    macos: 'Download the macOS package and drag the application to your Applications folder.',
    linux: 'Add our repository and install using your distribution\'s package manager.',
    default: 'Please visit our website for installation instructions for your operating system.'
  };
  
  return instructions[os.toLowerCase()] || instructions.default;
};