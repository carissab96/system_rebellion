// alertUtils.ts
import store from '../store/store';
import { createSystemAlert } from '../store/slices/systemAlertsSlice';
// We'll use this for direct API calls when needed
import { API_BASE_URL } from './api';

// Direct backend URL for consistency with SystemAlerts component
const BACKEND_URL = 'http://127.0.0.1:8000';

/**
 * Utility to create system alerts from auto-tuner events or other system events
 */
export const createAlertFromEvent = (
  title: string,
  message: string,
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL',
  relatedMetrics?: any
) => {
  // Create the alert data
  const alertData = {
    title,
    message,
    severity,
    is_read: false, // Add the required is_read property
    additional_data: relatedMetrics || {}
  };

  // Dispatch the action to create the alert
  store.dispatch(createSystemAlert(alertData));
  
  // For debugging - log the API URL we would use for direct API calls
  console.log(`Alert created. API endpoint would be: ${BACKEND_URL}/api/system-alerts/ or ${API_BASE_URL}/system-alerts/`);
};

/**
 * Create an alert from an auto-tuner recommendation
 */
export const createAlertFromRecommendation = (recommendation: any) => {
  // Extract information from the recommendation
  const { parameter, current_value, recommended_value, confidence, impact_score, reason } = recommendation;
  
  // Determine severity based on confidence and impact
  let severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  const combinedScore = confidence * impact_score;
  
  if (combinedScore > 0.7) {
    severity = 'CRITICAL';
  } else if (combinedScore > 0.5) {
    severity = 'HIGH';
  } else if (combinedScore > 0.3) {
    severity = 'MEDIUM';
  } else {
    severity = 'LOW';
  }
  
  // Create a title and message
  const title = `Auto-Tuner Recommendation: ${parameter}`;
  const message = `${reason}. Current value: ${current_value}, Recommended value: ${recommended_value} (Confidence: ${(confidence * 100).toFixed(0)}%, Impact: ${(impact_score * 100).toFixed(0)}%)`;
  
  // Create the alert with additional data for applying the recommendation
  createAlertFromEvent(title, message, severity, { 
    parameter, 
    current_value, 
    recommended_value, 
    confidence, 
    impact_score,
    actionable: true,
    action_type: 'apply_recommendation',
    recommendation_data: recommendation
  });
};

/**
 * Create an alert from a system pattern detection
 */
export const createAlertFromPattern = (pattern: any) => {
  // Extract information from the pattern
  const { type, pattern: patternText, confidence, details } = pattern;
  
  // Determine severity based on confidence
  let severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  
  if (confidence > 0.8) {
    severity = 'CRITICAL';
  } else if (confidence > 0.6) {
    severity = 'HIGH';
  } else if (confidence > 0.4) {
    severity = 'MEDIUM';
  } else {
    severity = 'LOW';
  }
  
  // Create a title and message
  const title = `System Pattern Detected: ${type}`;
  const message = `${patternText}. (Confidence: ${(confidence * 100).toFixed(0)}%)`;
  
  // Create the alert with additional data
  createAlertFromEvent(title, message, severity, {
    ...details,
    pattern_type: type,
    confidence,
    actionable: details?.actionable || false,
    action_type: details?.action_type || null
  });
};

/**
 * Create an alert from a system metric threshold being exceeded
 */
export const createAlertFromMetricThreshold = (metric: string, value: number, threshold: number) => {
  // Determine severity based on how much the threshold is exceeded
  let severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  const exceedRatio = value / threshold;
  
  if (exceedRatio > 1.5) {
    severity = 'CRITICAL';
  } else if (exceedRatio > 1.3) {
    severity = 'HIGH';
  } else if (exceedRatio > 1.1) {
    severity = 'MEDIUM';
  } else {
    severity = 'LOW';
  }
  
  // Format the metric name for display
  const formattedMetric = metric
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
  
  // Create a title and message
  const title = `${formattedMetric} Threshold Exceeded`;
  const message = `${formattedMetric} has reached ${value.toFixed(1)}%, exceeding the threshold of ${threshold}%.`;
  
  // Create the alert
  createAlertFromEvent(title, message, severity, {
    metric,
    current_value: value,
    threshold,
    actionable: true,
    action_type: 'view_metrics'
  });
};

/**
 * Create an alert from a tuning action that was applied
 */
export const createAlertFromTuningAction = (tuningAction: any, success: boolean) => {
  const { parameter, old_value, new_value, reason } = tuningAction;
  
  // Determine severity based on success and parameter importance
  const severity = success ? 'MEDIUM' : 'HIGH';
  
  // Create a title and message
  const title = success 
    ? `System Tuning Applied: ${parameter}` 
    : `System Tuning Failed: ${parameter}`;
    
  const message = success
    ? `Successfully changed ${parameter} from ${old_value} to ${new_value}. ${reason || ''}`
    : `Failed to change ${parameter} from ${old_value} to ${new_value}. ${reason || ''}`;
  
  // Create the alert
  createAlertFromEvent(title, message, severity, {
    parameter,
    old_value,
    new_value,
    success,
    timestamp: new Date().toISOString(),
    actionable: false
  });
};

export default {
  createAlertFromEvent,
  createAlertFromRecommendation,
  createAlertFromPattern,
  createAlertFromMetricThreshold,
  createAlertFromTuningAction
};
