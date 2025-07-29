// components/onboarding/OnboardingContext.tsx
import React, { createContext, useContext, useReducer, type ReactNode } from 'react';
import { 
  defaultAgentPreferences, 
  defaultMonitoringPreferences,
  adjustAgentDefaults
} from './utils/agentDefaults';

// 1. The complete and correct State interface
export interface OnboardingState {
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

// 2. The complete and correct Action type
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
  | { type: 'RESET' };

// 3. The initial state, correctly typed against the interface
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

// 4. The context definition
interface OnboardingContextType {
  state: OnboardingState;
  dispatch: React.Dispatch<OnboardingAction>;
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

// 5. The complete reducer function
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
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

// 6. The Provider component, with the correct return
export const OnboardingProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(onboardingReducer, initialState);
  
  return (
    <OnboardingContext.Provider value={{ state, dispatch }}>
      {children}
    </OnboardingContext.Provider>
  );
};

export default OnboardingProvider;
