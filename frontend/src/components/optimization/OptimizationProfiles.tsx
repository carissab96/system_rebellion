import React, { useState, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import './OptimizationProfiles.css';
import { 
  fetchOptimizationProfiles, 
  createOptimizationProfile,
  updateOptimizationProfile,
  deleteOptimizationProfile
} from '../../store/slices/optimizationSlice';
import Modal from '../common/Modal';

interface OptimizationProfileFormData {
  name: string;
  description: string;
  settings: {
    cpuThreshold: number;
    memoryThreshold: number;
    diskThreshold: number;
    networkThreshold: number;
    enableAutoTuning: boolean;
  };
}

const defaultFormData: OptimizationProfileFormData = {
  name: '',
  description: '',
  settings: {
    cpuThreshold: 80,
    memoryThreshold: 80,
    diskThreshold: 90,
    networkThreshold: 70,
    enableAutoTuning: false
  }
};

export const OptimizationProfiles: React.FC = () => {
  const dispatch = useAppDispatch();
  const { profiles, loading, error } = useAppSelector((state) => state.optimization);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState<OptimizationProfileFormData>(defaultFormData);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [snailQuote, setSnailQuote] = useState<string>('');

  const snailQuotes = [
    "The Meth Snail is frantically optimizing your system parameters!",
    "Speed is my middle name! Well, actually it's Methamphetamine, but close enough!",
    "These optimization profiles are like my stash - carefully measured and extremely potent!",
    "I'm tweaking these settings faster than I tweak on a Friday night!",
    "Sir Hawkington thinks these settings are too aggressive, but what does that monocle-wearing aristocrat know about SPEED?!"
  ];

  useEffect(() => {
    dispatch(fetchOptimizationProfiles());
    setSnailQuote(snailQuotes[Math.floor(Math.random() * snailQuotes.length)]);
  }, [dispatch]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSettingChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      settings: {
        ...formData.settings,
        [name]: type === 'checkbox' ? checked : Number(value)
      }
    });
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
    setFormData({
      name: profile.name,
      description: profile.description,
      settings: {
        cpuThreshold: profile.settings.cpuThreshold || 80,
        memoryThreshold: profile.settings.memoryThreshold || 80,
        diskThreshold: profile.settings.diskThreshold || 90,
        networkThreshold: profile.settings.networkThreshold || 70,
        enableAutoTuning: profile.settings.enableAutoTuning || false
      }
    });
    setEditingId(profile.id);
    setIsModalOpen(true);
  };

  const handleDelete = (id: string) => {
    if (window.confirm("The Meth Snail asks: Are you ABSOLUTELY SURE you want to delete this optimization profile? This action cannot be undone and the Snail will be VERY disappointed!")) {
      dispatch(deleteOptimizationProfile(id));
      setSnailQuote("The Meth Snail just watched you delete that profile and is now crying methamphetamine tears!");
    }
  };

  const openCreateModal = () => {
    setFormData(defaultFormData);
    setEditingId(null);
    setIsModalOpen(true);
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
        <h2>Optimization Profiles</h2>
        <div className="snail-quote">{snailQuote}</div>
        <button className="create-profile-button" onClick={openCreateModal}>
          <span className="button-icon">⚡</span>
          <span>Create New Profile</span>
        </button>
      </div>

      <div className="profiles-grid">
        {profiles && profiles.length > 0 ? (
          profiles.map((profile: any) => (
            <div key={profile.id} className="profile-card">
              <div className="profile-header">
                <h3>{profile.name}</h3>
                {profile.is_active && <span className="active-badge">ACTIVE</span>}
              </div>
              <p className="profile-description">{profile.description}</p>
              
              <div className="profile-settings">
                <div className="setting-item">
                  <span className="setting-label">CPU Threshold:</span>
                  <span className="setting-value">{profile.settings.cpuThreshold}%</span>
                </div>
                <div className="setting-item">
                  <span className="setting-label">Memory Threshold:</span>
                  <span className="setting-value">{profile.settings.memoryThreshold}%</span>
                </div>
                <div className="setting-item">
                  <span className="setting-label">Disk Threshold:</span>
                  <span className="setting-value">{profile.settings.diskThreshold}%</span>
                </div>
                <div className="setting-item">
                  <span className="setting-label">Network Threshold:</span>
                  <span className="setting-value">{profile.settings.networkThreshold}%</span>
                </div>
                <div className="setting-item">
                  <span className="setting-label">Auto-Tuning:</span>
                  <span className="setting-value">
                    {profile.settings.enableAutoTuning ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>
              
              <div className="profile-actions">
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
            <p>The Meth Snail hasn't created any optimization profiles yet.</p>
            <p>Create your first profile to unleash the Snail's optimization powers!</p>
          </div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? "Edit Optimization Profile" : "Create Optimization Profile"}
        size="medium"
      >
        <div className="profile-form">
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
          </div>
          
          <div className="form-actions">
            <button className="cancel-button" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button className="submit-button" onClick={handleSubmit}>
              {editingId ? "Update Profile" : "Create Profile"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default OptimizationProfiles;
