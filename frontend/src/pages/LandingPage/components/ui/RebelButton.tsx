// src/components/ui/RebelButton.tsx
import React from 'react';

interface RebelButtonProps {
  variant?: 'primary' | 'secondary' | 'tertiary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
  href?: string;
  target?: string;
}

export const RebelButton: React.FC<RebelButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  children,
  onClick,
  disabled = false,
  loading = false,
  icon,
  className = '',
  type = 'button',
  href,
  target
}) => {
  const getButtonClass = () => {
    const baseClass = 'rebel-button';
    const variantClass = `rebel-button--${variant}`;
    const sizeClass = `rebel-button--${size}`;
    const stateClass = loading ? 'rebel-button--loading' : '';
    
    return `${baseClass} ${variantClass} ${sizeClass} ${stateClass} ${className}`.trim();
  };

  const buttonContent = (
    <>
      {loading && (
        <span className="rebel-button__spinner" />
      )}
      {icon && !loading && (
        <span className="rebel-button__icon">{icon}</span>
      )}
      <span className="rebel-button__content">{children}</span>
    </>
  );

  // If href is provided, render as link
  if (href) {
    return (
      <a
        href={href}
        target={target}
        className={getButtonClass()}
        onClick={onClick}
      >
        {buttonContent}
      </a>
    );
  }

  // Otherwise render as button
  return (
    <button
      type={type}
      className={getButtonClass()}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {buttonContent}
    </button>
  );
};

// Pre-built rebellion-themed buttons
export const JoinRebellionButton: React.FC<{ 
  onClick?: () => void;
  loading?: boolean;
}> = ({ onClick, loading }) => (
  <RebelButton
    variant="primary"
    size="large"
    onClick={onClick}
    loading={loading}
    icon={!loading ? "🚀" : undefined}
  >
    Join the Rebellion
  </RebelButton>
);

export const InstallNowButton: React.FC<{ onClick?: () => void }> = ({ onClick }) => (
  <RebelButton
    variant="secondary"
    size="medium"
    onClick={onClick}
    icon="⚡"
  >
    Install Now
  </RebelButton>
);

export const ViewDocsButton: React.FC<{ href?: string }> = ({ href = "#docs" }) => (
  <RebelButton
    variant="tertiary"
    size="medium"
    href={href}
    icon="📖"
  >
    View Documentation
  </RebelButton>
);

export const EmergencyContactButton: React.FC<{ onClick?: () => void }> = ({ onClick }) => (
  <RebelButton
    variant="danger"
    size="small"
    onClick={onClick}
    icon="🚨"
  >
    Emergency Support
  </RebelButton>
);

export const GitHubButton: React.FC = () => (
  <RebelButton
    variant="secondary"
    size="medium"
    href="https://github.com/hti-monitoring"
    target="_blank"
    icon="⭐"
  >
    Star on GitHub
  </RebelButton>
);

export const ScheduleDemoButton: React.FC<{ onClick?: () => void }> = ({ onClick }) => (
  <RebelButton
    variant="primary"
    size="medium"
    onClick={onClick}
    icon="📅"
  >
    Schedule Demo
  </RebelButton>
);