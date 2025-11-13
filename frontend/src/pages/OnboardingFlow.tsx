// pages/OnboardingFlow.tsx
// SYSTEM REBELLION - Onboarding Flow (Part 1 of 2)
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "Configure your consciousness. Meet your agents."
//
// Multi-step onboarding with system detection, network checks, and agent intros.
// Progress is saved. Can be resumed. Can be re-run from settings.
// No skipping. Must complete to access the theater.

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from '../store/store';
import {
  detectSystem,
  validateSystem,
  testNetworkLatency,
  checkPortAccessibility,
  SYSTEM_REQUIREMENTS,
  type DetectedSystem,
} from '../utils/systemDetection';
import './OnboardingFlow.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Onboarding steps
enum OnboardingStep {
  WELCOME = 0,
  SYSTEM_DETECTION = 1,
  NETWORK_CHECK = 2,
  AGENT_INTRODUCTION = 3,
  COMPLETE = 4,
}

// Disk type options
type DiskType = 'ssd' | 'hdd' | 'unknown';

// Network setup options
type NetworkSetup = 'home' | 'small_team' | 'enterprise';

// Agent data
const AGENTS = [
  {
    name: 'Sir Hawkington',
    role: 'Triage Commander',
    color: 'var(--hawkington-gold)',
    personality: 'Aristocratic precision in system analysis and agent orchestration',
    capabilities: ['System triage', 'Agent coordination', 'Priority routing', 'Decision making'],
  },
  {
    name: 'Meth Snail (Terry)',
    role: 'Performance Optimizer',
    color: 'var(--snail-electric)',
    personality: 'Caffeinated speed demon ensuring maximum system efficiency',
    capabilities: ['Memory optimization', 'Cache management', 'Performance tuning', 'Speed monitoring'],
  },
  {
    name: 'The Hamsters',
    role: 'Storage Managers',
    color: 'var(--hamster-amber)',
    personality: 'Beer-powered telepathic engineers managing disk space',
    capabilities: ['Disk monitoring', 'Storage cleanup', 'Backup management', 'Telepathic consensus'],
  },
  {
    name: 'Quantum Shadow People',
    role: 'Network Security',
    color: 'var(--qsp-violet)',
    personality: 'Quantum-phase monitoring for paranoid network protection',
    capabilities: ['Network security', 'Threat detection', 'Firewall monitoring', 'Quantum encryption'],
  },
  {
    name: 'The Stick',
    role: 'Learning Coordinator',
    color: 'var(--stick-coral)',
    personality: 'Patient, persistent behavior monitoring and system education',
    capabilities: ['Learning tracking', 'Compliance monitoring', 'Behavior guidance', 'Progress reporting'],
  },
  {
    name: 'VIC-20 Sage',
    role: 'Coordination Oracle',
    color: 'var(--vic20-cyan)',
    personality: 'Ancient VIC-20 wisdom orchestrating multi-agent harmony',
    capabilities: ['Agent coordination', 'Pattern recognition', 'Wisdom sharing', 'System orchestration'],
  },
];

