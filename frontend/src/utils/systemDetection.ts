// utils/systemDetection.ts
// SYSTEM REBELLION - System Detection Utilities
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "Know thy hardware, optimize thy consciousness"
//
// Clean, professional system detection using browser APIs.
// No fake data. Real hardware info or graceful degradation.

export interface SystemRequirements {
  minRamGB: number;
  minCpuCores: number;
  recommendedRamGB: number;
  recommendedCpuCores: number;
}

export interface DetectedSystem {
  os: string;
  osVersion: string;
  ramGB: number | null;
  cpuCores: number | null;
  timezone: string;
  userAgent: string;
  platform: string;
  language: string;
  screenResolution: string;
  isOnline: boolean;
}

export interface SystemValidation {
  meetsMinimum: boolean;
  meetsRecommended: boolean;
  warnings: string[];
  errors: string[];
}

// System requirements for System Rebellion
export const SYSTEM_REQUIREMENTS: SystemRequirements = {
  minRamGB: 8,
  minCpuCores: 2,
  recommendedRamGB: 16,
  recommendedCpuCores: 4,
};

/**
 * Detect the operating system from user agent and platform
 */
export const detectOS = (): { os: string; version: string } => {
  const userAgent = navigator.userAgent.toLowerCase();
  const platform = navigator.platform.toLowerCase();

  // Windows detection
  if (userAgent.includes('win')) {
    if (userAgent.includes('windows nt 10.0')) return { os: 'Windows', version: '10/11' };
    if (userAgent.includes('windows nt 6.3')) return { os: 'Windows', version: '8.1' };
    if (userAgent.includes('windows nt 6.2')) return { os: 'Windows', version: '8' };
    if (userAgent.includes('windows nt 6.1')) return { os: 'Windows', version: '7' };
    return { os: 'Windows', version: 'Unknown' };
  }

  // macOS detection
  if (platform.includes('mac') || userAgent.includes('mac')) {
    const match = userAgent.match(/mac os x (\d+)[._](\d+)/);
    if (match) {
      const major = parseInt(match[1]);
      const minor = parseInt(match[2]);
      return { os: 'macOS', version: `${major}.${minor}` };
    }
    return { os: 'macOS', version: 'Unknown' };
  }

  // Linux detection
  if (platform.includes('linux') || userAgent.includes('linux')) {
    if (userAgent.includes('ubuntu')) return { os: 'Linux', version: 'Ubuntu' };
    if (userAgent.includes('fedora')) return { os: 'Linux', version: 'Fedora' };
    if (userAgent.includes('debian')) return { os: 'Linux', version: 'Debian' };
    if (userAgent.includes('arch')) return { os: 'Linux', version: 'Arch' };
    return { os: 'Linux', version: 'Unknown' };
  }

  // Fallback
  return { os: 'Unknown', version: 'Unknown' };
};

/**
 * Detect RAM in GB (if available via Device Memory API)
 * Note: This is an approximate value and may not be available in all browsers
 */
export const detectRAM = (): number | null => {
  // Device Memory API (Chrome, Edge, Opera)
  if ('deviceMemory' in navigator) {
    return (navigator as any).deviceMemory as number;
  }

  // Fallback: Not available
  return null;
};

/**
 * Detect CPU cores (logical processors)
 */
export const detectCPUCores = (): number | null => {
  if ('hardwareConcurrency' in navigator) {
    return navigator.hardwareConcurrency || null;
  }
  return null;
};

/**
 * Detect timezone
 */
export const detectTimezone = (): string => {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch {
    return 'UTC';
  }
};

/**
 * Get screen resolution
 */
export const getScreenResolution = (): string => {
  return `${window.screen.width}x${window.screen.height}`;
};

/**
 * Detect all system information
 */
export const detectSystem = (): DetectedSystem => {
  const { os, version } = detectOS();

  return {
    os,
    osVersion: version,
    ramGB: detectRAM(),
    cpuCores: detectCPUCores(),
    timezone: detectTimezone(),
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    screenResolution: getScreenResolution(),
    isOnline: navigator.onLine,
  };
};

