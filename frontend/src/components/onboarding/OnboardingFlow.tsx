//new version at at 28 Jul 2025 22.42:11
// components/onboarding/OnboardingFlow.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import type { AxiosError } from 'axios';

// Import our final, robust apiService
import apiService from '../../services/api'; 
import { OnboardingProvider, useOnboarding } from './OnboardingContext';
import { steps } from './steps'; // The array of step configurations
import { ProgressBar } from './components/ProgressBar'; // The progress bar component

import styles from './OnboardingFlow.module.css'; // Our layout styles

const OnboardingFlowContent: React.FC = () => {
  const { state, dispatch } = useOnboarding();
  const { currentStep } = state;
  const navigate = useNavigate();

  const [isCompleting, setIsCompleting] = useState(false);
  const [completionError, setCompletionError] = useState<string | null>(null);

  // --- FIX: THIS DATA IS NOW USED BELOW ---
  const currentStepInfo = steps[currentStep - 1]; // Get config for the current step
  const { component: CurrentStepComponent, title, subtitle } = currentStepInfo;
  const totalSteps = steps.length;

  const handleNext = () => dispatch({ type: 'NEXT_STEP' });
  const handleBack = () => dispatch({ type: 'PREVIOUS_STEP' });

  const handleComplete = async () => {
    if (isCompleting) return;
    setIsCompleting(true);
    setCompletionError(null);

    try {
      await apiService.completeOnboarding(state.preferences);
      navigate('/dashboard'); // Navigate on success
    } catch (err: any) {
      const error = err as AxiosError<any>;
      const errorMessage = error.response?.data?.detail || 'A server error occurred. Please try again.';
      setCompletionError(errorMessage);
    } finally {
      setIsCompleting(false);
    }
  };

  return (
    <div className={styles.onboardingFlow}>
      {/* Compose the module class with the global .card class */}
      <div className={`${styles.onboardingCard} card`}>
        {/* --- FIX: PROGRESS BAR FULLY INTEGRATED --- */}
        <div className="card-body">
            <ProgressBar totalSteps={totalSteps} currentStep={currentStep} />
        </div>

        {/* --- FIX: HEADER IS NOW DYNAMIC --- */}
        <header className={`${styles.stepHeader} card-header`}>
          <h1 className="card-title">{title}</h1>
          <p className="card-subtitle mt-1">{subtitle}</p>
        </header>

        {/* --- FIX: STEP CONTENT IS NOW DYNAMIC --- */}
        <main className={`${styles.contentArea} card-body`}>
          <AnimatePresence mode="wait">
            <motion.div key={currentStep} className="slide-in-up">
              <CurrentStepComponent
                onNext={handleNext}
                onBack={handleBack}
                onComplete={handleComplete}
                isCompleting={isCompleting}
                completionError={completionError}
              />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
};

// The main export wraps everything in the provider, no changes needed here.
export const OnboardingFlow: React.FC = () => {
  return (
    <OnboardingProvider>
      <OnboardingFlowContent />
    </OnboardingProvider>
  );
};






// // components/onboarding/OnboardingFlow.tsx
// import React, { useState } from 'react';
// import apiService from '../../services/api';
// import { useNavigate } from 'react-router-dom';
// import { motion, AnimatePresence } from 'framer-motion';
// import { OnboardingProvider, useOnboarding } from './OnboardingContext';
// import { steps } from './steps';
// import styles from './OnboardingFlow.module.css';
// import { ProgressBar } from './components/ProgressBar';
// import { AxiosError } from 'axios';

// interface StepProps {
//   onNext: () => void;
//   onBack: () => void;
//   onComplete?: () => void;
//   isFirst?: boolean;
//   isLast?: boolean;
// }

// const OnboardingFlowContent: React.FC = () => {
//   const navigate = useNavigate();
//   const { state } = useOnboarding();
//   const [currentStep, setCurrentStep] = useState(0);
//   const {component: CurrentStepComponent, title, subtitle } = steps[currentStep];
//   const totalSteps = steps.length;
//   const [isCompleting, setIsCompleting] = useState(false);
//   const [setCompletionError] = useState<string | null>(null);

//   const handleNext = () => {
//     if (currentStep < totalSteps - 1) {
//       setCurrentStep(currentStep + 1);
//     }
//   };

//   const handleBack = () => {
//     if (currentStep > 0) {
//       setCurrentStep(currentStep - 1);
//     }
//   };

//   const handleComplete = async () => {
//     setIsCompleting(true);
//     try {
//       // Compile all the data
//       const onboardingData = {
//         first_name: state.profile.first_name,
//         last_name: state.profile.last_name,
//         company_name: state.profile.company_name,
//         job_title: state.profile.job_title,
//         system_name: state.system.system_name,
//         system_profile: state.system.system_profile,
//         permissions_granted: state.system.permissions_granted,
//         installation_method: state.system.installation_method,
//         agent_preferences: state.preferences.agent_preferences,
//         monitoring_preferences: state.preferences.monitoring_preferences,
//         is_onboarded: true
//       };

//       await apiService.completeOnboarding(onboardingData);
//       navigate('/dashboard');
//     } catch (err: any) {
//       const error = err as AxiosError<any>;
//       console.error('An error occurred during onboarding completion:', error.response?.data || error.message);
//       setCompletionError(error.response?.data || error.message);
//     } finally {
//       setIsCompleting(false);
//     }
//   };

//   const currentStepConfig = steps[currentStep];
//   const StepComponent = currentStepConfig.component;

//   return (
//     <div className={styles.onboardingFlow}>
//       <div className={styles.onboardingProgress}>
//         <div 
//           className={styles.progressBar} 
//           style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
//         />
//       </div>

//       <AnimatePresence mode="wait">
//         <motion.div
//           key={currentStep}
//           initial={{ opacity: 0, x: 20 }}
//           animate={{ opacity: 1, x: 0 }}
//           exit={{ opacity: 0, x: -20 }}
//           transition={{ duration: 0.3 }}
//           className={styles.onboardingContent}
//         >
//           <div className={styles.stepHeader}>
//             <h1 className={styles.stepTitle}>{currentStepConfig.title}</h1>
//             <p className={styles.stepSubtitle}>{currentStepConfig.subtitle}</p>
//           </div>

//           <div className={styles.stepBody}>
//             <StepComponent
//               onNext={handleNext}
//               onBack={handleBack}
//               onComplete={handleComplete}
//               isFirst={currentStep === 0}
//               isLast={currentStep === totalSteps - 1}
//               isCompleting={isCompleting}
//             />
//           </div>
//         </motion.div>
//       </AnimatePresence>

//       <div className={styles.onboardingFooter}>
//         <span className={styles.stepIndicator}>
//           {currentStep + 1} of {totalSteps}
//         </span>
//       </div>
//     </div>
//   );
// };

// const OnboardingFlow: React.FC = () => {
//   return (
//     <OnboardingProvider>
//       <OnboardingFlowContent />
//     </OnboardingProvider>
//   );
// };

// export default OnboardingFlow;
// export type { StepProps };