/**
 * System Rebellion UI - Spacing Tokens
 * 
 * Our proprietary spacing system for consistent layout and component sizing.
 * Based on a 4px base unit for perfect alignment across the application.
 */

export const spacing = {
  // Base units
  xxs: '2px',
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
  xxxl: '64px',
  
  // Component-specific spacing
  button: {
    paddingX: '16px',
    paddingY: '8px',
    iconSize: '20px',
    iconGap: '8px',
  },
  
  card: {
    padding: '20px',
    gap: '16px',
    borderRadius: '12px',
  },
  
  input: {
    paddingX: '12px',
    paddingY: '8px',
    borderRadius: '8px',
  },
  
  // Layout spacing
  layout: {
    containerPadding: '20px',
    sectionGap: '32px',
    itemGap: '16px',
  },
  
  // Helper function to get spacing in pixels
  px: (value: number) => `${value * 4}px`,
};
