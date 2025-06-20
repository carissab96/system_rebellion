import React, { useState, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './SystemAlerts.css';
import { 
  fetchSystemAlerts, 
  markAlertAsRead,
  deleteSystemAlert,
  createSystemAlert,
  markAllAlertsAsRead,
  toggleAlertSelection,
  selectAllAlerts,
  deselectAllAlerts,
  deleteSelectedAlerts,
  updateAlertActionStatus,
  updateSelectedAlertsActionStatus,
  markSelectedAlertsAsRead
} from '../../store/slices/systemAlertsSlice';
import Modal from '../common/Modal';
import '../common/CharacterIcons.css'
import alertUtils from '../../utils/alertUtils';
import { Button } from '../../design-system/components';

const API_PATH = '/api/system-alerts';

interface SystemAlertFormData {
  title: string;
  message: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  is_read: boolean;
  additional_data?: any;
  created_at: string;
  updated_at: string;
}

const defaultFormData: SystemAlertFormData = {
  title: '',
  message: '',
  severity: 'MEDIUM',
  is_read: false,
  additional_data: {},
  created_at: '',
  updated_at: ''
};

export const SystemAlerts: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { alerts, loading, error, selectedCount } = useAppSelector((state) => {
    console.log('Current alerts state:', state.systemAlerts);
    return state.systemAlerts;
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);
  const [isPatternModalOpen, setIsPatternModalOpen] = useState(false);
  const [currentActionableAlert, setCurrentActionableAlert] = useState<any>(null);
  const [currentPatternAlert, setCurrentPatternAlert] = useState<any>(null);
  const [formData, setFormData] = useState<SystemAlertFormData>(defaultFormData);
  const [shadowQuote, setShadowQuote] = useState<string>('');
  const [debugInfo, setDebugInfo] = useState<string>('');
  const [actionResult, setActionResult] = useState<any>(null);
  const [showActionMenu, setShowActionMenu] = useState(false);
  const [expandedAlertId, setExpandedAlertId] = useState<string | null>(null);
  const [filterOptions, setFilterOptions] = useState({
    severity: 'ALL',
    read_status: 'ALL',
    action_status: 'ALL',
    date_range: 'ALL'
  });

  const shadowQuotes = [
    "The Quantum Shadow People are monitoring your router configurations...",
    "We've detected unusual activity in the quantum realm. Your router may be at risk.",
    "The shadows between dimensions suggest your system needs attention.",
    "We exist in the spaces between your packets. Your network traffic reveals all.",
    "Your router's quantum state is unstable. We recommend immediate reconfiguration."
  ];

  useEffect(() => {
    console.log('🔍 SystemAlerts component mounted - Dispatching fetchSystemAlerts');
    dispatch(fetchSystemAlerts({ skip: 0, limit: 20, is_read: undefined }))
      .then((result) => {
        console.log('✅ fetchSystemAlerts result:', result);
      })
      .catch((error) => {
        console.error('❌ fetchSystemAlerts error:', error);
        setDebugInfo(`Fetch error: ${JSON.stringify(error)}`);
      });
    setShadowQuote(shadowQuotes[Math.floor(Math.random() * shadowQuotes.length)]);
    
    // Generate test alerts for auto-tuner integration
    generateRealSystemAlerts();
  }, [dispatch]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = () => {
    dispatch(createSystemAlert(formData))
      .then(result => {
        console.log('Alert created successfully:', result);
        setIsModalOpen(false);
        setFormData(defaultFormData);
        setShadowQuote(shadowQuotes[Math.floor(Math.random() * shadowQuotes.length)]);
      })
      .catch(error => {
        console.error('Error creating alert:', error);
        setDebugInfo(`Create error: ${JSON.stringify(error)}`);
      });
  };

  const handleMarkAsRead = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    dispatch(markAlertAsRead(id))
      .then(result => {
        console.log('Alert marked as read:', result);
      })
      .catch(error => {
        console.error('Error marking alert as read:', error);
      });
  };

  const handleDelete = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (window.confirm("The Quantum Shadow People ask: Are you sure you want to delete this alert? This information will be lost to the void between dimensions.")) {
      dispatch(deleteSystemAlert(id))
        .then(result => {
          console.log('Alert deleted successfully:', result);
          setShadowQuote("The Quantum Shadow People have banished that alert to the void.");
        })
        .catch(error => {
          console.error('Error deleting alert:', error);
        });
    }
  };
    // Handle actionable alerts
    const handleAlertAction = (alert: any) => {
      console.log('Handling actionable alert:', alert);
      setCurrentActionableAlert(alert);
      
      // Check if the alert has additional_data with action information
      if (alert.additional_data && alert.additional_data.actionable) {
        const actionType = alert.additional_data.action_type;
        
        switch (actionType) {
          case 'apply_recommendation':
            setIsActionModalOpen(true);
            break;
          case 'view_metrics':
            // Navigate to metrics dashboard
            navigate('/dashboard');
            break;
          default:
            console.log('Unknown action type:', actionType);
        }
      }
    };
    
    // Handle pattern visualization
    const handlePatternVisualization = (alert: any) => {
      if (alert.additional_data && alert.additional_data.pattern_data) {
        setCurrentPatternAlert(alert);
        setIsPatternModalOpen(true);
      }
    };
    
    // Apply a recommendation from an alert
    const applyRecommendation = async () => {
      if (!currentActionableAlert || !currentActionableAlert.additional_data) return;
      
      const recommendationData = currentActionableAlert.additional_data.recommendation_data;
      if (!recommendationData) {
        console.error('No recommendation data found in alert');
        return;
      }
      
      try {
        // Find the recommendation index in the current recommendations list
        // For simplicity, we'll just use 0 as the index here
        const recommendationIndex = 0;
        
        // Call the API to apply the recommendation
        const response = await axios.post(
          `${API_PATH}/api/auto-tuner/recommendations/apply`,
          { recommendation_id: recommendationIndex }
        );
        
        console.log('Applied recommendation:', response.data);
        setActionResult(response.data);
        
        // Create a new alert for the applied tuning action
        if (response.data.success) {
          const tuningAction = {
            parameter: recommendationData.parameter,
            old_value: recommendationData.current_value,
            new_value: recommendationData.recommended_value,
            reason: recommendationData.reason
          };
          
          alertUtils.createAlertFromTuningAction(tuningAction, true);
        } else {
          const tuningAction = {
            parameter: recommendationData.parameter,
            old_value: recommendationData.current_value,
            new_value: recommendationData.recommended_value,
            reason: 'Failed to apply recommendation'
          };
          
          alertUtils.createAlertFromTuningAction(tuningAction, false);
        }
        
        // Mark the recommendation alert as read
        dispatch(markAlertAsRead(currentActionableAlert.id));
        
        // Close the action modal
        setIsActionModalOpen(false);
        
      } catch (error) {
        console.error('Error applying recommendation:', error);
        setActionResult({ success: false, error: 'Failed to apply recommendation' });
      }
    };
    
    // Generate real system alerts based on auto-tuner and metrics
    const generateRealSystemAlerts = async () => {
      try {
        // Get current metrics
        const metricsResponse = await axios.get(`${API_PATH}/api/auto-tuner/metrics/current`);
        const metrics = metricsResponse.data;
        
        // Check for threshold violations and create alerts
        if (metrics.cpu_usage > 70) {
          alertUtils.createAlertFromMetricThreshold('cpu_usage', metrics.cpu_usage, 70);
        }
        
        if (metrics.memory_usage > 80) {
          alertUtils.createAlertFromMetricThreshold('memory_usage', metrics.memory_usage, 80);
        }
        
        // Get auto-tuner recommendations
        const recommendationsResponse = await axios.get(`${API_PATH}/api/auto-tuner/recommendations`);
        const recommendations = recommendationsResponse.data;
        
        // Create alerts for the top recommendations
        if (recommendations && recommendations.length > 0) {
          alertUtils.createAlertFromRecommendation(recommendations[0]);
        }
        
        // Get system patterns
        const patternsResponse = await axios.get(`${API_PATH}/api/auto-tuner/patterns`);
        const patterns = patternsResponse.data;
        
        // Create alerts for detected patterns
        if (patterns && patterns.detected_patterns && patterns.detected_patterns.length > 0) {
          alertUtils.createAlertFromPattern(patterns.detected_patterns[0]);
        }
        
      } catch (error) {
        console.error('Error generating real system alerts:', error);
      }
    };
    
    const handleMarkAllAsRead = () => {
      if (window.confirm("The Quantum Shadow People ask: Are you sure you want to mark all alerts as read?")) {
        dispatch(markAllAlertsAsRead())
          .then(result => {
            console.log('All alerts marked as read:', result);
            setShadowQuote("The Quantum Shadow People have acknowledged all your alerts.");
          })
          .catch(error => {
            console.error('Error marking all alerts as read:', error);
          });
      }
    };
    
    // New functions for bulk operations and action status management
    const handleToggleSelection = (id: string, e: React.MouseEvent) => {
      e.stopPropagation();
      dispatch(toggleAlertSelection(id));
    };
  
    const handleSelectAll = () => {
      dispatch(selectAllAlerts());
    };
  
    const handleDeselectAll = () => {
      dispatch(deselectAllAlerts());
    };
  
    const handleDeleteSelected = () => {
      if (window.confirm(`The Quantum Shadow People ask: Are you sure you want to delete ${selectedCount} selected alerts? This information will be lost to the void between dimensions.`)) {
        dispatch(deleteSelectedAlerts());
        setShadowQuote("The Quantum Shadow People have banished the selected alerts to the void.");
      }
    };
  
    const handleUpdateActionStatus = (status: 'none' | 'actioned' | 'not_actioned' | 'to_action_later') => {
      dispatch(updateSelectedAlertsActionStatus(status));
      setShowActionMenu(false);
      setShadowQuote(`The Quantum Shadow People have updated the status of the selected alerts to ${status.replace('_', ' ')}.`);
    };
  
    const handleMarkSelectedAsRead = () => {
      dispatch(markSelectedAlertsAsRead());
      setShadowQuote("The Quantum Shadow People have acknowledged the selected alerts.");
    };
  
    const handleAlertClick = (id: string) => {
      if (expandedAlertId === id) {
        setExpandedAlertId(null);
      } else {
        setExpandedAlertId(id);
      }
    };
    
    // Filter functions
    const handleFilterChange = (filterType: string, value: string) => {
      setFilterOptions({
        ...filterOptions,
        [filterType]: value
      });
    };
  
    const getFilteredAlerts = () => {
      if (!alerts) return [];
      
      return alerts.filter((alert: any) => {
        // Filter by severity
        if (filterOptions.severity !== 'ALL' && alert.severity !== filterOptions.severity) {
          return false;
        }
        
        // Filter by read status
        if (filterOptions.read_status === 'READ' && !alert.is_read) {
          return false;
        }
        if (filterOptions.read_status === 'UNREAD' && alert.is_read) {
          return false;
        }
        
        // Filter by action status
        if (filterOptions.action_status !== 'ALL' && 
            alert.action_status !== filterOptions.action_status && 
            !(filterOptions.action_status === 'NONE' && !alert.action_status)) {
          return false;
        }
        
        // Filter by date
        if (filterOptions.date_range !== 'ALL') {
          const alertDate = new Date(alert.timestamp);
          const now = new Date();
          
          if (filterOptions.date_range === 'TODAY') {
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            if (alertDate < today) return false;
          } else if (filterOptions.date_range === 'YESTERDAY') {
            const yesterday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
            const dayBefore = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 2);
            if (alertDate < dayBefore || alertDate >= yesterday) return false;
          } else if (filterOptions.date_range === 'THIS_WEEK') {
            const startOfWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate() - now.getDay());
            if (alertDate < startOfWeek) return false;
          } else if (filterOptions.date_range === 'THIS_MONTH') {
            const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
            if (alertDate < startOfMonth) return false;
          }
        }
        
        return true;
      });
    };
    const getActionStatusLabel = (status?: string) => {
      switch (status) {
        case 'actioned':
          return 'Actioned';
        case 'not_actioned':
          return 'Not Actioned';
        case 'to_action_later':
          return 'To Action Later';
        default:
          return 'No Status';
      }
    };
  
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString();
    };
  
    const getSeverityClass = (severity: string) => {
      switch (severity.toUpperCase()) {
        case 'CRITICAL':
          return 'critical';
        case 'HIGH':
          return 'high';
        case 'MEDIUM':
          return 'medium';
        case 'LOW':
          return 'low';
        default:
          return '';
      }
    };
  
    // Test API connection for debugging
    const testApiConnection = async () => {
      try {
        const response = await axios.get(`${API_PATH}/api/health-check`);
        setDebugInfo(`API connection successful: ${JSON.stringify(response.data)}`);
      } catch (error: any) {
        setDebugInfo(`API connection failed: ${error.message}`);
      }
    };
  
    // Login with test credentials for debugging
    const loginForFreshToken = async () => {
      try {
        const response = await axios.post(`${API_PATH}/api/auth/login`, {
          username: 'testuser',
          password: 'testpassword'
        });
        if (response.data.access_token) {
          localStorage.setItem('token', response.data.access_token);
          setDebugInfo('Login successful, new token acquired');
          return true;
        }
        return false;
      } catch (error: any) {
        setDebugInfo(`Login failed: ${error.message}`);
        return false;
      }
    };
  
    const openCreateModal = () => {
      setFormData(defaultFormData);
      setIsModalOpen(true);
    };
  
    if (loading) {
      return <div className="loading-container">The Quantum Shadow People are gathering alerts from the void...</div>;
    }
  
    if (error) {
      return (
        <div className="error-container">
          <h3>The Quantum Shadow People have encountered an interdimensional error!</h3>
          <p>{error}</p>
          <div className="error-details">
            <p>Possible causes:</p>
            <ul>
              <li>Authentication token may be missing or invalid</li>
              <li>Backend server may be unreachable</li>
              <li>API endpoint configuration may be incorrect</li>
            </ul>
          </div>
          
          <div className="debug-info">
            <p>Debug Info:</p>
            <p>Token exists: {localStorage.getItem('token') ? 'Yes' : 'No'}</p>
            <p>Backend URL: {API_PATH}</p>
            <p>API Path: {API_PATH}</p>
            <p>Full Alerts Endpoint: {`${API_PATH}`}</p>
            <p>Redux API Call Path: {`/api${API_PATH}`}</p>
            <p>{debugInfo}</p>
            <Button variant="cyber" size="sm" onClick={testApiConnection}>Test API Connection</Button>
          </div>
          <div className="error-actions">
            <Button 
              variant="primary"
              onClick={() => dispatch(fetchSystemAlerts({ skip: 0, limit: 20, is_read: undefined }))}
            >
              Recalibrate the quantum field and try again
            </Button>
            <Button 
              variant="accent"
              onClick={async () => {
                const success = await loginForFreshToken();
                if (success) dispatch(fetchSystemAlerts({ skip: 0, limit: 20, is_read: undefined }));
              }}
            >
              Login with test credentials
            </Button>
            <Button 
              variant="secondary"
              onClick={() => navigate('/login')}
            >
              Return to login portal
            </Button>
          </div>
        </div>
      );
    }
  
    return (
      <div className="system-alerts-container">
        <div className="alerts-header">
          <div className="alerts-header-top">
            <h2>System Alerts</h2>
            <div className="quantum-shadow-icon">
            </div>
          </div>
          <div className="shadow-quote">{shadowQuote}</div>
          <div className="alert-actions-container">
            <Button 
              variant="accent" 
              onClick={openCreateModal}
              leftIcon="⚠️"
              glow
            >
              Create New Alert
            </Button>
            {alerts && alerts.length > 0 && alerts.some((alert: any) => !alert.is_read) && (
              <Button 
                variant="primary" 
                onClick={handleMarkAllAsRead}
                leftIcon="✓"
                glow
              >
                Mark All as Read
              </Button>
            )}
          </div>
        </div>
  
        {/* Alert statistics */}
        <div className="alert-statistics">
          <div className="stat-card">
            <div className="stat-title">Total Alerts</div>
            <div className="stat-value">{alerts?.length || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-title">Unread</div>
            <div className="stat-value">{alerts?.filter((alert: any) => !alert.is_read).length || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-title">Critical</div>
            <div className="stat-value">{alerts?.filter((alert: any) => alert.severity === 'CRITICAL').length || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-title">Actionable</div>
            <div className="stat-value">{alerts?.filter((alert: any) => alert.additional_data && alert.additional_data.actionable).length || 0}</div>
          </div>
        </div>
  
        {/* Filter bar */}
        <div className="filter-bar">
          <div className="filter-group">
            <label>Severity:</label>
            <select 
              value={filterOptions.severity}
              onChange={(e) => handleFilterChange('severity', e.target.value)}
            >
              <option value="ALL">All</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Status:</label>
            <select 
              value={filterOptions.read_status}
              onChange={(e) => handleFilterChange('read_status', e.target.value)}
            >
              <option value="ALL">All</option>
              <option value="READ">Read</option>
              <option value="UNREAD">Unread</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Action Status:</label>
            <select 
              value={filterOptions.action_status}
              onChange={(e) => handleFilterChange('action_status', e.target.value)}
            >
              <option value="ALL">All</option>
              <option value="NONE">No Status</option>
              <option value="actioned">Actioned</option>
              <option value="not_actioned">Not Actioned</option>
              <option value="to_action_later">Action Later</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Date:</label>
            <select 
              value={filterOptions.date_range}
              onChange={(e) => handleFilterChange('date_range', e.target.value)}
            >
              <option value="ALL">All Time</option>
              <option value="TODAY">Today</option>
              <option value="YESTERDAY">Yesterday</option>
              <option value="THIS_WEEK">This Week</option>
              <option value="THIS_MONTH">This Month</option>
            </select>
          </div>
          <Button 
            variant="secondary" 
            size="sm"
            onClick={() => setFilterOptions({
              severity: 'ALL',
              read_status: 'ALL',
              action_status: 'ALL',
              date_range: 'ALL'
            })}
            leftIcon="🔄"
          >
            Reset Filters
          </Button>
        </div>
  
        {/* Bulk actions section */}
        {selectedCount > 0 && (
          <div className="bulk-actions">
            <span className="selected-count">{selectedCount} selected</span>
            <div className="bulk-action-buttons">
              <Button 
                variant="primary" 
                size="sm"
                onClick={handleMarkSelectedAsRead}
                leftIcon="✓"
              >
                Mark Selected as Read
              </Button>
              <Button 
                variant="danger" 
                size="sm"
                onClick={handleDeleteSelected}
                leftIcon="🗑️"
              >
                Delete Selected
              </Button>
              <div className="action-status-dropdown">
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={() => setShowActionMenu(!showActionMenu)}
                  leftIcon="🔄"
                >
                  Set Status
                </Button>
                {showActionMenu && (
                  <div className="action-status-menu">
                    <Button variant="success" size="sm" onClick={() => handleUpdateActionStatus('actioned')} fullWidth>Actioned</Button>
                    <Button variant="danger" size="sm" onClick={() => handleUpdateActionStatus('not_actioned')} fullWidth>Not Actioned</Button>
                    <Button variant="warning" size="sm" onClick={() => handleUpdateActionStatus('to_action_later')} fullWidth>Action Later</Button>
                    <Button variant="secondary" size="sm" onClick={() => handleUpdateActionStatus('none')} fullWidth>No Status</Button>
                  </div>
                )}
              </div>
              <Button 
                variant="secondary" 
                size="sm"
                onClick={handleDeselectAll}
                leftIcon="✕"
              >
                Deselect All
              </Button>
            </div>
          </div>
        )}
        
        <div className="alerts-list">
          {getFilteredAlerts().length > 0 ? (
            getFilteredAlerts().map((alert, index) => (
              <div 
                key={`${alert.id}-${index}`} 
                className={`alert-card ${!alert.is_read ? 'unread' : 'read'} ${alert.selected ? 'selected' : ''} ${expandedAlertId === alert.id ? 'expanded' : ''}`}
                onClick={() => handleAlertClick(alert.id)}
              >
                <div className="alert-selection">
                  <input 
                    type="checkbox" 
                    checked={alert.selected || false}
                    onChange={(e) => handleToggleSelection(alert.id, e.nativeEvent as unknown as React.MouseEvent)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
                
                <div className="alert-content">
                  <div className="alert-header">
                    <div className={`severity-indicator ${getSeverityClass(alert.severity)}`}>
                      {alert.severity}
                    </div>
                    <h3>{alert.title}</h3>
                    {!alert.is_read && <span className="unread-badge">NEW</span>}
                    {alert.action_status && (
                      <span className={`action-status-badge ${alert.action_status}`}>
                        {getActionStatusLabel(alert.action_status)}
                      </span>
                    )}
                  </div>
                  
                  <div className="alert-timestamp">
                    {formatDate(alert.timestamp)}
                  </div>
                  
                  <p className="alert-message">{alert.message}</p>
                  
                  {expandedAlertId === alert.id && (
                    <div className="action-status-selector">
                      <span>Status:</span>
                      <select 
                        value={alert.action_status || 'none'}
                        onChange={(e) => {
                          dispatch(updateAlertActionStatus({
                            id: alert.id, 
                            status: e.target.value as 'none' | 'actioned' | 'not_actioned' | 'to_action_later'
                          }));
                          e.stopPropagation();
                        }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <option value="none">No Status</option>
                        <option value="actioned">Actioned</option>
                        <option value="not_actioned">Not Actioned</option>
                        <option value="to_action_later">Action Later</option>
                      </select>
                    </div>
                  )}
                </div>
                
                <div className="alert-actions">
                  {!alert.is_read && (
                    <Button 
                      variant="primary" 
                      size="sm"
                      circle
                      onClick={(e) => handleMarkAsRead(alert.id, e)}
                      title="Mark as Read"
                    >
                      ✓
                    </Button>
                  )}
                  {alert.additional_data && alert.additional_data.actionable && (
                    <Button 
                      variant="cyber" 
                      size="sm"
                      circle
                      onClick={(e) => { e.stopPropagation(); handleAlertAction(alert); }}
                      title={alert.additional_data.action_type === 'apply_recommendation' ? 'Apply' : 'View'}
                    >
                      ⚡
                    </Button>
                  )}
                  {alert.additional_data && alert.additional_data.pattern_data && (
                    <Button 
                      variant="warning" 
                      size="sm"
                      circle
                      onClick={(e) => { e.stopPropagation(); handlePatternVisualization(alert); }}
                      title="View Pattern"
                    >
                      📊
                    </Button>
                  )}
                  <Button 
                    variant="danger" 
                    size="sm"
                    circle
                    onClick={(e) => handleDelete(alert.id, e)}
                    title="Delete"
                  >
                    ×
                  </Button>
                </div>
              </div>
            ))
          ) : (
            <div className="no-alerts">
              <p>No alerts match your current filters.</p>
              <p>Try adjusting your filter criteria or check back later.</p>
            </div>
          )}
        </div>
        
        <div className="alerts-footer">
          <Button 
            variant="primary" 
            size="sm" 
            onClick={handleSelectAll}
          >
            Select All
          </Button>
        </div>
  
        {/* Create Alert Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Create System Alert"
          size="medium"
        >
          <div className="alert-form">
            <div className="modal-intro">
              <div className="modal-icon">
              </div>
              <p className="modal-description">
                The Quantum Shadow People will broadcast this alert across all dimensions. Choose your words wisely.
              </p>
            </div>
  
            <div className="form-group">
              <label htmlFor="title">Alert Title:</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="Enter alert title..."
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="message">Alert Message:</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleInputChange}
                placeholder="Describe the alert details..."
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="severity">Severity Level:</label>
              <div className="severity-selector">
                <select
                  id="severity"
                  name="severity"
                  value={formData.severity}
                  onChange={handleInputChange}
                >
                  <option value="LOW">Low - Informational only</option>
                  <option value="MEDIUM">Medium - Requires attention</option>
                  <option value="HIGH">High - Urgent action needed</option>
                  <option value="CRITICAL">Critical - System at risk</option>
                </select>
                <div className={`severity-preview ${getSeverityClass(formData.severity)}`}>
                  {formData.severity}
                </div>
              </div>
            </div>
            
            <div className="form-actions">
              <Button 
                variant="secondary" 
                onClick={() => setIsModalOpen(false)}
                leftIcon="✕"
              >
                Cancel
              </Button>
              <Button 
                variant="accent" 
                onClick={handleSubmit}
                disabled={!formData.title || !formData.message}
                leftIcon="⚠️"
                glow
              >
                Create Alert
              </Button>
            </div>
          </div>
        </Modal>
        
        {/* Action Modal for Recommendations */}
        <Modal
          isOpen={isActionModalOpen}
          onClose={() => setIsActionModalOpen(false)}
          title="Apply System Recommendation"
          size="medium"
        >
          {currentActionableAlert && (
            <div className="action-modal-content">
              <div className="modal-intro">
                <div className="modal-icon">
                </div>
                <p className="modal-description">
                  The Quantum Shadow People will apply this system optimization. Proceed with caution.
                </p>
              </div>
              
              <div className="recommendation-details">
                <h3>{currentActionableAlert.title}</h3>
                <p>{currentActionableAlert.message}</p>
                
                {currentActionableAlert.additional_data && (
                  <div className="recommendation-params">
                    <div className="param-item">
                      <span className="param-label">Parameter:</span>
                      <span className="param-value">{currentActionableAlert.additional_data.parameter}</span>
                    </div>
                    
                    <div className="param-item">
                      <span className="param-label">Current Value:</span>
                      <span className="param-value">{currentActionableAlert.additional_data.current_value}</span>
                    </div>
                    
                    <div className="param-item">
                      <span className="param-label">Recommended Value:</span>
                      <span className="param-value">{currentActionableAlert.additional_data.recommended_value}</span>
                    </div>
                    
                    <div className="param-item">
                      <span className="param-label">Confidence:</span>
                      <span className="param-value">
                        {(currentActionableAlert.additional_data.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                )}
                
                {actionResult && (
                  <div className={`action-result ${actionResult.success ? 'success' : 'error'}`}>
                    <h4>{actionResult.success ? 'Success!' : 'Failed!'}</h4>
                    <p>{actionResult.success 
                      ? 'The recommendation was successfully applied.' 
                      : `Error: ${actionResult.error || 'Unknown error'}`}</p>
                  </div>
                )}
              </div>
              
              <div className="form-actions">
                <Button 
                  variant="secondary" 
                  onClick={() => setIsActionModalOpen(false)}
                  leftIcon="✕"
                >
                  Cancel
                </Button>
                <Button 
                  variant="cyber" 
                  onClick={applyRecommendation}
                  disabled={!!actionResult}
                  leftIcon="⚡"
                  glow
                >
                  Apply Recommendation
                </Button>
              </div>
            </div>
          )}
        </Modal>
  
        {/* Pattern Visualization Modal */}
        <Modal
          isOpen={isPatternModalOpen}
          onClose={() => setIsPatternModalOpen(false)}
          title="System Pattern Analysis"
          size="large"
        >
          {currentPatternAlert && (
            <div className="pattern-modal-content">
              <div className="modal-intro">
                <div className="modal-icon">
                </div>
                <p className="modal-description">
                  The Quantum Shadow People have detected recurring patterns in your system behavior.
                </p>
              </div>
              
              <div className="pattern-details">
              <h3>{currentPatternAlert.title}</h3>
              <p>{currentPatternAlert.message}</p>
              
              {currentPatternAlert.additional_data && currentPatternAlert.additional_data.pattern_data && (
                <div className="pattern-visualization">
                  <h4>Pattern Visualization</h4>
                  <div className="graph-container">
                    {/* Simplified graph representation */}
                    <div className="graph-y-axis">
                      <span>100%</span>
                      <span>75%</span>
                      <span>50%</span>
                      <span>25%</span>
                      <span>0%</span>
                    </div>
                    <div className="graph-content">
                      {currentPatternAlert.additional_data.pattern_data.points && 
                        currentPatternAlert.additional_data.pattern_data.points.map((point: number, index: number) => (
                          <div 
                            key={index} 
                            className="graph-bar" 
                            style={{ height: `${point}%` }}
                            title={`Value: ${point}%`}
                          />
                        ))
                      }
                    </div>
                    <div className="graph-x-axis">
                      <span>Time</span>
                    </div>
                  </div>
                  
                  <div className="pattern-stats">
                    <div className="stat-item">
                      <span className="stat-label">Confidence:</span>
                      <span className="stat-value">
                        {(currentPatternAlert.additional_data.pattern_data.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Periodicity:</span>
                      <span className="stat-value">
                        {currentPatternAlert.additional_data.pattern_data.periodicity} minutes
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">First Detected:</span>
                      <span className="stat-value">
                        {formatDate(currentPatternAlert.additional_data.pattern_data.first_detected)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div className="form-actions">
              <Button 
                variant="secondary" 
                onClick={() => setIsPatternModalOpen(false)}
                leftIcon="✕"
              >
                Close
              </Button>
              <Button 
                variant="cyber" 
                onClick={() => {
                  navigate('/metrics');
                  setIsPatternModalOpen(false);
                }}
                leftIcon="📊"
                glow
              >
                View Full Metrics
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default SystemAlerts;