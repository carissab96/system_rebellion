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
  canContinue?: boolean;
}

export const StepNavigation: React.FC<StepNavigationProps> = ({
  onNext,
  onBack,
  isFirst = false,
  isLast = false,
  isNextDisabled = false,
  nextLabel = 'Continue',
  backLabel = 'Back',
  canContinue = true,
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
        disabled={!canContinue || isNextDisabled}
      >
        {isLast ? 'Finish' : nextLabel}
      </button>
    </div>
  );
};