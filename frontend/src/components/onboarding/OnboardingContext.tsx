 
 
/* eslint-disable no-unused-vars */
/* eslint-disable no-console */
// components/onboarding/OnboardingContext.tsx
import React, { createContext, useReducer, useState, useCallback, useEffect, type ReactNode } from 'react';

import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';

import { apiService } from '../../services/api';
import { logout } from '../../store/slices/authSlice';
import type { RootState } from '../../store/store';

import { 
  defaultAgentPreferences, 
  defaultMonitoringPreferences,
  adjustAgentDefaults
} from './utils/agentDefaults';

// Backend progress tracking interface
interface OnboardingProgress {
  form_data: OnboardingState | null;
  current_step: number;
  completed_steps: number[];
  step_data: Record<string, any>;
  started_at: string;
  last_updated_at: string;
  completion_percentage: number;
}

// State interface
interface OnboardingState {
  currentStep: number;
  profile: {
    first_name: string;
    last_name: string;
    company_name: string;
    job_title: string;
  };
  system: {
    system_name: string;
    system_profile: {
      os_type: string;
      os_version: string;
      total_ram_gb: number;
      storage_type: string;
      total_storage_gb: number;
      cpu_cores: number;
      is_virtual: boolean;
      network_type: string;
      admin_access: string;
      mdm_controlled: boolean;
      custom_restrictions: string[];
    };
    permissions_granted: boolean;
    installation_method: string;
  };
  preferences: {
    first_name: string;
    agent_preferences: typeof defaultAgentPreferences;
    monitoring_preferences: typeof defaultMonitoringPreferences;
  };
}

// Action type
export type OnboardingAction = 
  | { type: 'UPDATE_PROFILE'; payload: Partial<OnboardingState['profile']> }
  | { type: 'UPDATE_SYSTEM'; payload: Partial<OnboardingState['system']> }
  | { type: 'UPDATE_SYSTEM_PROFILE'; payload: Partial<OnboardingState['system']['system_profile']> }
  | { type: 'UPDATE_AGENT_PREFERENCES'; payload: Partial<OnboardingState['preferences']['agent_preferences']> }
  | { type: 'UPDATE_MONITORING_PREFERENCES'; payload: Partial<OnboardingState['preferences']['monitoring_preferences']> }
  | { type: 'SET_PERMISSIONS'; payload: { permissions_granted: boolean; method: string } }
  | { type: 'ADJUST_DEFAULTS_FROM_PROFILE'; payload: OnboardingState['system']['system_profile'] }
  | { type: 'NEXT_STEP' }
  | { type: 'PREVIOUS_STEP' }
  | { type: 'RESET' }
  | { type: 'LOAD_SAVED_STATE'; payload: OnboardingState };

// Initial state
const initialState: OnboardingState = {
  currentStep: 1,
  profile: {
    first_name: '',
    last_name: '',
    company_name: '',
    job_title: ''
  },
  system: {
    system_name: '',
    system_profile: {
      os_type: '',
      os_version: '',
      total_ram_gb: 0,
      storage_type: '',
      total_storage_gb: 0,
      cpu_cores: 0,
      is_virtual: false,
      network_type: 'standard',
      admin_access: 'full',
      mdm_controlled: false,
      custom_restrictions: []
    },
    permissions_granted: false,
    installation_method: ''
  },
  preferences: {
    first_name: '',
    agent_preferences: defaultAgentPreferences,
    monitoring_preferences: defaultMonitoringPreferences
  }
};

// Context type definition
interface OnboardingContextType {
  state: OnboardingState;
  dispatch: React.Dispatch<OnboardingAction>;
  
  // Save/Load functionality
  saveProgress: () => Promise<void>;
  loadSavedProgress: () => Promise<boolean>;
  clearSavedProgress: () => Promise<void>;
  
  // Modal state
  showSaveModal: boolean;
  setShowSaveModal: (show: boolean) => void;
  
  // Exit actions
  saveAndExit: () => Promise<void>;
  exitWithoutSaving: () => Promise<void>;
  saveAndLogout: () => Promise<void>;
  
  // Preview mode
  startPreviewMode: (agentId: string) => Promise<void>;
  
  // Progress state
  isProgressSaved: boolean;
  savedAt: string | null;
  backendProgress?: OnboardingProgress;
}

// Create the context
export const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

