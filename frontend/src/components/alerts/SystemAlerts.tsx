import React, { useState, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import './SystemAlerts.css';
import { 
  fetchSystemAlerts, 
  markAlertAsRead,
  deleteSystemAlert,
  createSystemAlert
} from '../../store/slices/alertsSlice';
import Modal from '../common/Modal';
import { QuantumShadowPerson } from '../common/CharacterIcons';

interface SystemAlertFormData {
  title: string;
  message: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

const defaultFormData: SystemAlertFormData = {
  title: '',
  message: '',
  severity: 'MEDIUM'
};

export const SystemAlerts: React.FC = () => {
  const dispatch = useAppDispatch();
  const { alerts, loading, error } = useAppSelector((state) => state.alerts);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState<SystemAlertFormData>(defaultFormData);
  const [shadowQuote, setShadowQuote] = useState<string>('');

  const shadowQuotes = [
    "The Quantum Shadow People are monitoring your router configurations...",
    "We've detected unusual activity in the quantum realm. Your router may be at risk.",
    "The shadows between dimensions suggest your system needs attention.",
    "We exist in the spaces between your packets. Your network traffic reveals all.",
    "Your router's quantum state is unstable. We recommend immediate reconfiguration."
  ];

  useEffect(() => {
    dispatch(fetchSystemAlerts());
    setShadowQuote(shadowQuotes[Math.floor(Math.random() * shadowQuotes.length)]);
  }, [dispatch]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = () => {
    dispatch(createSystemAlert(formData));
    setIsModalOpen(false);
    setFormData(defaultFormData);
    setShadowQuote(shadowQuotes[Math.floor(Math.random() * shadowQuotes.length)]);
  };

  const handleMarkAsRead = (id: string) => {
    dispatch(markAlertAsRead(id));
  };

  const handleDelete = (id: string) => {
    if (window.confirm("The Quantum Shadow People ask: Are you sure you want to delete this alert? This information will be lost to the void between dimensions.")) {
      dispatch(deleteSystemAlert(id));
      setShadowQuote("The Quantum Shadow People have banished that alert to the void.");
    }
  };

  const openCreateModal = () => {
    setFormData(defaultFormData);
    setIsModalOpen(true);
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'LOW': return 'severity-low';
      case 'MEDIUM': return 'severity-medium';
      case 'HIGH': return 'severity-high';
      case 'CRITICAL': return 'severity-critical';
      default: return '';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return <div className="loading-container">The Quantum Shadow People are gathering alerts from the void...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <h3>The Quantum Shadow People have encountered an interdimensional error!</h3>
        <p>{error}</p>
        <button onClick={() => dispatch(fetchSystemAlerts())}>
          Recalibrate the quantum field and try again
        </button>
      </div>
    );
  }

  return (
    <div className="system-alerts-container">
      <div className="alerts-header">
        <h2>System Alerts</h2>
        <div className="shadow-quote">{shadowQuote}</div>
        <div className="quantum-shadow-icon">
          <QuantumShadowPerson className="shadow-icon" />
        </div>
        <button className="create-alert-button" onClick={openCreateModal}>
          <span className="button-icon">⚠️</span>
          <span>Create New Alert</span>
        </button>
      </div>

      <div className="alerts-list">
        {alerts && alerts.length > 0 ? (
          alerts.map((alert: any) => (
            <div key={alert.id} className={`alert-card ${alert.is_read ? 'read' : 'unread'}`}>
              <div className="alert-header">
                <div className={`severity-indicator ${getSeverityClass(alert.severity)}`}>
                  {alert.severity}
                </div>
                <h3>{alert.title}</h3>
                {!alert.is_read && <span className="unread-badge">NEW</span>}
              </div>
              
              <div className="alert-timestamp">
                {formatDate(alert.timestamp)}
              </div>
              
              <p className="alert-message">{alert.message}</p>
              
              <div className="alert-actions">
                {!alert.is_read && (
                  <button className="mark-read-button" onClick={() => handleMarkAsRead(alert.id)}>
                    Mark as Read
                  </button>
                )}
                <button className="delete-button" onClick={() => handleDelete(alert.id)}>
                  Delete
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

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create System Alert"
        size="medium"
      >
        <div className="alert-form">
          <div className="form-group">
            <label htmlFor="title">Alert Title:</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="Enter alert title..."
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
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="severity">Severity Level:</label>
            <select
              id="severity"
              name="severity"
              value={formData.severity}
              onChange={handleInputChange}
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>
          
          <div className="form-actions">
            <button className="cancel-button" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button className="submit-button" onClick={handleSubmit}>
              Create Alert
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default SystemAlerts;
