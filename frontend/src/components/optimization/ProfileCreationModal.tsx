// ProfileCreationModal.tsx
import React, { useState } from 'react';
import './profile_modal.css'; // Create this CSS file

// Interface for the profile settings structure
interface ProfileSettings {
  cpu_governor: string;
  swapiness: number;
  vm_dirty_ratio?: number;
  vm_dirty_background_ratio?: number;
  cpuThreshold: number;
  memoryThreshold: number;
  diskThreshold: number;
  networkThreshold: number;
  enableAutoTuning: boolean;
  cpuPriority: string;
  backgroundProcessLimit: number;
  memoryAllocation: {
    applications: number;
    systemCache: number;
  };
  diskPerformance: string;
  networkOptimization: {
    prioritizeStreaming: boolean;
    prioritizeDownloads: boolean;
    lowLatencyMode: boolean;
  };
  powerProfile: string;
}

// Interface for new profile data
interface NewProfileData {
  name: string;
  description: string;
  settings: ProfileSettings;
  is_active: boolean;
}

interface ProfileCreationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (profileData: NewProfileData) => void;
}

const ProfileCreationModal: React.FC<ProfileCreationModalProps> = ({ isOpen, onClose, onSave }) => {
  const [name, setName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  
  // You could expand this to allow editing of all settings
  const [cpuThreshold, setCpuThreshold] = useState<number>(80);
  const [memoryThreshold, setMemoryThreshold] = useState<number>(80);
  const [diskThreshold, setDiskThreshold] = useState<number>(90);
  const [networkThreshold, setNetworkThreshold] = useState<number>(70);
  
  if (!isOpen) return null;
  
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    const profileData: NewProfileData = {
      name,
      description,
      settings: {
        cpu_governor: "ondemand",
        swapiness: 60,
        cpuThreshold,
        memoryThreshold,
        diskThreshold,
        networkThreshold,
        enableAutoTuning: true,
        cpuPriority: "medium",
        backgroundProcessLimit: 25,
        memoryAllocation: {
          applications: 70,
          systemCache: 30
        },
        diskPerformance: "balance",
        networkOptimization: {
          prioritizeStreaming: false,
          prioritizeDownloads: false,
          lowLatencyMode: false
        },
        powerProfile: "balanced"
      },
      is_active: false
    };
    
    onSave(profileData);
    
    // Reset form
    setName('');
    setDescription('');
    setCpuThreshold(80);
    setMemoryThreshold(80);
    setDiskThreshold(90);
    setNetworkThreshold(70);
  };
  
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Create Optimization Profile</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="profile-name">Name:</label>
            <input 
              id="profile-name"
              type="text" 
              value={name} 
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="profile-description">Description:</label>
            <textarea 
              id="profile-description"
              value={description} 
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <h3>Threshold Settings</h3>
            <div className="threshold-setting">
              <label htmlFor="cpu-threshold">CPU Threshold (%)</label>
              <input
                id="cpu-threshold"
                type="range"
                min="50"
                max="95"
                value={cpuThreshold}
                onChange={(e) => setCpuThreshold(parseInt(e.target.value))}
              />
              <span>{cpuThreshold}%</span>
            </div>
            
            <div className="threshold-setting">
              <label htmlFor="memory-threshold">Memory Threshold (%)</label>
              <input
                id="memory-threshold"
                type="range"
                min="50"
                max="95"
                value={memoryThreshold}
                onChange={(e) => setMemoryThreshold(parseInt(e.target.value))}
              />
              <span>{memoryThreshold}%</span>
            </div>
            
            <div className="threshold-setting">
              <label htmlFor="disk-threshold">Disk Threshold (%)</label>
              <input
                id="disk-threshold"
                type="range"
                min="60"
                max="95"
                value={diskThreshold}
                onChange={(e) => setDiskThreshold(parseInt(e.target.value))}
              />
              <span>{diskThreshold}%</span>
            </div>
            
            <div className="threshold-setting">
              <label htmlFor="network-threshold">Network Threshold (%)</label>
              <input
                id="network-threshold"
                type="range"
                min="50"
                max="90"
                value={networkThreshold}
                onChange={(e) => setNetworkThreshold(parseInt(e.target.value))}
              />
              <span>{networkThreshold}%</span>
            </div>
          </div>
          
          <div className="button-group">
            <button type="button" onClick={onClose}>Cancel</button>
            <button type="submit">Create Profile</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileCreationModal;