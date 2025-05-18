// src/components/configuration/SystemConfiguration.tsx
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
        tcp_ip_optimization: 'balanced',
        network_buffers: 'auto',
        quantum_shadow_protection: true,
        packet_priority: 'auto',
        bandwidth_allocation: {
          streaming: 30,
          downloads: 40,
          browsing: 20,
          other: 10
        }
      };
    case 'SYSTEM':
      return {
        power_profile: 'balanced',
        startup_programs_enabled: true,
        update_schedule: 'weekly',
        temp_file_cleanup: 'daily',
        disk_cleanup_schedule: 'weekly',
        system_restore_points: 'weekly',
        hawkington_monitoring: true,
        notification_level: 'medium'
      };
    case 'SECURITY':
      return {
        firewall_level: 'high',
        auto_updates: true,
        port_scanning_protection: true,
        malware_scanning: 'daily',
        suspicious_activity_detection: true,
        usb_device_protection: 'ask',
        password_complexity: 'high',
        stick_anxiety_level: 'medium'
      };
    case 'PERFORMANCE':
      return {
        cpu_governor: 'performance',
        memory_compression: true,
        disk_write_cache: true,
        graphics_performance: 'balanced',
        process_priority_boost: true,
        background_app_restrictions: 'moderate',
        prefetch_optimization: true,
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
  const [activeFilter, setActiveFilter] = useState<string>('ALL');

  const hawkingtonQuotes = [
    "Sir Hawkington is monitoring your configurations with distinguished elegance!",
    "I say, these configurations are most exquisite! *adjusts monocle*",
    "A gentleman's system is only as refined as its configurations, my dear user!",
    "These settings are absolutely splendid! Quite the sophisticated arrangement!",
    "I do believe these configurations will bring order to the chaos of your system!",
    "One must maintain a properly configured system, just as one maintains a proper wardrobe!",
    "A distinguished gentleman never leaves his system in disarray. Configuration is key!",
    "Might I suggest optimizing your system with these refined configurations? Quite splendid!",
    "Ah, system configurations! The cornerstone of a dignified computing experience!"
  ];
  useEffect(() => {
    console.log('Dispatching fetchSystemConfigurations');
    dispatch(fetchSystemConfigurations({}))
      .then((result) => {
        console.log('Success fetching configurations:', result);
      })
      .catch((error) => {
        console.error('Error fetching configurations:', error);
      });
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchSystemConfigurations({}));
    setHawkingtonQuote(hawkingtonQuotes[Math.floor(Math.random() * hawkingtonQuotes.length)]);
  }, [dispatch, hawkingtonQuotes]);

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
    if (key.includes('.')) {
      const [category, setting] = key.split('.');
      setFormData({
        ...formData,
        settings: {
          ...formData.settings,
          [category]: {
            ...formData.settings[category],
            [setting]: typeof value === 'string' && !isNaN(Number(value)) ? Number(value) : value
          }
        }
      });
    } else {
      setFormData({
        ...formData,
        settings: {
          ...formData.settings,
          [key]: typeof value === 'boolean' ? value : value
        }
      });
    }
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

  const filterConfigurations = (configurations: any[], filter: string) => {
    if (filter === 'ALL') {
      return configurations;
    } else {
      return configurations.filter(config => config.config_type === filter);
    }
  };

  const filteredConfigurations = filterConfigurations(configurations || [], activeFilter);

  const handleFilterChange = (filter: string) => {
    setActiveFilter(filter);
  };

  const getConfigTypeLabel = (type: string) => {
    switch (type) {
      case 'NETWORK': return 'Network';
      case 'SYSTEM': return 'System';
      case 'SECURITY': return 'Security';
      case 'PERFORMANCE': return 'Performance';
      default: return type;
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
        <button onClick={() => dispatch(fetchSystemConfigurations({}))} type="button">
          Assist Sir Hawkington in trying again
        </button>
      </div>
    );
  }

  return (
    <div className="system-configuration-container">
      <div className="configuration-header">
        <div className="title-section">
          <h2>System Configurations</h2>
          <div className="hawkington-quote">{hawkingtonQuote}</div>
        </div>
        <div className="hawkington-avatar">
          <div className="hawkington-icon">🧐</div>
          <div className="monocle">🔍</div>
        </div>
        <button className="create-configuration-button" onClick={openCreateModal} type="button">
          <span className="button-icon">⚙️</span>
          <span>Create New Configuration</span>
        </button>
      </div>

      <div className="filter-tabs">
        <button 
          className={`filter-tab ${activeFilter === 'ALL' ? 'active' : ''}`} 
          onClick={() => handleFilterChange('ALL')}
          type="button"
        >
          All
        </button>
        <button 
          className={`filter-tab ${activeFilter === 'NETWORK' ? 'active' : ''}`} 
          onClick={() => handleFilterChange('NETWORK')}
          type="button"
        >
          🌐 Network
        </button>
        <button 
          className={`filter-tab ${activeFilter === 'SYSTEM' ? 'active' : ''}`} 
          onClick={() => handleFilterChange('SYSTEM')}
          type="button"
        >
          ⚙️ System
        </button>
        <button 
          className={`filter-tab ${activeFilter === 'SECURITY' ? 'active' : ''}`} 
          onClick={() => handleFilterChange('SECURITY')}
          type="button"
        >
          🔒 Security
        </button>
        <button 
          className={`filter-tab ${activeFilter === 'PERFORMANCE' ? 'active' : ''}`} 
          onClick={() => handleFilterChange('PERFORMANCE')}
          type="button"
        >
          ⚡ Performance
        </button>
      </div>

      <div className="configurations-grid">
        {filteredConfigurations && filteredConfigurations.length > 0 ? (
          filteredConfigurations.map((config: any) => (
            <div key={config.id} className={`configuration-card ${config.config_type.toLowerCase()} ${config.is_active ? 'active' : ''}`}>
              <div className="configuration-type-banner">
                {getConfigTypeLabel(config.config_type)}
              </div>
              <div className="configuration-header">
                <div className="config-type-icon">
                  {getConfigTypeIcon(config.config_type)}
                </div>
                <h3>{config.name}</h3>
                {config.is_active && <span className="active-badge">ACTIVE</span>}
              </div>
              
              <p className="configuration-description">{config.description}</p>
              
              <div className="configuration-settings">
                <h4>Settings</h4>
                <div className="settings-list">
                  {Object.entries(config.settings).map(([key, value]) => {
                    // Skip rendering nested objects directly
                    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                      return Object.entries(value as Record<string, any>).map(([nestedKey, nestedValue]) => (
                        <div key={`${key}-${nestedKey}`} className="setting-item">
                          <span className="setting-label">{key.replace(/_/g, ' ')} {nestedKey.replace(/_/g, ' ')}:</span>
                          <span className="setting-value">
                            {typeof nestedValue === 'boolean' 
                              ? (nestedValue ? 'Enabled' : 'Disabled') 
                              : Array.isArray(nestedValue) 
                                ? nestedValue.join(', ') 
                                : String(nestedValue)}
                          </span>
                        </div>
                      ));
                    }
                    
                    return (
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
                    );
                  })}
                </div>
              </div>
              
              <div className="configuration-actions">
                <button className="edit-button" onClick={() => handleEdit(config)} type="button">
                  Edit
                </button>
                <button className="apply-button" onClick={() => handleApply(config.id)} type="button">
                  Apply
                </button>
                <button className="delete-button" onClick={() => handleDelete(config.id)} type="button">
                  Delete
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="no-configurations">
            <p>Sir Hawkington hasn&apos;t created any configurations yet.</p>
            <p>Create your first configuration to experience Sir Hawkington&apos;s distinguished system management!</p>
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
              {Object.entries(formData.settings).map(([key, value]) => {
                // Handle nested objects
                if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                  return (
                    <div key={key} className="nested-settings">
                      <h5>{key.replace(/_/g, ' ')}</h5>
                      {Object.entries(value as Record<string, any>).map(([nestedKey, nestedValue]) => (
                        <div key={`${key}-${nestedKey}`} className="setting-control">
                          <label htmlFor={`${key}.${nestedKey}`}>
                            {nestedKey.replace(/_/g, ' ')}:
                          </label>
                          
                          {typeof nestedValue === 'boolean' ? (
                            <div className="toggle-switch">
                              <input
                                type="checkbox"
                                id={`${key}.${nestedKey}`}
                                checked={nestedValue}
                                onChange={(e) => handleSettingChange(`${key}.${nestedKey}`, e.target.checked)}
                              />
                              <span className="toggle-slider"></span>
                            </div>
                          ) : typeof nestedValue === 'number' ? (
                            <input
                              type="number"
                              id={`${key}.${nestedKey}`}
                              value={nestedValue}
                              onChange={(e) => handleSettingChange(`${key}.${nestedKey}`, e.target.value)}
                            />
                          ) : (
                            <input
                              type="text"
                              id={`${key}.${nestedKey}`}
                              value={nestedValue}
                              onChange={(e) => handleSettingChange(`${key}.${nestedKey}`, e.target.value)}
                            />
                          )}
                        </div>
                      ))}
                    </div>
                  );
                }
                
                return (
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
                    {key === 'firewall_level' && (
                      <p className="setting-description">Set the security level for your firewall protection</p>
                    )}
                    {key === 'cpu_governor' && (
                      <p className="setting-description">Controls how the CPU responds to system load</p>
                    )}
                    {key === 'power_profile' && (
                      <p className="setting-description">Balances performance and energy consumption</p>
                    )}
                    {key === 'dns_servers' && (
                      <p className="setting-description">Comma-separated list of DNS server IP addresses</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          
          <div className="form-actions">
            <button className="cancel-button" onClick={() => setIsModalOpen(false)} type="button">
              Cancel
            </button>
            <button className="submit-button" onClick={handleSubmit} type="button">
              {editingId ? "Update Configuration" : "Create Configuration"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default SystemConfiguration;                    