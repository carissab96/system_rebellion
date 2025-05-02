import React from 'react';
import './Toggle.css';

export type ToggleVariant = 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'danger' | 'cyber';
export type ToggleSize = 'sm' | 'md' | 'lg';

export interface ToggleProps {
  /** Whether the toggle is checked */
  checked: boolean;
  /** Function called when the toggle state changes */
  onChange: (checked: boolean) => void;
  /** Toggle variant that determines color scheme */
  variant?: ToggleVariant;
  /** Toggle size */
  size?: ToggleSize;
  /** Whether the toggle has a glow effect when active */
  glow?: boolean;
  /** Whether the toggle is disabled */
  disabled?: boolean;
  /** Label for the toggle */
  label?: React.ReactNode;
  /** Whether the label should appear on the right side */
  labelRight?: boolean;
  /** Additional CSS class names */
  className?: string;
  /** ID for the input element */
  id?: string;
  /** Name for the input element */
  name?: string;
  /** Additional props */
  [x: string]: any;
}

/**
 * Toggle component for System Rebellion UI
 * 
 * A customizable toggle switch component that follows the System Rebellion design system.
 * Supports various variants, sizes, and styles with cyberpunk aesthetics.
 */
export const Toggle: React.FC<ToggleProps> = ({
  checked,
  onChange,
  variant = 'primary',
  size = 'md',
  glow = false,
  disabled = false,
  label,
  labelRight = true,
  className = '',
  id,
  name,
  ...props
}) => {
  // Generate a unique ID if none is provided
  const toggleId = id || `sr-toggle-${Math.random().toString(36).substring(2, 9)}`;
  
  // Build the class names based on props
  const toggleClasses = [
    'sr-toggle',
    `sr-toggle-${variant}`,
    `sr-toggle-${size}`,
    glow ? 'sr-toggle-glow' : '',
    disabled ? 'sr-toggle-disabled' : '',
    className
  ].filter(Boolean).join(' ');

  // Handle the change event
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!disabled) {
      onChange(e.target.checked);
    }
  };

  return (
    <div className={toggleClasses}>
      {label && !labelRight && (
        <label htmlFor={toggleId} className="sr-toggle-label sr-toggle-label-left">
          {label}
        </label>
      )}
      
      <div className="sr-toggle-container">
        <input
          type="checkbox"
          id={toggleId}
          name={name}
          checked={checked}
          onChange={handleChange}
          disabled={disabled}
          className="sr-toggle-input"
          {...props}
        />
        <span className="sr-toggle-switch">
          <span className="sr-toggle-slider"></span>
        </span>
      </div>
      
      {label && labelRight && (
        <label htmlFor={toggleId} className="sr-toggle-label sr-toggle-label-right">
          {label}
        </label>
      )}
    </div>
  );
};

export default Toggle;
