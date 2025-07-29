import { defaultAgentPreferences } from "./agentDefaults";

// utils/systemDetection.ts
export const detectOperatingSystem = (): string => {
    const platform = navigator.platform.toLowerCase();
    if (platform.includes('win')) return 'windows';
    if (platform.includes('mac')) return 'macos';
    if (platform.includes('linux')) return 'linux';
    return 'unknown';
  };
  
  export const getInstallInstructions = (os: string) => {
    // All that switch logic here
  };
  
  // utils/agentDefaults.ts
  export const adjustAgentDefaults = (systemProfile: any) => {
    const defaults = { ...defaultAgentPreferences };
    
    if (systemProfile.total_ram_gb <= 8) {
      defaults.snail_optimization_aggression = 3;
      // etc...
    }
    
    return defaults;
  };