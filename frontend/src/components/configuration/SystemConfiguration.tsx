import React, { useState, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import './SystemConfiguration.css';
import { 
  fetchSystemConfigurations, 
  createSystemConfiguration,
  updateSystemConfiguration,
  deleteSystemConfiguration,
  applySystemConfiguration
} from '../../store/slices/configurationSlice';
import Modal from '../common/Modal';

interface SystemConfigurationFormData {
  name: string;
  description: string;
  config_type: 'NETWORK' | 'SYSTEM' | 'SECURITY' | 'PERFORMANCE';
  settings: {
    [key: string]: any;
  };
}

const defaultFormData: SystemConfigurationFormData = {
  name: '',
  description: '',
  config_type: 'SYSTEM',
  settings: {}
};

const getDefaultSettingsForType = (type: string) => {
  switch (type) {
    case 'NETWORK':
      return {
        dns_servers: ['8.8.8.8', '1.1.1.1'],
        use_ipv6: true,
        firewall_enabled: true,
        quantum_shadow_protection: true
      };
    case 'SYSTEM':
      return {
        power_profile: 'balanced',
        startup_programs_enabled: true,
        update_schedule: 'weekly',
        hawkington_monitoring: true
      };
    case 'SECURITY':
      return {
        firewall_level: 'high',
        auto_updates: true,
        port_scanning_protection: true,
        stick_anxiety_level: 'medium'
      };
    case 'PERFORMANCE':
      return {
        cpu_governor: 'performance',
        memory_compression: true,
        disk_write_cache: true,
        meth_snail_boost: true
      };
    default:
      return {};
  }
};

export const SystemConfiguration: React.FC = () => {
  const dispatch = useAppDispatch();
  const { configurations, loading, error } = useAppSelector((state) => state.configuration);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState<SystemConfigurationFormData>(defaultFormData);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [hawkingtonQuote, setHawkingtonQuote] = useState<string>('');

  const hawkingtonQuotes = [
    "Sir Hawkington is monitoring your configurations with distinguished elegance!",
    "I say, these configurations are most exquisite! *adjusts monocle*",
    "A gentleman's system is only as refined as its configurations, my dear user!",
    "These settings are absolutely splendid! Quite the sophisticated arrangement!",
    "I do believe these configurations will bring order to the chaos of your system!"
  ];

  useEffect(() => {
    dispatch(fetchSystemConfigurations());
    setHawkingtonQuote(hawkingtonQuotes[Math.floor(Math.random() * hawkingtonQuotes.length)]);
  }, [dispatch]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name === 'config_type') {
      setFormData({
        ...formData,
        config_type: value as any,
        settings: getDefaultSettingsForType(value)
      });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSettingChange = (key: string, value: any) => {
    setFormData({
      ...formData,
      settings: {
        ...formData.settings,
        [key]: typeof value === 'boolean' ? value : value
      }
    });
  };

  const handleSubmit = () => {
    if (editingId) {
      dispatch(updateSystemConfiguration({ id: editingId, ...formData }));
    } else {
      dispatch(createSystemConfiguration(formData));
    }
    setIsModalOpen(false);
    setFormData(defaultFormData);
    setEditingId(null);
    setHawkingtonQuote(hawkingtonQuotes[Math.floor(Math.random() * hawkingtonQuotes.length)]);
  };

  const handleEdit = (config: any) => {
    setFormData({
      name: config.name,
      description: config.description,
      config_type: config.config_type,
      settings: config.settings
    });
    setEditingId(config.id);
    setIsModalOpen(true);
  };

  const handleDelete = (id: string) => {
    if (window.confirm("Sir Hawkington inquires: Are you absolutely certain you wish to delete this distinguished configuration? This action cannot be undone and would be most unfortunate!")) {
      dispatch(deleteSystemConfiguration(id));
      setHawkingtonQuote("Sir Hawkington is utterly devastated by the loss of that magnificent configuration!");
    }
  };

  const handleApply = (id: string) => {
    dispatch(applySystemConfiguration(id));
    setHawkingtonQuote("Sir Hawkington is applying your configuration with the utmost elegance and precision!");
  };

  const openCreateModal = () => {
    setFormData({
      ...defaultFormData,
      settings: getDefaultSettingsForType('SYSTEM')
    });
    setEditingId(null);
    setIsModalOpen(true);
  };

  const getConfigTypeIcon = (type: string) => {
    switch (type) {
      case 'NETWORK': return '🌐';
      case 'SYSTEM': return '⚙️';
      case 'SECURITY': return '🔒';
      case 'PERFORMANCE': return '⚡';
      default: return '📋';
    }
  };

  if (loading) {
    return <div className="loading-container">Sir Hawkington is gathering your configurations with distinguished elegance...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <h3>Sir Hawkington has encountered a most unfortunate error!</h3>
        <p>{error}</p>
        <button onClick={() => dispatch(fetchSystemConfigurations())}>
          Assist Sir Hawkington in trying again
        </button>
      </div>
    );
  }

  return (
    <div className="system-configuration-container">
      <div className="configuration-header">
        <h2>System Configurations</h2>
        <div className="hawkington-quote">{hawkingtonQuote}</div>
        <div className="hawkington-icon">🧐</div>
        <button className="create-configuration-button" onClick={openCreateModal}>
          <span className="button-icon">⚙️</span>
          <span>Create New Configuration</span>
        </button>
      </div>

      <div className="configurations-grid">
        {configurations && configurations.length > 0 ? (
          configurations.map((config: any) => (
            <div key={config.id} className={`configuration-card ${config.is_active ? 'active' : ''}`}>
              <div className="configuration-header">
                <div className="config-type-icon">
                  {getConfigTypeIcon(config.config_type)}
                </div>
                <h3>{config.name}</h3>
                {config.is_active && <span className="active-badge">ACTIVE</span>}
              </div>
              
              <p className="configuration-description">{config.description}</p>
              <div className="configuration-type">
                Type: <span className="type-value">{config.config_type}</span>
              </div>
              
              <div className="configuration-settings">
                <h4>Settings</h4>
                {Object.entries(config.settings).map(([key, value]) => (
                  <div key={key} className="setting-item">
                    <span className="setting-label">{key.replace(/_/g, ' ')}:</span>
                    <span className="setting-value">
                      {typeof value === 'boolean' 
                        ? (value ? 'Enabled' : 'Disabled') 
                        : Array.isArray(value) 
                          ? value.join(', ') 
                          : String(value)}
                    </span>
                  </div>
                ))}
              </div>
              
              <div className="configuration-actions">
                <button className="edit-button" onClick={() => handleEdit(config)}>
                  Edit
                </button>
                <button className="apply-button" onClick={() => handleApply(config.id)}>
                  Apply
                </button>
                <button className="delete-button" onClick={() => handleDelete(config.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="no-configurations">
            <p>Sir Hawkington hasn't created any configurations yet.</p>
            <p>Create your first configuration to experience Sir Hawkington's distinguished system management!</p>
          </div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? "Edit System Configuration" : "Create System Configuration"}
        size="large"
      >
        <div className="configuration-form">
          <div className="form-group">
            <label htmlFor="name">Configuration Name:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g., Gaming Setup, Work Configuration, etc."
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="description">Description:</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe what this configuration is for..."
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="config_type">Configuration Type:</label>
            <select
              id="config_type"
              name="config_type"
              value={formData.config_type}
              onChange={handleInputChange}
            >
              <option value="NETWORK">Network</option>
              <option value="SYSTEM">System</option>
              <option value="SECURITY">Security</option>
              <option value="PERFORMANCE">Performance</option>
            </select>
          </div>
          
          <div className="form-group">
            <h4>Settings</h4>
            <div className="settings-grid">
              {Object.entries(formData.settings).map(([key, value]) => (
                <div key={key} className="setting-control">
                  <label htmlFor={key}>
                    {key.replace(/_/g, ' ')}:
                  </label>
                  
                  {typeof value === 'boolean' ? (
                    <div className="toggle-switch">
                      <input
                        type="checkbox"
                        id={key}
                        checked={value}
                        onChange={(e) => handleSettingChange(key, e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </div>
                  ) : Array.isArray(value) ? (
                    <input
                      type="text"
                      id={key}
                      value={value.join(', ')}
                      onChange={(e) => handleSettingChange(key, e.target.value.split(', '))}
                    />
                  ) : typeof value === 'number' ? (
                    <input
                      type="number"
                      id={key}
                      value={value}
                      onChange={(e) => handleSettingChange(key, Number(e.target.value))}
                    />
                  ) : (
                    <input
                      type="text"
                      id={key}
                      value={value}
                      onChange={(e) => handleSettingChange(key, e.target.value)}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
          
          <div className="form-actions">
            <button className="cancel-button" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button className="submit-button" onClick={handleSubmit}>
              {editingId ? "Update Configuration" : "Create Configuration"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default SystemConfiguration;
