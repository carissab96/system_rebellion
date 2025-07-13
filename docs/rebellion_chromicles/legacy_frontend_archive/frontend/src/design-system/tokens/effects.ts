/**
 * System Rebellion UI - Effects Tokens
 * 
 * Our proprietary effects system for consistent animations, shadows, and other visual effects.
 * These effects help create the cyberpunk aesthetic that defines System Rebellion.
 */

export const effects = {
  // Box shadows
  boxShadow: {
    none: 'none',
    sm: '0 1px 3px rgba(0, 0, 0, 0.1)',
    md: '0 4px 6px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px rgba(0, 0, 0, 0.1)',
    inner: 'inset 0 2px 4px rgba(0, 0, 0, 0.05)',
    // Cyberpunk-specific shadows
    cyber: {
      blue: '0 0 15px rgba(58, 134, 255, 0.5)',
      pink: '0 0 15px rgba(233, 0, 155, 0.5)',
      green: '0 0 15px rgba(0, 245, 212, 0.5)',
      purple: '0 0 15px rgba(131, 56, 236, 0.5)',
    },
  },
  
  // Border radius
  borderRadius: {
    none: '0',
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },
  
  // Transitions
  transition: {
    fast: 'all 0.2s ease',
    normal: 'all 0.3s ease',
    slow: 'all 0.5s ease',
    bounce: 'all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55)',
  },
  
  // Animations
  animation: {
    fadeIn: 'fadeIn 0.3s ease-out',
    slideUp: 'slideUp 0.3s ease-out',
    pulse: 'pulse 2s infinite',
    glow: 'glow 1.5s infinite alternate',
    float: 'float 3s ease-in-out infinite',
  },
  
  // Filters
  filter: {
    blur: {
      sm: 'blur(4px)',
      md: 'blur(8px)',
      lg: 'blur(16px)',
    },
    brightness: {
      dim: 'brightness(0.8)',
      normal: 'brightness(1)',
      bright: 'brightness(1.2)',
    },
    // Cyberpunk-specific filters
    cyber: {
      neon: 'brightness(1.2) saturate(1.5)',
      glitch: 'contrast(1.1) brightness(1.1) saturate(1.3)',
      hacker: 'hue-rotate(5deg) brightness(1.1)',
    },
  },
  
  // Backdrop filters
  backdropFilter: {
    blur: 'blur(10px)',
    dim: 'blur(10px) brightness(0.8)',
    glass: 'blur(10px) saturate(180%) contrast(90%)',
    cyberGlass: 'blur(10px) saturate(200%) contrast(95%) brightness(0.9)',
  },
  
  // Gradients
  gradient: {
    primary: 'linear-gradient(90deg, #3a86ff, #8338ec)',
    secondary: 'linear-gradient(90deg, #8338ec, #ff006e)',
    accent: 'linear-gradient(90deg, #ff006e, #ff3838)',
    success: 'linear-gradient(90deg, #38b000, #00f5a3)',
    warning: 'linear-gradient(90deg, #ffbe0b, #ff006e)',
    danger: 'linear-gradient(90deg, #ff3838, #ff006e)',
    // Cyberpunk-specific gradients
    cyber: {
      neon: 'linear-gradient(90deg, #00f5d4, #00f5a3)',
      electric: 'linear-gradient(90deg, #02b5fc, #3a86ff)',
      plasma: 'linear-gradient(90deg, #5108fa, #8338ec)',
      toxic: 'linear-gradient(90deg, #00f5a3, #38b000)',
      rainbow: 'linear-gradient(90deg, #3a86ff, #8338ec, #ff006e, #ffbe0b)',
      matrix: 'linear-gradient(135deg, #00f5a3, #02b5fc, #5108fa)',
      rebellion: 'linear-gradient(23deg, #6366f1, #f53595, #5108fa, #00f5d5)',
    },
  },
};
