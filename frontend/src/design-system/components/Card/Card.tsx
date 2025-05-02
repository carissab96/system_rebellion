import React from 'react';
import './Card.css';
import { colors, effects, spacing } from '../../tokens';

export type CardVariant = 'default' | 'primary' | 'secondary' | 'accent' | 'cyber';
export type CardElevation = 'flat' | 'low' | 'medium' | 'high';

export interface CardProps {
  /** Card variant that determines color scheme */
  variant?: CardVariant;
  /** Card elevation that determines shadow depth */
  elevation?: CardElevation;
  /** Whether the card has a border */
  bordered?: boolean;
  /** Whether the card has a gradient border */
  gradientBorder?: boolean;
  /** Whether the card has a glow effect */
  glow?: boolean;
  /** Whether the card has a glass effect (backdrop blur) */
  glass?: boolean;
  /** Whether the card is interactive (has hover effects) */
  interactive?: boolean;
  /** Card header content */
  header?: React.ReactNode;
  /** Card footer content */
  footer?: React.ReactNode;
  /** Additional CSS class names */
  className?: string;
  /** Card content */
  children: React.ReactNode;
  /** Additional props */
  [x: string]: any;
}

/**
 * Card component for System Rebellion UI
 * 
 * A customizable card component that follows the System Rebellion design system.
 * Supports various variants, elevations, and styles.
 */
export const Card: React.FC<CardProps> = ({
  variant = 'default',
  elevation = 'low',
  bordered = false,
  gradientBorder = false,
  glow = false,
  glass = false,
  interactive = false,
  header,
  footer,
  className = '',
  children,
  ...props
}) => {
  // Build the class names based on props
  const cardClasses = [
    'sr-card',
    `sr-card-${variant}`,
    `sr-card-elevation-${elevation}`,
    bordered ? 'sr-card-bordered' : '',
    gradientBorder ? 'sr-card-gradient-border' : '',
    glow ? 'sr-card-glow' : '',
    glass ? 'sr-card-glass' : '',
    interactive ? 'sr-card-interactive' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClasses} {...props}>
      {header && <div className="sr-card-header">{header}</div>}
      <div className="sr-card-body">{children}</div>
      {footer && <div className="sr-card-footer">{footer}</div>}
    </div>
  );
};

export default Card;
