import React, { forwardRef } from 'react';
import './Input.css';

export type InputVariant = 'primary' | 'secondary' | 'accent' | 'cyber';
export type InputSize = 'sm' | 'md' | 'lg';
export type InputType = 'text' | 'password' | 'email' | 'number' | 'search' | 'tel' | 'url';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Input variant that determines color scheme */
  variant?: InputVariant;
  /** Input size */
  size?: InputSize;
  /** Whether the input has a glow effect */
  glow?: boolean;
  /** Whether the input has a glass effect */
  glass?: boolean;
  /** Whether the input has a cyber-style border */
  cyberBorder?: boolean;
  /** Label for the input */
  label?: React.ReactNode;
  /** Helper text displayed below the input */
  helperText?: React.ReactNode;
  /** Error message displayed below the input */
  error?: React.ReactNode;
  /** Icon displayed at the start of the input */
  startIcon?: React.ReactNode;
  /** Icon displayed at the end of the input */
  endIcon?: React.ReactNode;
  /** Additional CSS class names */
  className?: string;
  /** Input type */
  type?: InputType;
  /** Whether the input is full width */
  fullWidth?: boolean;
}

/**
 * Input component for System Rebellion UI
 * 
 * A customizable input component that follows the System Rebellion design system.
 * Supports various variants, sizes, and styles with cyberpunk aesthetics.
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(({
  variant = 'primary',
  size = 'md',
  glow = false,
  glass = false,
  cyberBorder = false,
  label,
  helperText,
  error,
  startIcon,
  endIcon,
  className = '',
  type = 'text',
  fullWidth = false,
  disabled = false,
  id,
  ...props
}, ref) => {
  // Generate a unique ID if none is provided
  const inputId = id || `sr-input-${Math.random().toString(36).substring(2, 9)}`;
  
  // Build the class names based on props
  const inputWrapperClasses = [
    'sr-input-wrapper',
    `sr-input-${variant}`,
    `sr-input-${size}`,
    glow ? 'sr-input-glow' : '',
    glass ? 'sr-input-glass' : '',
    cyberBorder ? 'sr-input-cyber-border' : '',
    fullWidth ? 'sr-input-full-width' : '',
    disabled ? 'sr-input-disabled' : '',
    error ? 'sr-input-error' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={inputWrapperClasses}>
      {label && (
        <label htmlFor={inputId} className="sr-input-label">
          {label}
        </label>
      )}
      
      <div className="sr-input-container">
        {startIcon && (
          <div className="sr-input-icon sr-input-start-icon">
            {startIcon}
          </div>
        )}
        
        <input
          ref={ref}
          id={inputId}
          type={type}
          disabled={disabled}
          className={`sr-input ${startIcon ? 'sr-input-has-start-icon' : ''} ${endIcon ? 'sr-input-has-end-icon' : ''}`}
          {...props}
        />
        
        {endIcon && (
          <div className="sr-input-icon sr-input-end-icon">
            {endIcon}
          </div>
        )}
      </div>
      
      {(helperText || error) && (
        <div className={`sr-input-helper-text ${error ? 'sr-input-helper-text-error' : ''}`}>
          {error || helperText}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
