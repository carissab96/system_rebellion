/**
 * System Rebellion UI - Typography Tokens
 * 
 * Our proprietary typography system for consistent text styling.
 * Designed to be both readable and maintain the cyberpunk aesthetic.
 */

export const typography = {
  // Font families
  fontFamily: {
    primary: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    code: "'Courier New', monospace",
    display: "'Orbitron', sans-serif", // For cyberpunk headings (requires import)
  },
  
  // Font weights
  fontWeight: {
    regular: 400,
    medium: 500,
    semiBold: 600,
    bold: 700,
  },
  
  // Font sizes
  fontSize: {
    xs: '0.75rem',     // 12px
    sm: '0.875rem',    // 14px
    md: '1rem',        // 16px
    lg: '1.125rem',    // 18px
    xl: '1.25rem',     // 20px
    xxl: '1.5rem',     // 24px
    xxxl: '2rem',      // 32px
    display: '2.5rem', // 40px
  },
  
  // Line heights
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    loose: 1.8,
  },
  
  // Letter spacing
  letterSpacing: {
    tight: '-0.01em',
    normal: '0',
    wide: '0.02em',
    cyber: '0.05em', // For cyberpunk effect
  },
  
  // Text shadows for cyberpunk effects
  textShadow: {
    none: 'none',
    subtle: '0 0 2px rgba(0, 0, 0, 0.3)',
    glow: {
      blue: '0 0 10px rgba(2, 181, 252, 0.5)',
      pink: '0 0 10px rgba(255, 0, 110, 0.5)',
      green: '0 0 10px rgba(0, 245, 163, 0.5)',
      purple: '0 0 10px rgba(81, 8, 250, 0.5)',
    },
  },
  
  // Predefined text styles
  textStyle: {
    heading1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '0.02em',
    },
    heading2: {
      fontSize: '2rem',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '0.01em',
    },
    heading3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '0.01em',
    },
    body: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0',
    },
    bodySmall: {
      fontSize: '0.875rem',
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0',
    },
    caption: {
      fontSize: '0.75rem',
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0.01em',
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 600,
      lineHeight: 1.2,
      letterSpacing: '0.02em',
      textTransform: 'uppercase' as const,
    },
  },
};
