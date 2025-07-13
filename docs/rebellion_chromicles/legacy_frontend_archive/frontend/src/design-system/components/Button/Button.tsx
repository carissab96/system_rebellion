import React from 'react';
import './Button.css';

export type ButtonVariant = 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'danger' | 'cyber';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button variant that determines color scheme */
  variant?: ButtonVariant;
  /** Button size */
  size?: ButtonSize;
  /** Whether the button is outlined (transparent with border) */
  outlined?: boolean;
  /** Whether the button is a circle (equal width and height) */
  circle?: boolean;
  /** Whether the button has a glow effect */
  glow?: boolean;
  /** Whether the button is full width */
  fullWidth?: boolean;
  /** Icon to display before button text */
  leftIcon?: React.ReactNode;
  /** Icon to display after button text */
  rightIcon?: React.ReactNode;
  /** Whether the button is in loading state */
  loading?: boolean;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Additional CSS class names */
  className?: string;
}

/**
 * Button component for System Rebellion UI
 * 
 * A customizable button component that follows the System Rebellion design system.
 * Supports various variants, sizes, and states.
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  outlined = false,
  circle = false,
  glow = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  loading = false,
  disabled = false,
  className = '',
  children,
  ...props
}) => {
  // Build the class names based on props
  const buttonClasses = [
    'sr-button',
    `sr-button-${variant}`,
    `sr-button-${size}`,
    outlined ? 'sr-button-outlined' : '',
    circle ? 'sr-button-circle' : '',
    glow ? 'sr-button-glow' : '',
    fullWidth ? 'sr-button-full-width' : '',
    loading ? 'sr-button-loading' : '',
    disabled ? 'sr-button-disabled' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <button 
      className={buttonClasses} 
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className="sr-button-spinner" />}
      {leftIcon && <span className="sr-button-icon sr-button-icon-left">{leftIcon}</span>}
      {children && <span className="sr-button-text">{children}</span>}
      {rightIcon && <span className="sr-button-icon sr-button-icon-right">{rightIcon}</span>}
    </button>
  );
};

export default Button;