/**
 * Validate system against requirements
 */
export const validateSystem = (
  detected: DetectedSystem,
  requirements: SystemRequirements = SYSTEM_REQUIREMENTS
): SystemValidation => {
  const warnings: string[] = [];
  const errors: string[] = [];

  // RAM validation
  if (detected.ramGB !== null) {
    if (detected.ramGB < requirements.minRamGB) {
      errors.push(
        `Your system has ${detected.ramGB}GB RAM. System Rebellion requires at least ${requirements.minRamGB}GB RAM for optimal performance.`
      );
    } else if (detected.ramGB < requirements.recommendedRamGB) {
      warnings.push(
        `Your system has ${detected.ramGB}GB RAM. We recommend ${requirements.recommendedRamGB}GB RAM for the best experience.`
      );
    }
  } else {
    warnings.push(
      'Unable to detect RAM. Please ensure you have at least 8GB RAM for optimal performance.'
    );
  }

  // CPU validation
  if (detected.cpuCores !== null) {
    if (detected.cpuCores < requirements.minCpuCores) {
      errors.push(
        `Your system has ${detected.cpuCores} CPU cores. System Rebellion requires at least ${requirements.minCpuCores} cores.`
      );
    } else if (detected.cpuCores < requirements.recommendedCpuCores) {
      warnings.push(
        `Your system has ${detected.cpuCores} CPU cores. We recommend ${requirements.recommendedCpuCores} cores for the best experience.`
      );
    }
  } else {
    warnings.push(
      'Unable to detect CPU cores. Please ensure you have at least 2 CPU cores.'
    );
  }

  // Online check
  if (!detected.isOnline) {
    errors.push('No internet connection detected. System Rebellion requires an active connection.');
  }

  const meetsMinimum = errors.length === 0;
  const meetsRecommended = meetsMinimum && warnings.length === 0;

  return {
    meetsMinimum,
    meetsRecommended,
    warnings,
    errors,
  };
};

/**
 * Test network latency to backend
 * Returns latency in milliseconds or null if failed
 */
export const testNetworkLatency = async (apiUrl: string): Promise<number | null> => {
  try {
    const start = performance.now();
    const response = await fetch(`${apiUrl}/api/health-check/ping`, {
      method: 'GET',
      cache: 'no-cache',
    });
    const end = performance.now();

    if (response.ok) {
      return Math.round(end - start);
    }
    return null;
  } catch {
    return null;
  }
};

/**
 * Check if ports are accessible (basic check)
 * This is a simplified check - real port scanning requires backend support
 */
export const checkPortAccessibility = async (apiUrl: string): Promise<boolean> => {
  try {
    const response = await fetch(`${apiUrl}/api/health-check/status`, {
      method: 'GET',
      cache: 'no-cache',
    });
    return response.ok;
  } catch {
    return false;
  }
};

/**
 * Format system info for display
 */
export const formatSystemInfo = (detected: DetectedSystem): string => {
  const parts: string[] = [];

  parts.push(`OS: ${detected.os} ${detected.osVersion}`);
  
  if (detected.ramGB !== null) {
    parts.push(`RAM: ${detected.ramGB}GB`);
  } else {
    parts.push('RAM: Unable to detect');
  }

  if (detected.cpuCores !== null) {
    parts.push(`CPU Cores: ${detected.cpuCores}`);
  } else {
    parts.push('CPU Cores: Unable to detect');
  }

  parts.push(`Timezone: ${detected.timezone}`);
  parts.push(`Resolution: ${detected.screenResolution}`);

  return parts.join(' | ');
};

// TODO: 30-day trial tracking
// - Add trial start date to user profile
// - Calculate days remaining
// - Show trial status in UI
// - Trigger upgrade prompts at 7 days, 3 days, 1 day, expired

// TODO: Usage metrics
// - Track agent usage per user
// - Track WebSocket connection time
// - Track API calls per user
// - Store metrics for billing/analytics

// TODO: Payment integration
// - Stripe/payment provider setup
// - Subscription tiers (if needed)
// - Upgrade flow from trial
// - Billing page in settings