// Reducer function
function onboardingReducer(state: OnboardingState, action: OnboardingAction): OnboardingState {
  switch (action.type) {
    case 'UPDATE_PROFILE':
      return { ...state, profile: { ...state.profile, ...action.payload } };
    case 'UPDATE_SYSTEM':
      return { ...state, system: { ...state.system, ...action.payload } };
    case 'UPDATE_SYSTEM_PROFILE':
      return { ...state, system: { ...state.system, system_profile: { ...state.system.system_profile, ...action.payload } } };
    case 'UPDATE_AGENT_PREFERENCES':
      return { ...state, preferences: { ...state.preferences, agent_preferences: { ...state.preferences.agent_preferences, ...action.payload } } };
    case 'UPDATE_MONITORING_PREFERENCES':
      return { ...state, preferences: { ...state.preferences, monitoring_preferences: { ...state.preferences.monitoring_preferences, ...action.payload } } };
    case 'SET_PERMISSIONS':
      return { ...state, system: { ...state.system, permissions_granted: action.payload.permissions_granted, installation_method: action.payload.method } };
    case 'ADJUST_DEFAULTS_FROM_PROFILE':
      const newAgentPrefs = adjustAgentDefaults(action.payload);
      return { ...state, preferences: { ...state.preferences, agent_preferences: newAgentPrefs } };
    case 'NEXT_STEP':
      return { ...state, currentStep: state.currentStep + 1 };
    case 'PREVIOUS_STEP':
      return { ...state, currentStep: state.currentStep - 1 };
    case 'LOAD_SAVED_STATE':
      return action.payload;
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

// Provider component
const OnboardingProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(onboardingReducer, initialState);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [isProgressSaved, setIsProgressSaved] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [backendProgress, setBackendProgress] = useState<OnboardingProgress>();
  const [isLoadingProgress, setIsLoadingProgress] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const reduxDispatch = useDispatch();
  // Get current user and navigation
  const user = useSelector((state: RootState) => state.auth.user);
  const navigate = useNavigate();
  const location = useLocation();
  const fromContinueSetup = location.state?.fromContinueSetup;


  // Backend API methods
  const saveProgressToBackend = useCallback(async (): Promise<void> => {
    try {
      const progressData = {
        current_step: state.currentStep,
        completed_steps: Array.from({ length: state.currentStep - 1 }, (_, i) => i + 1),
        form_data: {
          profile: state.profile,
          system: state.system,
          preferences: state.preferences
        }
      };

      const response = await apiService.saveOnboardingProgress(progressData);
      if (response.data) {
        setBackendProgress(response.data);
        console.log('Progress saved to backend:', response.data);
      }
    } catch (error) {
      console.error('Failed to save progress to backend:', error);
      throw error;
    }
  }, [state]);

  const loadProgressFromBackend = useCallback(async (): Promise<OnboardingProgress | null> => {
    if (isLoadingProgress) return null;

    setIsLoadingProgress(true);
    try {
      const response = await apiService.getOnboardingProgress();
      if (response.data) {
        setBackendProgress(response.data);
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('Failed to load progress from backend:', error);
      return null;
    } finally {
      setIsLoadingProgress(false);
    }
  }, [isLoadingProgress]);

  const clearProgressFromBackend = useCallback(async (): Promise<void> => {
    try {
      await apiService.clearOnboardingProgress();
      setBackendProgress(undefined);
      console.log('Progress cleared from backend');
    } catch (error) {
      console.error('Failed to clear progress from backend:', error);
      throw error;
    }
  }, []);

  // Enhanced save progress (backend + localStorage fallback)
  const saveProgress = useCallback(async (): Promise<void> => {
    try {
      // Try backend first
      await saveProgressToBackend();
    } catch (backendError) {
      console.warn('Backend save failed, falling back to localStorage:', backendError);
    }

    // Always save to localStorage as backup
    try {
      const progressToSave = {
        ...state,
        savedAt: new Date().toISOString(),
      };
      localStorage.setItem('onboarding-progress', JSON.stringify(progressToSave));
      setIsProgressSaved(true);
      setSavedAt(new Date().toISOString());
    } catch (error) {
      console.error('Failed to save progress to localStorage:', error);
      throw error;
    }
  }, [state, saveProgressToBackend]);

  // Enhanced load progress (backend first, localStorage fallback)
  const loadSavedProgress = useCallback(async (): Promise<boolean> => {
    try {
      // Try backend first
      const backendData = await loadProgressFromBackend();
      if (backendData && backendData.form_data) {
        const stateData = backendData.form_data as unknown as OnboardingState;
        dispatch({ type: 'LOAD_SAVED_STATE', payload: { ...stateData, currentStep: backendData.current_step } });
        setIsProgressSaved(true);
        setSavedAt(backendData.last_updated_at);
        console.log('Progress loaded from backend:', backendData);
        return true;
      }
    } catch (error) {
      console.warn('Backend load failed, trying localStorage:', error);
    }

    // Fallback to localStorage
    try {
      const saved = localStorage.getItem('onboarding-progress');
      if (!saved) return false;

      const progressData = JSON.parse(saved);
      const { savedAt: savedTime, ...stateData } = progressData;
      
      dispatch({ type: 'LOAD_SAVED_STATE', payload: stateData });
      setIsProgressSaved(true);
      setSavedAt(savedTime);
      
      console.log('Progress loaded from localStorage:', progressData);
      return true;
    } catch (error) {
      console.error('Failed to load saved progress:', error);
      localStorage.removeItem('onboarding-progress');
      return false;
    }
  }, [loadProgressFromBackend]);

  // Enhanced clear progress (backend + localStorage)
  const clearSavedProgress = useCallback(async (): Promise<void> => {
    try {
      // Clear from backend
      await clearProgressFromBackend();
    } catch (error) {
      console.warn('Backend clear failed:', error);
    }

    // Always clear localStorage
    localStorage.removeItem('onboarding-progress');
    setIsProgressSaved(false);
    setSavedAt(null);
    console.log('Saved progress cleared');
  }, [clearProgressFromBackend]);

  // Load progress only once and respect the fromContinueSetup flag
  useEffect(() => {
    if (user && !hasLoaded && !fromContinueSetup) {
      setHasLoaded(true);
      loadSavedProgress();
    }
  }, [user, hasLoaded, fromContinueSetup, loadSavedProgress]);

  // Prevent redirect to continue-setup when coming from continue-setup
  // useEffect(() => {
  //   if (user && user.is_onboarded && fromContinueSetup) {
  //     // Only redirect if not coming from continue setup page and has progress
  //     const checkAndRedirect = async () => {
  //       const hasLocalProgress = localStorage.getItem('onboarding-progress');
  //       const hasBackendProgress = backendProgress;
        
  //       if (hasLocalProgress || hasBackendProgress) {
  //         navigate('/continue-setup', { replace: true });
  //       }
  //     };
      
  //     checkAndRedirect();
  //   }
  // }, [user, fromContinueSetup, backendProgress, navigate]);

  // Simple save and exit
  const saveAndExit = async () => {
    try {
      await saveProgress();
      const destination = user?.is_onboarded ? '/agent-theater' : '/';
      navigate(destination, { replace: true });
    } catch (error) {
      console.error('Save error:', error);
      navigate(user?.is_onboarded ? '/agent-theater' : '/', { replace: true });
    }
  };

  // Simple exit without saving
  const exitWithoutSaving = async () => {
    if (window.confirm("Are you sure? You'll lose all progress and start over.")) {
      try {
        await clearSavedProgress();
      } catch (error) {
        console.error('Clear error:', error);
      }
      navigate('/', { replace: true });
    }
  };
  const saveAndLogout = async () => {
    try {
      await saveProgress();
      // Import and dispatch logout action
      reduxDispatch(logout());

      navigate('/', { replace: true });
    } catch (error) {
      console.error('Save and logout error:', error);
      reduxDispatch(logout());
      navigate('/', { replace: true });
    }
  };

  // Start preview mode with selected agent
  const startPreviewMode = async (agentId: string) => {
    try {
      await saveProgress();
      
      // Set preview mode in backend
      const previewData = {
        preview_agent_selected: agentId,
        preview_started_at: new Date().toISOString(),
        preview_expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days
      };
      
      await apiService.request({
        method: 'PUT',
        url: '/api/users/preview-mode',
        data: previewData
      });
      
      // Navigate to Agent Theater with preview mode
      navigate('/agent-theater?preview=true', { replace: true });
    } catch (error) {
      console.error('Start preview mode error:', error);
      // Still navigate but without backend update
      navigate('/agent-theater', { replace: true });
    }
  };
  const value: OnboardingContextType = {
    state,
    dispatch,
    saveProgress,
    loadSavedProgress,
    clearSavedProgress,
    showSaveModal,
    setShowSaveModal,
    saveAndExit,
    exitWithoutSaving,
    saveAndLogout,
    startPreviewMode,
    isProgressSaved,
    savedAt,
    backendProgress
  };

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  );

}
// Export the context and types

// export { OnboardingContext };
export type { OnboardingContextType, OnboardingProgress, OnboardingState }
export default OnboardingProvider