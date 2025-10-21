// components/onboarding/hooks/useSystemDetection.ts
import { useState, useEffect } from 'react';

type OsType = 'windows' | 'macos' | 'linux' | 'unknown';

/**
 * A custom hook that detects the user's operating system.
 * It runs once on component mount and returns the detected OS.
 *
 * @returns {OsType} The detected operating system as a string.
 */
export const useSystemDetection = (): OsType => {
  const [osType, setOsType] = useState<OsType>('unknown');

  useEffect(() => {
    // This logic should only run on the client-side.
    if (typeof window !== 'undefined') {
      const platform = window.navigator.platform.toLowerCase();
      if (platform.includes('win')) {
        setOsType('windows');
      } else if (platform.includes('mac')) {
        setOsType('macos');
      } else if (platform.includes('linux')) {
        setOsType('linux');
      }
    }
  }, []); // Empty dependency array ensures this runs only once on mount

  return osType;
};