// components/onboarding/components/StepNavigation.tsx
import React from 'react';

interface StepNavigationProps {
  onNext: () => void;
  onBack: () => void;
  isFirst?: boolean;
  isLast?: boolean;
  isNextDisabled?: boolean;
  nextLabel?: string;
  backLabel?: string;
}

export const StepNavigation: React.FC<StepNavigationProps> = ({
  onNext,
  onBack,
  isFirst = false,
  isLast = false,
  isNextDisabled = false,
  nextLabel = 'Continue',
  backLabel = 'Back',
}) => {
  return (
    <div className="button-group">
      {!isFirst && (
        <button className="onboarding-button secondary" onClick={onBack}>
          {backLabel}
        </button>
      )}
      <button 
        className="onboarding-button primary" 
        onClick={onNext}
        disabled={isNextDisabled}
      >
        {isLast ? 'Finish' : nextLabel}
      </button>
    </div>
  );
};