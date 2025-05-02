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
import { QuantumShadowPerson } from '../common/CharacterIcons';
import alertUtils from '../../utils/alertUtils';

// Direct backend URL instead of using the relative API_BASE_URL
const BACKEND_URL = 'http://127.0.0.1:8000';
// API path should match what's used in alertsSlice.ts (without /api prefix)
const API_PATH = '/system-alerts';

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
  const [currentActionableAlert, setCurrentActionableAlert] = useState<any>(null);
  const [formData, setFormData] = useState<SystemAlertFormData>(defaultFormData);
  const [shadowQuote, setShadowQuote] = useState<string>('');
  const [debugInfo, setDebugInfo] = useState<string>('');
  const [actionResult, setActionResult] = useState<any>(null);
  const [showActionMenu, setShowActionMenu] = useState(false);
  const [expandedAlertId, setExpandedAlertId] = useState<string | null>(null);

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
        `${BACKEND_URL}/api/auto-tuner/recommendations/apply`,
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
      const metricsResponse = await axios.get(`${BACKEND_URL}/api/auto-tuner/metrics/current`);
      const metrics = metricsResponse.data;
      
      // Check for threshold violations and create alerts
      if (metrics.cpu_usage > 70) {
        alertUtils.createAlertFromMetricThreshold('cpu_usage', metrics.cpu_usage, 70);
      }
      
      if (metrics.memory_usage > 80) {
        alertUtils.createAlertFromMetricThreshold('memory_usage', metrics.memory_usage, 80);
      }
      
      // Get auto-tuner recommendations
      const recommendationsResponse = await axios.get(`${BACKEND_URL}/api/auto-tuner/recommendations`);
      const recommendations = recommendationsResponse.data;
      
      // Create alerts for the top recommendations
      if (recommendations && recommendations.length > 0) {
        alertUtils.createAlertFromRecommendation(recommendations[0]);
      }
      
      // Get system patterns
      const patternsResponse = await axios.get(`${BACKEND_URL}/api/auto-tuner/patterns`);
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
      const response = await axios.get(`${BACKEND_URL}/api/health-check`);
      setDebugInfo(`API connection successful: ${JSON.stringify(response.data)}`);
    } catch (error: any) {
      setDebugInfo(`API connection failed: ${error.message}`);
    }
  };

  // Login with test credentials for debugging
  const loginForFreshToken = async () => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
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
          <p>Backend URL: {BACKEND_URL}</p>
          <p>API Path: {API_PATH}</p>
          <p>Full Alerts Endpoint: {`${BACKEND_URL}/api${API_PATH}`}</p>
          <p>Redux API Call Path: {`/api${API_PATH}`}</p>
          <p>{debugInfo}</p>
          <button className="debug-button" onClick={testApiConnection}>Test API Connection</button>
        </div>
        <div className="error-actions">
          <button onClick={() => dispatch(fetchSystemAlerts({ skip: 0, limit: 20, is_read: undefined }))}>
            Recalibrate the quantum field and try again
          </button>
          <button onClick={async () => {
            const success = await loginForFreshToken();
            if (success) dispatch(fetchSystemAlerts({ skip: 0, limit: 20, is_read: undefined }));
          }}>
            Login with test credentials
          </button>
          <button onClick={() => navigate('/login')}>
            Return to login portal
          </button>
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
            <QuantumShadowPerson className="shadow-icon" />
          </div>
        </div>
        <div className="shadow-quote">{shadowQuote}</div>
        <div className="alert-actions-container">
          <button className="create-alert-button" onClick={openCreateModal}>
            <span className="button-icon">⚠️</span>
            <span>Create New Alert</span>
          </button>
          {alerts && alerts.length > 0 && alerts.some((alert: any) => !alert.is_read) && (
            <button className="mark-all-read-button" onClick={handleMarkAllAsRead}>
              <span className="button-icon">✓</span>
              <span>Mark All as Read</span>
            </button>
          )}
        </div>
      </div>

      {/* Bulk actions section */}
      {selectedCount > 0 && (
        <div className="bulk-actions">
          <span className="selected-count">{selectedCount} selected</span>
          <div className="bulk-action-buttons">
            <button className="bulk-action-button" onClick={handleMarkSelectedAsRead}>
              <span className="button-icon">✓</span>
              <span>Mark Read</span>
            </button>
            <button className="bulk-action-button" onClick={handleDeleteSelected}>
              <span className="button-icon">🗑️</span>
              <span>Delete</span>
            </button>
            <div className="action-status-dropdown">
              <button 
                className="bulk-action-button action-status-toggle" 
                onClick={() => setShowActionMenu(!showActionMenu)}
              >
                <span className="button-icon">🔄</span>
                <span>Set Status</span>
              </button>
              {showActionMenu && (
                <div className="action-status-menu">
                  <button onClick={() => handleUpdateActionStatus('actioned')}>
                    Actioned
                  </button>
                  <button onClick={() => handleUpdateActionStatus('not_actioned')}>
                    Not Actioned
                  </button>
                  <button onClick={() => handleUpdateActionStatus('to_action_later')}>
                    Action Later
                  </button>
                  <button onClick={() => handleUpdateActionStatus('none')}>
                    No Status
                  </button>
                </div>
              )}
            </div>
            <button className="bulk-action-button" onClick={handleDeselectAll}>
              <span className="button-icon">❌</span>
              <span>Deselect All</span>
            </button>
          </div>
        </div>
      )}
      
      <div className="alerts-list">
        {alerts.length > 0 ? (
          alerts.map(alert => (
            <div 
              key={alert.id} 
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
                  <button 
                    className="mark-read-button alert-action-button" 
                    onClick={(e) => handleMarkAsRead(alert.id, e)}
                    data-tooltip="Mark as Read"
                  >
                    ✓
                  </button>
                )}
                {alert.additional_data && alert.additional_data.actionable && (
                  <button 
                    className="action-button alert-action-button" 
                    onClick={(e) => { e.stopPropagation(); handleAlertAction(alert); }}
                    data-tooltip={alert.additional_data.action_type === 'apply_recommendation' ? 'Apply' : 'View'}
                  >
                    ⚡
                  </button>
                )}
                <button 
                  className="delete-button alert-action-button" 
                  onClick={(e) => handleDelete(alert.id, e)}
                  data-tooltip="Delete"
                >
                  ×
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="no-alerts">
            <p>The Quantum Shadow People haven't detected any alerts.</p>
            <p>Your system appears to be stable across all quantum dimensions... for now.</p>
          </div>
        )}
      </div>
      
      <div className="alerts-footer">
        <button className="select-all-button" onClick={handleSelectAll}>
          Select All
        </button>
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
              <QuantumShadowPerson className="shadow-icon-large" />
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
            <button className="cancel-button" onClick={() => setIsModalOpen(false)}>
              <span className="button-icon">✕</span>
              <span>Cancel</span>
            </button>
            <button 
              className="submit-button" 
              onClick={handleSubmit}
              disabled={!formData.title || !formData.message}
            >
              <span className="button-icon">⚠️</span>
              <span>Create Alert</span>
            </button>
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
                <QuantumShadowPerson className="shadow-icon-large" />
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
              <button className="cancel-button" onClick={() => setIsActionModalOpen(false)}>
                <span className="button-icon">✕</span>
                <span>Cancel</span>
              </button>
              <button 
                className="apply-button" 
                onClick={applyRecommendation}
                disabled={!!actionResult}
              >
                <span className="button-icon">⚡</span>
                <span>Apply Recommendation</span>
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default SystemAlerts;