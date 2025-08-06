// components/onboarding/steps/index.ts
import { HamstersConfig } from './agents/HamstersConfig';
import { HawkingtonConfig } from './agents/HawkingtonConfig';
import { MonitoringConfig } from './agents/MonitoringConfig';
import { SpecialistsConfig } from './agents/SpecialistsConfig';
import { StickConfig } from './agents/StickConfig';
import { AgentsIntroStep } from './AgentsIntroStep';
import { CompleteStep } from './CompleteStep';
import { PermissionsStep } from './PermissionsStep';
import { ProfileStep } from './ProfileStep';
import { SystemNameStep } from './SystemNameStep';
import { SystemProfileStep } from './SystemProfileStep';
import { WelcomeStep } from './WelcomeStep';

export interface OnboardingStep {
  id: string;
  title: string;
  subtitle: string;
  component: React.ComponentType<any>;
}

export const steps: OnboardingStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to System Rebellion',
    subtitle: 'Where AI agents remember everything',
    component: WelcomeStep
  },
  {
    id: 'profile',
    title: 'Create Your Profile',
    subtitle: 'Tell us about yourself',
    component: ProfileStep
  },
  {
    id: 'permissions',
    title: 'System Access Setup',
    subtitle: 'Configure monitoring permissions',
    component: PermissionsStep
  },
  {
    id: 'system_profile',
    title: 'System Configuration',
    subtitle: 'Help us understand your infrastructure',
    component: SystemProfileStep
  },
  {
    id: 'system',
    title: 'Name Your System',
    subtitle: 'Give your infrastructure an identity',
    component: SystemNameStep
  },
  {
    id: 'agents',
    title: 'Meet Your AI Agents',
    subtitle: 'Six personalities, infinite memory',
    component: AgentsIntroStep
  },
  {
    id: 'hawkington',
    title: 'Configure Sir Hawkington',
    subtitle: 'Your aristocratic triage commander',
    component: HawkingtonConfig
  },
  {
    id: 'stick',
    title: 'Configure The Stick',
    subtitle: 'Anxiety-driven hypervigilance',
    component: StickConfig
  },
  {
    id: 'hamsters',
    title: 'Configure The Hamsters',
    subtitle: 'Beer-fueled infrastructure team',
    component: HamstersConfig
  },
  {
    id: 'specialists',
    title: 'Configure Specialists',
    subtitle: 'Snail, QSP, and VIC-20',
    component: SpecialistsConfig
  },
 // Continue components/onboarding/steps/index.ts
 {
    id: 'monitoring',
    title: 'Set Monitoring Preferences',
    subtitle: 'Define your thresholds',
    component: MonitoringConfig
  },
  {
    id: 'complete',
    title: 'Initialization Complete',
    subtitle: 'Your AI agents are ready',
    component: CompleteStep
  }
];

export * from './WelcomeStep';
export * from './ProfileStep';
export * from './PermissionsStep';
export * from './SystemProfileStep';
export * from './SystemNameStep';
export * from './AgentsIntroStep';
export * from './CompleteStep';