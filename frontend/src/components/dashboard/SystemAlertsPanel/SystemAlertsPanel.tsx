import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { useNavigate } from 'react-router-dom';
import { 
  fetchSystemAlerts, 
  markAlertAsRead, 
  deleteSystemAlert,
  updateAlertActionStatus,
  toggleAlertSelection,
  selectAllAlerts,
  deselectAllAlerts,
  deleteSelectedAlerts,
  updateSelectedAlertsActionStatus,
  markSelectedAlertsAsRead
} from '../../../store/slices/systemAlertsSlice';
import { QuantumShadowPerson } from '../../common/CharacterIcons';
import { Button } from '../../../design-system/components';
import './SystemAlertsPanel.css';

interface SystemAlertsPanelProps {
  maxAlerts?: number;
  showAllLink?: boolean;
  onNavigateToAlerts?: () => void;
}

export const SystemAlertsPanel: React.FC<SystemAlertsPanelProps> = ({
  maxAlerts = 5,
  showAllLink = true,
  onNavigateToAlerts
}) => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { alerts, loading: alertsLoading, error: alertsError, selectedCount } = useAppSelector((state) => state.systemAlerts);
  
  const [expandedAlertId, setExpandedAlertId] = useState<string | null>(null);
  const [showActionMenu, setShowActionMenu] = useState(false);

  // Alert management functions
  const handleMarkAsRead = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    dispatch(markAlertAsRead(id));
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    dispatch(deleteSystemAlert(id));
  };

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
    if (window.confirm('Are you sure you want to delete all selected alerts? This shit can\'t be undone.')) {
      dispatch(deleteSelectedAlerts());
    }
  };

  const handleUpdateActionStatus = (status: 'none' | 'actioned' | 'not_actioned' | 'to_action_later') => {
    dispatch(updateSelectedAlertsActionStatus(status));
    setShowActionMenu(false);
  };

  const handleMarkSelectedAsRead = () => {
    dispatch(markSelectedAlertsAsRead());
  };

  const handleAlertClick = (id: string) => {
    if (expandedAlertId === id) {
      setExpandedAlertId(null);
    } else {
      setExpandedAlertId(id);
    }
  };

  const handleViewAllAlerts = () => {
    if (onNavigateToAlerts) {
      onNavigateToAlerts();
    } else {
      navigate('/alerts');
    }
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

  const getActionStatusLabel = (status?: string) => {
    switch (status) {
      case 'actioned':
        return 'Actioned';
      case 'not_actioned':
        return 'Not Actioned';
      case 'to_action_later':
        return 'Action Later';
      default:
        return 'No Status';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="system-alerts">
      <div className="alerts-card-header">
        <h2>System Alerts</h2>
        <div className="quantum-shadow-icon">
          <QuantumShadowPerson className="shadow-icon" />
        </div>
      </div>

      {alertsLoading ? (
        <div className="alerts-loading">Loading alerts...</div>
      ) : alertsError ? (
        <div className="alerts-error">{alertsError}</div>
      ) : (
        <>
          {selectedCount > 0 && (
            <div className="bulk-actions">
              <span className="selected-count">{selectedCount} selected</span>
              <div className="bulk-action-buttons">
                <Button 
                  variant="primary" 
                  size="sm" 
                  onClick={handleMarkSelectedAsRead}
                >
                  Mark Read
                </Button>
                <Button 
                  variant="danger" 
                  size="sm" 
                  onClick={handleDeleteSelected}
                >
                  Delete
                </Button>
                <div className="action-status-dropdown">
                  <Button 
                    variant="secondary" 
                    size="sm" 
                    onClick={() => setShowActionMenu(!showActionMenu)}
                  >
                    Set Status
                  </Button>
                  {showActionMenu && (
                    <div className="action-status-menu">
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        onClick={() => handleUpdateActionStatus('actioned')}
                      >
                        Actioned
                      </Button>
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        onClick={() => handleUpdateActionStatus('not_actioned')}
                      >
                        Not Actioned
                      </Button>
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        onClick={() => handleUpdateActionStatus('to_action_later')}
                      >
                        Action Later
                      </Button>
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        onClick={() => handleUpdateActionStatus('none')}
                      >
                        No Status
                      </Button>
                    </div>
                  )}
                </div>
                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={handleDeselectAll}
                >
                  Deselect All
                </Button>
              </div>
            </div>
          )}

          <div className="dashboard-alerts-list">
            {alerts.filter(alert => !alert.is_read).length === 0 ? (
              <div className="no-alerts">
                <p>No unread alerts to display</p>
              </div>
            ) : (
              alerts.filter(alert => !alert.is_read).slice(0, maxAlerts).map(alert => (
                <div 
                  key={alert.id} 
                  className={`dashboard-alert-card ${alert.is_read ? 'read' : 'unread'} ${alert.selected ? 'selected' : ''} ${expandedAlertId === alert.id ? 'expanded' : ''}`}
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
                    
                    {expandedAlertId === alert.id && (
                      <>
                        <div className="alert-timestamp">
                          {formatDate(alert.timestamp)}
                        </div>
                        
                        <p className="alert-message">{alert.message}</p>
                        
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
                      </>
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
            )}
          </div>

          <div className="alerts-card-footer">
            <Button 
              variant="primary" 
              size="sm" 
              onClick={handleSelectAll}
            >
              Select All
            </Button>
            {showAllLink && (
              <Button 
                variant="secondary" 
                size="sm" 
                onClick={handleViewAllAlerts}
              >
                View All Alerts
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default SystemAlertsPanel;
