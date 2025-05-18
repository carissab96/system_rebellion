// src/components/optimization/OptimizationProfiles.tsx
import React, { useState, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import './OptimizationProfiles.css';
import { 
  fetchOptimizationProfiles, 
  createOptimizationProfile,
  updateOptimizationProfile,
  deleteOptimizationProfile,
  activateOptimizationProfile
} from '../../store/slices/optimizationSlice';
import Modal from '../common/Modal';

interface OptimizationProfileFormData {
  name: string;
  description: string;
  usageType: 'gaming' | 'creative' | 'development' | 'office' | 'browsing' | 'custom';
  settings: {
    cpuThreshold: number;
    memoryThreshold: number;
    diskThreshold: number;
    networkThreshold: number;
    enableAutoTuning: boolean;
    // Added settings for enhanced profiles
    cpuPriority: 'high' | 'medium' | 'low';
    backgroundProcessLimit: number;
    memoryAllocation: {
      applications: number; // percentage
      systemCache: number; // percentage
    };
    diskPerformance: 'speed' | 'balance' | 'powersave';
    networkOptimization: {
      prioritizeStreaming: boolean;
      prioritizeDownloads: boolean;
      lowLatencyMode: boolean;
    };
    powerProfile: 'performance' | 'balanced' | 'powersave';
  };
}

const defaultFormData: OptimizationProfileFormData = {
  name: '',
  description: '',
  usageType: 'custom',
  settings: {
    cpuThreshold: 80,
    memoryThreshold: 80,
    diskThreshold: 90,
    networkThreshold: 70,
    enableAutoTuning: false,
    // Default values for enhanced settings
    cpuPriority: 'medium',
    backgroundProcessLimit: 25,
    memoryAllocation: {
      applications: 70,
      systemCache: 30
    },
    diskPerformance: 'balance',
    networkOptimization: {
      prioritizeStreaming: false,
      prioritizeDownloads: false,
      lowLatencyMode: false
    },
    powerProfile: 'balanced'
  }
};

export const OptimizationProfiles: React.FC = () => {
  const dispatch = useAppDispatch();
  const { profiles, loading, error } = useAppSelector((state) => state.optimization);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState<OptimizationProfileFormData>(defaultFormData);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [snailQuote, setSnailQuote] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'basic' | 'advanced'>('basic');

  const snailQuotes = [
    "The Meth Snail is frantically optimizing your system parameters!",
    "Speed is my middle name! Well, actually it's Methamphetamine, but close enough!",
    "These optimization profiles are like my stash - carefully measured and extremely potent!",
    "I'm tweaking these settings faster than I tweak on a Friday night!",
    "Sir Hawkington thinks these settings are too aggressive, but what does that monocle-wearing aristocrat know about SPEED?!",
    "ZOOM ZOOM! Your system will be BLAZING after I'm done with it!",
    "Gaming? Creative work? Office tasks? The Meth Snail has a profile for EVERYTHING!",
    "72 HOURS WITHOUT SLEEP AND I'VE OPTIMIZED 147 SYSTEMS! I CAN SEE THROUGH TIME!"
  ];

  useEffect(() => {
    dispatch(fetchOptimizationProfiles());
    setSnailQuote(snailQuotes[Math.floor(Math.random() * snailQuotes.length)]);
  }, [dispatch]);

  const getInitialFormForUsageType = (usageType: string): OptimizationProfileFormData => {
    const baseForm = { ...defaultFormData, usageType: usageType as any };
    
    switch(usageType) {
      case 'gaming':
        return {
          ...baseForm,
          name: 'Gaming Profile',
          description: 'Optimized for maximum gaming performance',
          settings: {
            ...baseForm.settings,
            cpuThreshold: 90,
            memoryThreshold: 85,
            diskThreshold: 95,
            networkThreshold: 60,
            cpuPriority: 'high',
            backgroundProcessLimit: 10,
            memoryAllocation: {
              applications: 85,
              systemCache: 15
            },
            diskPerformance: 'speed',
            networkOptimization: {
              prioritizeStreaming: false,
              prioritizeDownloads: false,
              lowLatencyMode: true
            },
            powerProfile: 'performance'
          }
        };
        
      case 'creative':
        return {
          ...baseForm,
          name: 'Creative Workstation',
          description: 'Optimized for creative applications like video editing and 3D rendering',
          settings: {
            ...baseForm.settings,
            cpuThreshold: 85,
            memoryThreshold: 90,
            diskThreshold: 90,
            networkThreshold: 75,
            cpuPriority: 'high',
            backgroundProcessLimit: 15,
            memoryAllocation: {
              applications: 80,
              systemCache: 20
            },
            diskPerformance: 'speed',
            networkOptimization: {
              prioritizeStreaming: false,
              prioritizeDownloads: true,
              lowLatencyMode: false
            },
            powerProfile: 'performance'
          }
        };
        
      case 'development':
        return {
          ...baseForm,
          name: 'Development Environment',
          description: 'Balanced optimization for coding and testing',
          settings: {
            ...baseForm.settings,
            cpuThreshold: 80,
            memoryThreshold: 85,
            diskThreshold: 85,
            networkThreshold: 70,
            cpuPriority: 'medium',
            backgroundProcessLimit: 20,
            memoryAllocation: {
              applications: 75,
              systemCache: 25
            },
            diskPerformance: 'balance',
            networkOptimization: {
              prioritizeStreaming: false,
              prioritizeDownloads: true,
              lowLatencyMode: false
            },
            powerProfile: 'balanced'
          }
        };
        
      case 'office':
        return {
          ...baseForm,
          name: 'Office Productivity',
          description: 'Optimized for office applications and multitasking',
          settings: {
            ...baseForm.settings,
            cpuThreshold: 75,
            memoryThreshold: 75,
            diskThreshold: 80,
            networkThreshold: 65,
            cpuPriority: 'medium',
            backgroundProcessLimit: 30,
            memoryAllocation: {
              applications: 65,
              systemCache: 35
            },
            diskPerformance: 'balance',
            networkOptimization: {
              prioritizeStreaming: false,
              prioritizeDownloads: false,
              lowLatencyMode: false
            },
            powerProfile: 'balanced'
          }
        };
        
      case 'browsing':
        return {
          ...baseForm,
          name: 'Web Browsing',
          description: 'Optimized for browsing with power efficiency',
          settings: {
            ...baseForm.settings,
            cpuThreshold: 70,
            memoryThreshold: 70,
            diskThreshold: 75,
            networkThreshold: 80,
            cpuPriority: 'low',
            backgroundProcessLimit: 35,
            memoryAllocation: {
              applications: 60,
              systemCache: 40
            },
            diskPerformance: 'powersave',
            networkOptimization: {
              prioritizeStreaming: true,
              prioritizeDownloads: false,
              lowLatencyMode: false
            },
            powerProfile: 'powersave'
          }
        };
        
      default:
        return defaultFormData;
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name === 'usageType') {
      // Load preset when usage type changes
      const newFormData = getInitialFormForUsageType(value);
      setFormData(newFormData);
      return;
    }
    
    setFormData({ ...formData, [name]: value });
  };

  const handleSettingChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;
    
    // Handle nested settings
    if (name.includes('.')) {
      const [category, setting] = name.split('.');
      setFormData({
        ...formData,
        settings: {
          ...formData.settings,
          [category]: {
            ...formData.settings[category as keyof typeof formData.settings],
            [setting]: type === 'checkbox' ? checked : 
                      type === 'number' || name.endsWith('Threshold') || name === 'backgroundProcessLimit' ? 
                      Number(value) : value
          }
        }
      });
    } else {
      setFormData({
        ...formData,
        settings: {
          ...formData.settings,
          [name]: type === 'checkbox' ? checked : 
                  type === 'number' || name.endsWith('Threshold') || name === 'backgroundProcessLimit' ? 
                  Number(value) : value
        }
      });
    }
  };

  const handleSubmit = () => {
    if (editingId) {
      dispatch(updateOptimizationProfile({ id: editingId, ...formData }));
    } else {
      dispatch(createOptimizationProfile(formData));
    }
    setIsModalOpen(false);
    setFormData(defaultFormData);
    setEditingId(null);
    setSnailQuote(snailQuotes[Math.floor(Math.random() * snailQuotes.length)]);
  };

  const handleEdit = (profile: any) => {
    // Convert from API format to our form format if needed
    const formattedProfile = {
      name: profile.name,
      description: profile.description,
      usageType: profile.usageType || 'custom',
      settings: {
        cpuThreshold: profile.settings.cpuThreshold || 80,
        memoryThreshold: profile.settings.memoryThreshold || 80,
        diskThreshold: profile.settings.diskThreshold || 90,
        networkThreshold: profile.settings.networkThreshold || 70,
        enableAutoTuning: profile.settings.enableAutoTuning || false,
        cpuPriority: profile.settings.cpuPriority || 'medium',
        backgroundProcessLimit: profile.settings.backgroundProcessLimit || 25,
        memoryAllocation: profile.settings.memoryAllocation || {
          applications: 70,
          systemCache: 30
        },
        diskPerformance: profile.settings.diskPerformance || 'balance',
        networkOptimization: profile.settings.networkOptimization || {
          prioritizeStreaming: false,
          prioritizeDownloads: false,
          lowLatencyMode: false
        },
        powerProfile: profile.settings.powerProfile || 'balanced'
      }
    };
    
    setFormData(formattedProfile);
    setEditingId(profile.id);
    setIsModalOpen(true);
    setActiveTab('basic');
  };

  const handleDelete = (id: string) => {
    if (window.confirm("The Meth Snail asks: Are you ABSOLUTELY SURE you want to delete this optimization profile? This action cannot be undone and the Snail will be VERY disappointed!")) {
      dispatch(deleteOptimizationProfile(id));
      setSnailQuote("The Meth Snail just watched you delete that profile and is now crying methamphetamine tears!");
    }
  };

  const handleActivate = (id: string) => {
    dispatch(activateOptimizationProfile(id));
    setSnailQuote("The Meth Snail is PUMPED to apply this optimization profile! ZOOOOOM!");
  };

  const openCreateModal = () => {
    setFormData(defaultFormData);
    setEditingId(null);
    setIsModalOpen(true);
    setActiveTab('basic');
  };

  if (loading) {
    return <div className="loading-container">The Meth Snail is frantically gathering your optimization profiles...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <h3>The Meth Snail crashed into a wall!</h3>
        <p>{error}</p>
        <button onClick={() => dispatch(fetchOptimizationProfiles())}>
          Give the Snail another hit and try again
        </button>
      </div>
    );
  }

  return (
    <div className="optimization-profiles-container">
      <div className="profiles-header">
        <h2>System Usage Profiles</h2>
        <div className="snail-quote">{snailQuote}</div>
        <button className="create-profile-button" onClick={openCreateModal}>
          <span className="button-icon">⚡</span>
          <span>Create New Usage Profile</span>
        </button>
      </div>

      <div className="profiles-grid">
        {profiles && profiles.length > 0 ? (
          profiles.map((profile: any) => (
            <div key={profile.id} className="profile-card">
              <div className="profile-header">
                <h3>{profile.name}</h3>
                <div className="profile-badges">
                  {profile.is_active && <span className="active-badge">ACTIVE</span>}
                  {profile.usageType && <span className={`type-badge ${profile.usageType}`}>{profile.usageType}</span>}
                </div>
              </div>
              <p className="profile-description">{profile.description}</p>
              
              <div className="profile-settings">
                <div className="setting-item">
                  <span className="setting-label">CPU Priority:</span>
                  <span className="setting-value">
                    {profile.settings.cpuPriority ? 
                      profile.settings.cpuPriority.charAt(0).toUpperCase() + profile.settings.cpuPriority.slice(1) : 
                      'Medium'}
                  </span>
                </div>
                <div className="setting-item">
                  <span className="setting-label">CPU Threshold:</span>
                  <span className="setting-value">{profile.settings.cpuThreshold}%</span>
                </div>
                <div className="setting-item">
                  <span className="setting-label">Memory Threshold:</span>
                  <span className="setting-value">{profile.settings.memoryThreshold}%</span>
                </div>
                <div className="setting-item">
                  <span className="setting-label">Disk Performance:</span>
                  <span className="setting-value">
                    {profile.settings.diskPerformance ? 
                      profile.settings.diskPerformance.charAt(0).toUpperCase() + profile.settings.diskPerformance.slice(1) : 
                      'Balanced'}
                  </span>
                </div>
                <div className="setting-item">
                  <span className="setting-label">Power Profile:</span>
                  <span className="setting-value">
                    {profile.settings.powerProfile ? 
                      profile.settings.powerProfile.charAt(0).toUpperCase() + profile.settings.powerProfile.slice(1) : 
                      'Balanced'}
                  </span>
                </div>
              </div>
              
              <div className="profile-actions">
                {!profile.is_active && (
                  <button className="activate-button" onClick={() => handleActivate(profile.id)}>
                    Activate
                  </button>
                )}
                <button className="edit-button" onClick={() => handleEdit(profile)}>
                  Edit
                </button>
                <button className="delete-button" onClick={() => handleDelete(profile.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="no-profiles">
            <p>The Meth Snail hasn't created any usage profiles yet.</p>
            <p>Create your first profile to unleash the Snail's optimization powers!</p>
          </div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? "Edit Usage Profile" : "Create Usage Profile"}
        size="large"
      >
        <div className="profile-form">
          {/* Basic Info Section */}
          <div className="form-tabs">
            <button 
              className={`tab-button ${activeTab === 'basic' ? 'active' : ''}`}
              onClick={() => setActiveTab('basic')}
            >
              Basic Info
            </button>
            <button 
              className={`tab-button ${activeTab === 'advanced' ? 'active' : ''}`}
              onClick={() => setActiveTab('advanced')}
            >
              Advanced Settings
            </button>
          </div>
          
          {activeTab === 'basic' && (
            <div className="form-tab-content">
              <div className="form-group">
                <label htmlFor="usageType">Profile Type:</label>
                <select
                  id="usageType"
                  name="usageType"
                  value={formData.usageType}
                  onChange={handleInputChange}
                >
                  <option value="custom">Custom</option>
                  <option value="gaming">Gaming</option>
                  <option value="creative">Creative Work</option>
                  <option value="development">Development</option>
                  <option value="office">Office Work</option>
                  <option value="browsing">Web Browsing</option>
                </select>
                <p className="form-help">Choose a preset or customize your own profile</p>
              </div>
              
              <div className="form-group">
                <label htmlFor="name">Profile Name:</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Gaming Mode, Work Mode, etc."
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="description">Description:</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Describe what this optimization profile is for..."
                />
              </div>
              
              <div className="form-group">
                <h4>Threshold Settings</h4>
                <div className="slider-container">
                  <label htmlFor="cpuThreshold">CPU Threshold: {formData.settings.cpuThreshold}%</label>
                  <input
                    type="range"
                    id="cpuThreshold"
                    name="cpuThreshold"
                    min="50"
                    max="95"
                    value={formData.settings.cpuThreshold}
                    onChange={handleSettingChange}
                  />
                  <p className="setting-description">Processes will be optimized when CPU usage exceeds this threshold</p>
                </div>
                
                <div className="slider-container">
                  <label htmlFor="memoryThreshold">Memory Threshold: {formData.settings.memoryThreshold}%</label>
                  <input
                    type="range"
                    id="memoryThreshold"
                    name="memoryThreshold"
                    min="50"
                    max="95"
                    value={formData.settings.memoryThreshold}
                    onChange={handleSettingChange}
                  />
    <p className="setting-description">Memory optimization kicks in at this usage percentage</p>
                </div>
                
                <div className="slider-container">
                  <label htmlFor="diskThreshold">Disk Threshold: {formData.settings.diskThreshold}%</label>
                  <input
                    type="range"
                    id="diskThreshold"
                    name="diskThreshold"
                    min="50"
                    max="95"
                    value={formData.settings.diskThreshold}
                    onChange={handleSettingChange}
                  />
                  <p className="setting-description">Disk optimization activates when usage reaches this level</p>
                </div>
                
                <div className="slider-container">
                  <label htmlFor="networkThreshold">Network Threshold: {formData.settings.networkThreshold}%</label>
                  <input
                    type="range"
                    id="networkThreshold"
                    name="networkThreshold"
                    min="50"
                    max="95"
                    value={formData.settings.networkThreshold}
                    onChange={handleSettingChange}
                  />
                  <p className="setting-description">Network traffic will be optimized at this utilization</p>
                </div>
              </div>
              
              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="enableAutoTuning"
                    checked={formData.settings.enableAutoTuning}
                    onChange={handleSettingChange}
                  />
                  Enable Auto-Tuning (The Meth Snail will optimize automatically)
                </label>
                <p className="setting-description">When enabled, the system will dynamically adjust settings based on usage patterns</p>
              </div>
            </div>
          )}
          
          {activeTab === 'advanced' && (
            <div className="form-tab-content">
              <div className="form-group">
                <h4>CPU Settings</h4>
                <div className="select-container">
                  <label htmlFor="cpuPriority">CPU Priority:</label>
                  <select
                    id="cpuPriority"
                    name="cpuPriority"
                    value={formData.settings.cpuPriority}
                    onChange={handleSettingChange}
                  >
                    <option value="low">Low (Power Saving)</option>
                    <option value="medium">Medium (Balanced)</option>
                    <option value="high">High (Performance)</option>
                  </select>
                </div>
                
                <div className="slider-container">
                  <label htmlFor="backgroundProcessLimit">Background Process Limit: {formData.settings.backgroundProcessLimit}</label>
                  <input
                    type="range"
                    id="backgroundProcessLimit"
                    name="backgroundProcessLimit"
                    min="5"
                    max="50"
                    value={formData.settings.backgroundProcessLimit}
                    onChange={handleSettingChange}
                  />
                  <p className="setting-description">Maximum number of background processes allowed</p>
                </div>
              </div>
              
              <div className="form-group">
                <h4>Memory Allocation</h4>
                <div className="slider-container">
                  <label htmlFor="memoryAllocation.applications">Applications: {formData.settings.memoryAllocation.applications}%</label>
                  <input
                    type="range"
                    id="memoryAllocation.applications"
                    name="memoryAllocation.applications"
                    min="50"
                    max="90"
                    value={formData.settings.memoryAllocation.applications}
                    onChange={handleSettingChange}
                  />
                  <p className="setting-description">Percentage of memory prioritized for applications</p>
                </div>
                
                <div className="slider-container">
                  <label htmlFor="memoryAllocation.systemCache">System Cache: {formData.settings.memoryAllocation.systemCache}%</label>
                  <input
                    type="range"
                    disabled
                    id="memoryAllocation.systemCache"
                    name="memoryAllocation.systemCache"
                    min="10"
                    max="50"
                    value={formData.settings.memoryAllocation.systemCache}
                  />
                  <p className="setting-description">Percentage of memory reserved for system cache</p>
                </div>
              </div>
              
              <div className="form-group">
                <h4>Disk Performance</h4>
                <div className="select-container">
                  <label htmlFor="diskPerformance">Disk Performance Mode:</label>
                  <select
                    id="diskPerformance"
                    name="diskPerformance"
                    value={formData.settings.diskPerformance}
                    onChange={handleSettingChange}
                  >
                    <option value="speed">Speed (Maximum Performance)</option>
                    <option value="balance">Balance (Default)</option>
                    <option value="powersave">Power Save (Extended Battery Life)</option>
                  </select>
                </div>
              </div>
              
              <div className="form-group">
                <h4>Network Optimization</h4>
                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      name="networkOptimization.prioritizeStreaming"
                      checked={formData.settings.networkOptimization.prioritizeStreaming}
                      onChange={handleSettingChange}
                    />
                    Prioritize Streaming Traffic
                  </label>
                  <p className="setting-description">Optimizes for video/audio streaming services</p>
                </div>
                
                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      name="networkOptimization.prioritizeDownloads"
                      checked={formData.settings.networkOptimization.prioritizeDownloads}
                      onChange={handleSettingChange}
                    />
                    Prioritize Downloads
                  </label>
                  <p className="setting-description">Optimizes for file transfers and downloads</p>
                </div>
                
                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      name="networkOptimization.lowLatencyMode"
                      checked={formData.settings.networkOptimization.lowLatencyMode}
                      onChange={handleSettingChange}
                    />
                    Low Latency Mode
                  </label>
                  <p className="setting-description">Optimizes for gaming and real-time applications</p>
                </div>
              </div>
              
              <div className="form-group">
                <h4>Power Management</h4>
                <div className="select-container">
                  <label htmlFor="powerProfile">Power Profile:</label>
                  <select
                    id="powerProfile"
                    name="powerProfile"
                    value={formData.settings.powerProfile}
                    onChange={handleSettingChange}
                  >
                    <option value="performance">Performance (Maximum Speed)</option>
                    <option value="balanced">Balanced (Default)</option>
                    <option value="powersave">Power Save (Battery Optimized)</option>
                  </select>
                </div>
              </div>
            </div>
          )}
          
          <div className="form-actions">
            <button 
              className="cancel-button" 
              onClick={() => setIsModalOpen(false)}
              type="button"
            >
              Cancel
            </button>
            <button 
              className="submit-button" 
              onClick={handleSubmit}
              type="button"
            >
              {editingId ? "Update Profile" : "Create Profile"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default OptimizationProfiles;