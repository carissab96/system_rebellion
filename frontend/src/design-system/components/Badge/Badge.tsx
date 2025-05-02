import React from 'react';
import './Badge.css';
import { colors, effects } from '../../tokens';

export type BadgeVariant = 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'danger' | 'cyber' | 'info';
export type BadgeSize = 'sm' | 'md' | 'lg';

export interface BadgeProps {
  /** Badge variant that determines color scheme */
  variant?: BadgeVariant;
  /** Badge size */
  size?: BadgeSize;
  /** Whether the badge is outlined */
  outlined?: boolean;
  /** Whether the badge is rounded (pill shape) */
  rounded?: boolean;
  /** Whether the badge has a glow effect */
  glow?: boolean;
  /** Whether the badge is pulsing */
  pulse?: boolean;
  /** Additional CSS class names */
  className?: string;
  /** Badge content */
  children: React.ReactNode;
  /** Additional props */
  [x: string]: any;
}

/**
 * Badge component for System Rebellion UI
 * 
 * A customizable badge component that follows the System Rebellion design system.
 * Supports various variants, sizes, and styles.
 */
export const Badge: React.FC<BadgeProps> = ({
  variant = 'primary',
  size = 'md',
  outlined = false,
  rounded = false,
  glow = false,
  pulse = false,
  className = '',
  children,
  ...props
}) => {
  // Build the class names based on props
  const badgeClasses = [
    'sr-badge',
    `sr-badge-${variant}`,
    `sr-badge-${size}`,
    outlined ? 'sr-badge-outlined' : '',
    rounded ? 'sr-badge-rounded' : '',
    glow ? 'sr-badge-glow' : '',
    pulse ? 'sr-badge-pulse' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <span className={badgeClasses} {...props}>
      {children}
    </span>
  );
};

export default Badge;
