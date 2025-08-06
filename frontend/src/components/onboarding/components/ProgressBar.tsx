import React from 'react';

import styles from '../OnboardingFlow.module.css';

type ProgressBarProps = {
  totalSteps: number;
  currentStep: number;
};

export const ProgressBar: React.FC<ProgressBarProps> = ({ totalSteps, currentStep }) => {
  return (
    <div className={styles.progressTracker}>
      {Array.from({ length: totalSteps }).map((_, index) => (
        <React.Fragment key={index}>
          <div
            className={`
              ${styles.progressStep}
              ${index + 1 === currentStep ? styles.active : ''}
              ${index + 1 < currentStep ? styles.completed : ''}
            `}
          />
          {index < totalSteps - 1 && <div className={styles.progressLine} />}
        </React.Fragment>
      ))}
    </div>
  );
};