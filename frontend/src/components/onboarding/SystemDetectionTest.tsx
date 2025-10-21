import React, { useState, useEffect } from 'react';

import { defaultAgentPreferences } from './utils/agentDefaults';
import { 
  detectOperatingSystem, 
  adjustAgentDefaults, 
  type SystemProfile,
  __testAdjustments 
} from './utils/systemDetection';

const SystemDetectionTest: React.FC = () => {
  const [systemProfile, setSystemProfile] = useState<Partial<SystemProfile>>({});
  const [detectedOS, setDetectedOS] = useState<string>('');
  const [adjustedPrefs, setAdjustedPrefs] = useState(defaultAgentPreferences);
  const [testProfiles, setTestProfiles] = useState<{
    lowEnd: ReturnType<typeof __testAdjustments.getLowEndSystemDefaults>;
    highEnd: ReturnType<typeof __testAdjustments.getHighEndSystemDefaults>;
  } | null>(null);

  useEffect(() => {
    // Detect current OS
    const os = detectOperatingSystem();
    setDetectedOS(os);
    
    // Load test profiles
    setTestProfiles({
      lowEnd: __testAdjustments.getLowEndSystemDefaults(),
      highEnd: __testAdjustments.getHighEndSystemDefaults()
    });
  }, []);

  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const newValue = type === 'number' ? Number(value) : 
                    type === 'checkbox' ? (e.target as HTMLInputElement).checked : 
                    value;
    
    setSystemProfile(prev => ({
      ...prev,
      [name]: newValue
    }));
  };

  const applyProfile = () => {
    const profile: SystemProfile = {
      os_type: systemProfile.os_type || 'unknown',
      os_version: systemProfile.os_version || '1.0',
      total_ram_gb: systemProfile.total_ram_gb || 8,
      storage_type: systemProfile.storage_type || 'SSD',
      total_storage_gb: systemProfile.total_storage_gb || 512,
      cpu_cores: systemProfile.cpu_cores || 4,
      is_virtual: systemProfile.is_virtual || false,
      network_type: systemProfile.network_type || 'ethernet',
      admin_access: systemProfile.admin_access || 'standard',
      mdm_controlled: systemProfile.mdm_controlled || false,
      custom_restrictions: systemProfile.custom_restrictions || []
    };

    const adjusted = adjustAgentDefaults(profile);
    setAdjustedPrefs(adjusted);
  };

  const renderPreference = (key: string, value: any) => (
    <div key={key} className="flex justify-between py-1">
      <span className="font-mono text-sm">{key}:</span>
      <span className="font-mono text-sm">
        {typeof value === 'number' ? value.toFixed(2) : String(value)}
      </span>
    </div>
  );

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">System Detection & Preference Adjustment Test</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* System Profile Input */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-4">System Profile</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Detected OS:</label>
              <input 
                type="text" 
                value={detectedOS} 
                readOnly 
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">OS Type:</label>
              <select
                name="os_type"
                value={systemProfile.os_type || ''}
                onChange={handleProfileChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              >
                <option value="">Select OS</option>
                <option value="windows">Windows</option>
                <option value="macos">macOS</option>
                <option value="linux">Linux</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">CPU Cores:</label>
              <input
                type="number"
                name="cpu_cores"
                min="1"
                max="64"
                value={systemProfile.cpu_cores || ''}
                onChange={handleProfileChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Total RAM (GB):</label>
              <input
                type="number"
                name="total_ram_gb"
                min="1"
                max="512"
                value={systemProfile.total_ram_gb || ''}
                onChange={handleProfileChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_virtual"
                name="is_virtual"
                checked={systemProfile.is_virtual || false}
                onChange={handleProfileChange}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="is_virtual" className="ml-2 block text-sm text-gray-700">
                Virtual Machine
              </label>
            </div>

            <button
              onClick={applyProfile}
              className="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Apply Profile
            </button>
          </div>
        </div>

        {/* Adjusted Preferences */}
        <div className="space-y-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Adjusted Preferences</h2>
            <div className="space-y-2">
              {Object.entries(adjustedPrefs).map(([key, value]) => 
                renderPreference(key, value)
              )}
            </div>
          </div>

          {/* Test Profiles */}
          {testProfiles && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-medium text-blue-800 mb-2">Low-End System</h3>
                <div className="space-y-1">
                  {Object.entries(testProfiles.lowEnd)
                    .filter(([key]) => key in defaultAgentPreferences)
                    .slice(0, 5)
                    .map(([key, value]) => renderPreference(key, value))}
                </div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-medium text-green-800 mb-2">High-End System</h3>
                <div className="space-y-1">
                  {Object.entries(testProfiles.highEnd)
                    .filter(([key]) => key in defaultAgentPreferences)
                    .slice(0, 5)
                    .map(([key, value]) => renderPreference(key, value))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemDetectionTest;