export const OnboardingFlow: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Current step
  const [currentStep, setCurrentStep] = useState<OnboardingStep>(OnboardingStep.WELCOME);

  // System detection state
  const [detectedSystem, setDetectedSystem] = useState<DetectedSystem | null>(null);
  const [systemValidation, setSystemValidation] = useState<ReturnType<typeof validateSystem> | null>(null);
  const [diskType, setDiskType] = useState<DiskType>('unknown');
  const [networkSetup, setNetworkSetup] = useState<NetworkSetup>('home');
  const [canProceed, setCanProceed] = useState(false);

  // Network check state
  const [networkLatency, setNetworkLatency] = useState<number | null>(null);
  const [portAccessible, setPortAccessible] = useState<boolean | null>(null);
  const [networkCheckComplete, setNetworkCheckComplete] = useState(false);
  const [networkCheckLoading, setNetworkCheckLoading] = useState(false);

  // Agent introduction state
  const [currentAgentIndex, setCurrentAgentIndex] = useState(0);

  // Loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Detect system on mount
  useEffect(() => {
    if (currentStep === OnboardingStep.SYSTEM_DETECTION && !detectedSystem) {
      const detected = detectSystem();
      setDetectedSystem(detected);
      const validation = validateSystem(detected);
      setSystemValidation(validation);
      setCanProceed(validation.meetsMinimum);
    }
  }, [currentStep, detectedSystem]);

  // Run network check
  const runNetworkCheck = async () => {
    setNetworkCheckLoading(true);
    setError(null);

    try {
      const latency = await testNetworkLatency(API_BASE_URL);
      setNetworkLatency(latency);

      const accessible = await checkPortAccessibility(API_BASE_URL);
      setPortAccessible(accessible);

      setNetworkCheckComplete(true);
    } catch (err) {
      setError('Network check failed. Please check your connection.');
    } finally {
      setNetworkCheckLoading(false);
    }
  };

  // Save onboarding data to backend
  const saveOnboardingData = async () => {
    if (!detectedSystem) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/update-profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          operating_system: detectedSystem.os,
          os_version: detectedSystem.osVersion,
          cpu_cores: detectedSystem.cpuCores,
          total_memory: detectedSystem.ramGB,
          disk_type: diskType,
          network_setup: networkSetup,
          timezone: detectedSystem.timezone,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save onboarding data');
      }

      navigate('/theater');
    } catch (err) {
      setError('Failed to save configuration. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Navigation handlers
  const handleNext = () => {
    if (currentStep === OnboardingStep.COMPLETE) {
      saveOnboardingData();
    } else if (currentStep === OnboardingStep.AGENT_INTRODUCTION) {
      if (currentAgentIndex < AGENTS.length - 1) {
        setCurrentAgentIndex(currentAgentIndex + 1);
      } else {
        setCurrentStep(OnboardingStep.COMPLETE);
      }
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep === OnboardingStep.AGENT_INTRODUCTION && currentAgentIndex > 0) {
      setCurrentAgentIndex(currentAgentIndex - 1);
    } else if (currentStep > OnboardingStep.WELCOME) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canGoNext = () => {
    switch (currentStep) {
      case OnboardingStep.WELCOME:
        return true;
      case OnboardingStep.SYSTEM_DETECTION:
        return canProceed;
      case OnboardingStep.NETWORK_CHECK:
        return networkCheckComplete;
      case OnboardingStep.AGENT_INTRODUCTION:
        return true;
      case OnboardingStep.COMPLETE:
        return true;
      default:
        return false;
    }
  };

  const currentAgent = AGENTS[currentAgentIndex];

  return (
    <div className="onboarding-container">
      {/* Progress bar */}
      <div className="onboarding-progress">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${(currentStep / (OnboardingStep.COMPLETE)) * 100}%` }}
          />
        </div>
        <div className="progress-steps">
          {['Welcome', 'System', 'Network', 'Agents', 'Complete'].map((label, idx) => (
            <div
              key={idx}
              className={`progress-step ${idx <= currentStep ? 'active' : ''} ${idx < currentStep ? 'completed' : ''}`}
            >
              <div className="step-circle">{idx < currentStep ? '✓' : idx + 1}</div>
              <div className="step-label">{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Main content */}
      <div className="onboarding-content">
        {/* TODO: Add step content rendering - see Part 2 */}
        <div className="step-placeholder">
          Step {currentStep} content will be added in Part 2
        </div>
      </div>

      {/* Navigation */}
      <div className="onboarding-nav">
        {currentStep > OnboardingStep.WELCOME && (
          <button className="btn btn-secondary" onClick={handleBack}>
            Back
          </button>
        )}
        <button
          className="btn btn-primary"
          onClick={handleNext}
          disabled={!canGoNext() || isLoading}
        >
          {isLoading ? 'Saving...' : currentStep === OnboardingStep.COMPLETE ? 'Enter Theater' : 'Next'}
        </button>
      </div>

      {/* Error display */}
      {error && (
        <div className="onboarding-error">
          {error}
        </div>
      )}
    </div>
  );
};

// TODO: Part 2 will add:
// - Step content rendering
// - Welcome step UI
// - System detection UI
// - Network check UI
// - Agent introduction UI
// - Complete step UI
