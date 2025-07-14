import React from 'react';
import './Alert.css';


export type AlertVariant = 'info' | 'success' | 'warning' | 'danger' | 'cyber';
export type AlertSize = 'sm' | 'md' | 'lg';

export interface AlertProps {
  /** Alert variant that determines color scheme */
  variant?: AlertVariant;
  /** Alert size */
  size?: AlertSize;
  /** Alert title */
  title?: React.ReactNode;
  /** Whether the alert is dismissible */
  dismissible?: boolean;
  /** Function called when dismiss button is clicked */
  onDismiss?: () => void;
  /** Whether the alert has a glow effect */
  glow?: boolean;
  /** Whether the alert has an icon */
  hasIcon?: boolean;
  /** Custom icon to display */
  icon?: React.ReactNode;
  /** Whether the alert has a border */
  bordered?: boolean;
  /** Whether the alert is actionable */
  actionable?: boolean;
  /** Action button text */
  actionText?: string;
  /** Function called when action button is clicked */
  onAction?: () => void;
  /** Additional CSS class names */
  className?: string;
  /** Alert content */
  children: React.ReactNode;
}

/**
 * Alert component for System Rebellion UI
 * 
 * A customizable alert component that follows the System Rebellion design system.
 * Supports various variants, sizes, and states.
 */
export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  size = 'md',
  title,
  dismissible = false,
  onDismiss,
  glow = false,
  hasIcon = true,
  icon,
  bordered = false,
  actionable = false,
  actionText = 'Action',
  onAction,
  className = '',
  children,
}) => {
  // Default icons based on variant
  const getDefaultIcon = () => {
    switch (variant) {
      case 'info':
        return 'ℹ️';
      case 'success':
        return '✓';
      case 'warning':
        return '⚠️';
      case 'danger':
        return '⚠️';
      case 'cyber':
        return '⚡';
      default:
        return 'ℹ️';
    }
  };

  // Build the class names based on props
  const alertClasses = [
    'sr-alert',
    `sr-alert-${variant}`,
    `sr-alert-${size}`,
    glow ? 'sr-alert-glow' : '',
    bordered ? 'sr-alert-bordered' : '',
    actionable ? 'sr-alert-actionable' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={alertClasses} role="alert">
      {hasIcon && (
        <div className="sr-alert-icon">
          {icon || getDefaultIcon()}
        </div>
      )}
      <div className="sr-alert-content">
        {title && <div className="sr-alert-title">{title}</div>}
        <div className="sr-alert-message">{children}</div>
        {actionable && (
          <button className="sr-alert-action" onClick={onAction}>
            {actionText}
          </button>
        )}
      </div>
      {dismissible && (
        <button className="sr-alert-dismiss" onClick={onDismiss}>
          ×
        </button>
      )}
    </div>
  );
};

export default Alert;
