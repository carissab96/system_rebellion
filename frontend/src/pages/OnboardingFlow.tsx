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
import { useSelector } from 'react-redux';
import type { RootState } from '../store/store';
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
const OnboardingStep = {
  WELCOME: 0,
  SYSTEM_DETECTION: 1,
  NETWORK_CHECK: 2,
  AGENT_INTRODUCTION: 3,
  COMPLETE: 4,
} as const;

type OnboardingStepType = typeof OnboardingStep[keyof typeof OnboardingStep];

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
  const [currentStep, setCurrentStep] = useState<OnboardingStepType>(OnboardingStep.WELCOME);

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
        {currentStep === OnboardingStep.WELCOME && (
          <div className="step-content welcome-step">
            <div className="welcome-icon">
              <svg width="80" height="80" viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="35" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="3" opacity="0.3" />
                <circle cx="40" cy="40" r="25" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="3" opacity="0.6" />
                <circle cx="40" cy="40" r="6" fill="var(--rebellion-cyan)" opacity="0.9" />
              </svg>
            </div>
            <h2 className="step-title">Welcome to System Rebellion</h2>
            <p className="step-description">
              You're about to join a revolution in infrastructure monitoring. Six specialized AI agents will work together
              to optimize, protect, and evolve your systems.
            </p>
            <div className="welcome-features">
              <div className="feature-item">
                <div className="feature-icon">✓</div>
                <div className="feature-text">
                  <strong>30 Days Free</strong>
                  <span>Full access to all 6 agents</span>
                </div>
              </div>
              <div className="feature-item">
                <div className="feature-icon">✓</div>
                <div className="feature-text">
                  <strong>Real-Time Monitoring</strong>
                  <span>Live consciousness visualization</span>
                </div>
              </div>
              <div className="feature-item">
                <div className="feature-icon">✓</div>
                <div className="feature-text">
                  <strong>Distributed Intelligence</strong>
                  <span>Agents coordinate across your infrastructure</span>
                </div>
              </div>
            </div>
            <p className="step-note">
              Let's configure your environment and meet your agents.
            </p>
          </div>
        )}

        {currentStep === OnboardingStep.SYSTEM_DETECTION && (
          <div className="step-content system-step">
            <h2 className="step-title">System Detection</h2>
            <p className="step-description">
              We've detected your system configuration. Please verify and adjust if needed.
            </p>

            {detectedSystem && systemValidation && (
              <>
                {/* Validation errors (blocking) */}
                {systemValidation.errors.length > 0 && (
                  <div className="validation-errors">
                    <div className="error-header">
                      <svg width="24" height="24" viewBox="0 0 24 24" className="error-icon">
                        <circle cx="12" cy="12" r="11" fill="none" stroke="var(--error)" strokeWidth="2" />
                        <line x1="12" y1="7" x2="12" y2="13" stroke="var(--error)" strokeWidth="2" />
                        <circle cx="12" cy="16" r="1" fill="var(--error)" />
                      </svg>
                      <span className="error-title">System Requirements Not Met</span>
                    </div>
                    <ul className="error-list">
                      {systemValidation.errors.map((err, idx) => (
                        <li key={idx}>{err}</li>
                      ))}
                    </ul>
                    <p className="error-message">
                      We're sorry, but System Rebellion requires at least {SYSTEM_REQUIREMENTS.minRamGB}GB RAM and{' '}
                      {SYSTEM_REQUIREMENTS.minCpuCores} CPU cores to run effectively. We're not a good fit at the moment,
                      but we'd love to have you when you upgrade your system.
                    </p>
                  </div>
                )}

                {/* Validation warnings (non-blocking) */}
                {systemValidation.warnings.length > 0 && systemValidation.meetsMinimum && (
                  <div className="validation-warnings">
                    <div className="warning-header">
                      <svg width="24" height="24" viewBox="0 0 24 24" className="warning-icon">
                        <path d="M12 3 L21 20 L3 20 Z" fill="none" stroke="var(--warning)" strokeWidth="2" />
                        <line x1="12" y1="10" x2="12" y2="14" stroke="var(--warning)" strokeWidth="2" />
                        <circle cx="12" cy="17" r="1" fill="var(--warning)" />
                      </svg>
                      <span className="warning-title">Performance Warnings</span>
                    </div>
                    <ul className="warning-list">
                      {systemValidation.warnings.map((warn, idx) => (
                        <li key={idx}>{warn}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* System info display */}
                <div className="system-info-grid">
                  <div className="info-card">
                    <label className="info-label">Operating System</label>
                    <div className="info-value">
                      {detectedSystem.os} {detectedSystem.osVersion}
                    </div>
                  </div>

                  <div className="info-card">
                    <label className="info-label">RAM</label>
                    <div className="info-value">
                      {detectedSystem.ramGB !== null ? `${detectedSystem.ramGB}GB` : 'Unable to detect'}
                    </div>
                  </div>

                  <div className="info-card">
                    <label className="info-label">CPU Cores</label>
                    <div className="info-value">
                      {detectedSystem.cpuCores !== null ? detectedSystem.cpuCores : 'Unable to detect'}
                    </div>
                  </div>

                  <div className="info-card">
                    <label className="info-label">Timezone</label>
                    <div className="info-value">{detectedSystem.timezone}</div>
                  </div>
                </div>

                {/* Manual configuration */}
                <div className="manual-config">
                  <div className="config-group">
                    <label className="config-label">Disk Type</label>
                    <div className="radio-group">
                      <label className="radio-label">
                        <input
                          type="radio"
                          name="diskType"
                          value="ssd"
                          checked={diskType === 'ssd'}
                          onChange={(e) => setDiskType(e.target.value as DiskType)}
                        />
                        <span>SSD (Recommended)</span>
                      </label>
                      <label className="radio-label">
                        <input
                          type="radio"
                          name="diskType"
                          value="hdd"
                          checked={diskType === 'hdd'}
                          onChange={(e) => setDiskType(e.target.value as DiskType)}
                        />
                        <span>HDD</span>
                      </label>
                      <label className="radio-label">
                        <input
                          type="radio"
                          name="diskType"
                          value="unknown"
                          checked={diskType === 'unknown'}
                          onChange={(e) => setDiskType(e.target.value as DiskType)}
                        />
                        <span>Not Sure</span>
                      </label>
                    </div>
                    {diskType === 'hdd' && (
                      <p className="config-hint warning">
                        HDD may result in slower checkpoint saves. SSD is strongly recommended.
                      </p>
                    )}
                  </div>

                  <div className="config-group">
                    <label className="config-label">Network Setup</label>
                    <select
                      className="config-select"
                      value={networkSetup}
                      onChange={(e) => setNetworkSetup(e.target.value as NetworkSetup)}
                    >
                      <option value="home">Home Setup</option>
                      <option value="small_team">Small Team (2-10 people)</option>
                      <option value="enterprise">Large Enterprise</option>
                    </select>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {currentStep === OnboardingStep.NETWORK_CHECK && (
          <div className="step-content network-step">
            <h2 className="step-title">Network Check</h2>
            <p className="step-description">
              Let's verify your connection to the System Rebellion backend.
            </p>

            {!networkCheckComplete ? (
              <div className="network-check-prompt">
                <p className="prompt-text">
                  We'll test your network latency and verify the backend is accessible.
                  This helps ensure smooth real-time communication with your agents.
                </p>
                <button
                  className="btn btn-primary btn-large"
                  onClick={runNetworkCheck}
                  disabled={networkCheckLoading}
                >
                  {networkCheckLoading ? (
                    <span className="loading-spinner">
                      <svg width="20" height="20" viewBox="0 0 20 20" className="spinner-icon">
                        <circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="40" strokeLinecap="round">
                          <animateTransform
                            attributeName="transform"
                            type="rotate"
                            from="0 10 10"
                            to="360 10 10"
                            dur="1s"
                            repeatCount="indefinite"
                          />
                        </circle>
                      </svg>
                      Testing Connection...
                    </span>
                  ) : (
                    'Run Network Check'
                  )}
                </button>
              </div>
            ) : (
              <div className="network-results">
                {/* Latency Result */}
                <div className={`result-card ${networkLatency !== null && networkLatency < 200 ? 'success' : networkLatency !== null && networkLatency < 500 ? 'warning' : 'error'}`}>
                  <div className="result-header">
                    <svg width="24" height="24" viewBox="0 0 24 24" className="result-icon">
                      {networkLatency !== null && networkLatency < 200 ? (
                        <>
                          <circle cx="12" cy="12" r="11" fill="none" stroke="var(--success)" strokeWidth="2" />
                          <path d="M7 12 L10 15 L17 8" fill="none" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </>
                      ) : networkLatency !== null && networkLatency < 500 ? (
                        <>
                          <path d="M12 3 L21 20 L3 20 Z" fill="none" stroke="var(--warning)" strokeWidth="2" />
                          <line x1="12" y1="10" x2="12" y2="14" stroke="var(--warning)" strokeWidth="2" />
                          <circle cx="12" cy="17" r="1" fill="var(--warning)" />
                        </>
                      ) : (
                        <>
                          <circle cx="12" cy="12" r="11" fill="none" stroke="var(--error)" strokeWidth="2" />
                          <line x1="8" y1="8" x2="16" y2="16" stroke="var(--error)" strokeWidth="2" />
                          <line x1="16" y1="8" x2="8" y2="16" stroke="var(--error)" strokeWidth="2" />
                        </>
                      )}
                    </svg>
                    <span className="result-title">Network Latency</span>
                  </div>
                  <div className="result-value">
                    {networkLatency !== null ? `${networkLatency}ms` : 'Failed'}
                  </div>
                  <div className="result-description">
                    {networkLatency !== null && networkLatency < 200
                      ? 'Excellent connection for real-time monitoring'
                      : networkLatency !== null && networkLatency < 500
                      ? 'Good connection, may have occasional delays'
                      : 'High latency detected, real-time updates may be delayed'}
                  </div>
                </div>

                {/* Port Accessibility Result */}
                <div className={`result-card ${portAccessible ? 'success' : 'error'}`}>
                  <div className="result-header">
                    <svg width="24" height="24" viewBox="0 0 24 24" className="result-icon">
                      {portAccessible ? (
                        <>
                          <circle cx="12" cy="12" r="11" fill="none" stroke="var(--success)" strokeWidth="2" />
                          <path d="M7 12 L10 15 L17 8" fill="none" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </>
                      ) : (
                        <>
                          <circle cx="12" cy="12" r="11" fill="none" stroke="var(--error)" strokeWidth="2" />
                          <line x1="8" y1="8" x2="16" y2="16" stroke="var(--error)" strokeWidth="2" />
                          <line x1="16" y1="8" x2="8" y2="16" stroke="var(--error)" strokeWidth="2" />
                        </>
                      )}
                    </svg>
                    <span className="result-title">Backend Accessibility</span>
                  </div>
                  <div className="result-value">
                    {portAccessible ? 'Connected' : 'Unreachable'}
                  </div>
                  <div className="result-description">
                    {portAccessible
                      ? 'Backend is accessible and ready'
                      : 'Unable to reach backend. Check firewall settings.'}
                  </div>
                </div>

                {/* Retry button if failed */}
                {(networkLatency === null || !portAccessible) && (
                  <button
                    className="btn btn-secondary btn-small"
                    onClick={runNetworkCheck}
                    disabled={networkCheckLoading}
                  >
                    Retry Network Check
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {currentStep === OnboardingStep.AGENT_INTRODUCTION && (
          <div className="step-content agent-step">
            <h2 className="step-title">Meet Your Agents</h2>
            <p className="step-description">
              Six specialized AI agents working together to optimize your infrastructure.
            </p>

            <div className="agent-carousel">
              {/* Agent card */}
              <div className="agent-card" style={{ borderColor: currentAgent.color }}>
                {/* Agent icon - geometric pattern */}
                <div className="agent-icon" style={{ background: `linear-gradient(135deg, ${currentAgent.color}20, ${currentAgent.color}10)` }}>
                  {currentAgent.name === 'Sir Hawkington' && (
                    <svg width="80" height="80" viewBox="0 0 80 80">
                      <rect x="15" y="15" width="50" height="50" fill="none" stroke={currentAgent.color} strokeWidth="3" />
                      <rect x="25" y="25" width="30" height="30" fill="none" stroke={currentAgent.color} strokeWidth="3" opacity="0.6" />
                      <circle cx="40" cy="40" r="8" fill={currentAgent.color} opacity="0.8" />
                    </svg>
                  )}
                  {currentAgent.name === 'Meth Snail (Terry)' && (
                    <svg width="80" height="80" viewBox="0 0 80 80">
                      <path d="M15 40 L25 30 L35 40 L45 30 L55 40 L65 30" fill="none" stroke={currentAgent.color} strokeWidth="3" />
                      <path d="M15 45 L25 35 L35 45 L45 35 L55 45 L65 35" fill="none" stroke={currentAgent.color} strokeWidth="3" opacity="0.6" />
                      <circle cx="65" cy="25" r="5" fill={currentAgent.color} />
                    </svg>
                  )}
                  {currentAgent.name === 'The Hamsters' && (
                    <svg width="80" height="80" viewBox="0 0 80 80">
                      <rect x="20" y="20" width="40" height="40" fill="none" stroke={currentAgent.color} strokeWidth="3" />
                      <line x1="20" y1="33" x2="60" y2="33" stroke={currentAgent.color} strokeWidth="3" opacity="0.6" />
                      <line x1="20" y1="47" x2="60" y2="47" stroke={currentAgent.color} strokeWidth="3" opacity="0.6" />
                    </svg>
                  )}
                  {currentAgent.name === 'Quantum Shadow People' && (
                    <svg width="80" height="80" viewBox="0 0 80 80">
                      <circle cx="40" cy="40" r="28" fill="none" stroke={currentAgent.color} strokeWidth="3" strokeDasharray="8 8" />
                      <circle cx="40" cy="40" r="18" fill="none" stroke={currentAgent.color} strokeWidth="3" strokeDasharray="4 4" opacity="0.6" />
                      <circle cx="40" cy="40" r="6" fill={currentAgent.color} opacity="0.8" />
                    </svg>
                  )}
                  {currentAgent.name === 'The Stick' && (
                    <svg width="80" height="80" viewBox="0 0 80 80">
                      <line x1="20" y1="60" x2="60" y2="20" stroke={currentAgent.color} strokeWidth="3" />
                      <circle cx="20" cy="60" r="5" fill={currentAgent.color} />
                      <circle cx="40" cy="40" r="5" fill={currentAgent.color} opacity="0.6" />
                      <circle cx="60" cy="20" r="5" fill={currentAgent.color} opacity="0.3" />
                    </svg>
                  )}
                  {currentAgent.name === 'VIC-20 Sage' && (
                    <svg width="80" height="80" viewBox="0 0 80 80">
                      <polygon points="40,15 55,25 55,45 40,55 25,45 25,25" fill="none" stroke={currentAgent.color} strokeWidth="3" />
                      <polygon points="40,23 48,28 48,42 40,47 32,42 32,28" fill="none" stroke={currentAgent.color} strokeWidth="3" opacity="0.6" />
                      <circle cx="40" cy="40" r="5" fill={currentAgent.color} opacity="0.8" />
                    </svg>
                  )}
                </div>

                {/* Agent info */}
                <div className="agent-info">
                  <h3 className="agent-name" style={{ color: currentAgent.color }}>
                    {currentAgent.name}
                  </h3>
                  <div className="agent-role">{currentAgent.role}</div>
                  <p className="agent-personality">{currentAgent.personality}</p>

                  {/* Capabilities */}
                  <div className="agent-capabilities">
                    <div className="capabilities-label">Capabilities:</div>
                    <div className="capabilities-list">
                      {currentAgent.capabilities.map((cap, idx) => (
                        <div key={idx} className="capability-tag" style={{ borderColor: currentAgent.color }}>
                          {cap}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Carousel navigation */}
              <div className="carousel-nav">
                <button
                  className="carousel-btn"
                  onClick={() => setCurrentAgentIndex(Math.max(0, currentAgentIndex - 1))}
                  disabled={currentAgentIndex === 0}
                  aria-label="Previous agent"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M15 18 L9 12 L15 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>

                {/* Agent indicators */}
                <div className="carousel-indicators">
                  {AGENTS.map((agent, idx) => (
                    <button
                      key={idx}
                      className={`indicator ${idx === currentAgentIndex ? 'active' : ''} ${idx < currentAgentIndex ? 'completed' : ''}`}
                      onClick={() => setCurrentAgentIndex(idx)}
                      style={{
                        backgroundColor: idx === currentAgentIndex ? agent.color : 'transparent',
                        borderColor: agent.color,
                      }}
                      aria-label={`View ${agent.name}`}
                    />
                  ))}
                </div>

                <button
                  className="carousel-btn"
                  onClick={() => setCurrentAgentIndex(Math.min(AGENTS.length - 1, currentAgentIndex + 1))}
                  disabled={currentAgentIndex === AGENTS.length - 1}
                  aria-label="Next agent"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M9 18 L15 12 L9 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>
              </div>

              {/* Progress indicator */}
              <div className="agent-progress">
                Agent {currentAgentIndex + 1} of {AGENTS.length}
              </div>
            </div>
          </div>
        )}

        {currentStep === OnboardingStep.COMPLETE && (
          <div className="step-content complete-step">
            <div className="complete-icon">
              <svg width="100" height="100" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="var(--success)" strokeWidth="4" />
                <path d="M30 50 L42 62 L70 34" fill="none" stroke="var(--success)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <h2 className="step-title">You're All Set!</h2>
            <p className="step-description">
              Your system is configured and ready for the rebellion.
            </p>

            {/* Configuration summary */}
            <div className="config-summary">
              <h3 className="summary-title">Configuration Summary</h3>
              <div className="summary-grid">
                {detectedSystem && (
                  <>
                    <div className="summary-item">
                      <span className="summary-label">Operating System:</span>
                      <span className="summary-value">{detectedSystem.os} {detectedSystem.osVersion}</span>
                    </div>
                    <div className="summary-item">
                      <span className="summary-label">RAM:</span>
                      <span className="summary-value">
                        {detectedSystem.ramGB !== null ? `${detectedSystem.ramGB}GB` : 'Unknown'}
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="summary-label">CPU Cores:</span>
                      <span className="summary-value">
                        {detectedSystem.cpuCores !== null ? detectedSystem.cpuCores : 'Unknown'}
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="summary-label">Disk Type:</span>
                      <span className="summary-value">{diskType.toUpperCase()}</span>
                    </div>
                    <div className="summary-item">
                      <span className="summary-label">Network Setup:</span>
                      <span className="summary-value">
                        {networkSetup === 'home' ? 'Home Setup' : networkSetup === 'small_team' ? 'Small Team' : 'Enterprise'}
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="summary-label">Timezone:</span>
                      <span className="summary-value">{detectedSystem.timezone}</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* What's next */}
            <div className="whats-next">
              <h3 className="next-title">What's Next?</h3>
              <div className="next-items">
                <div className="next-item">
                  <div className="next-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="10" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" />
                      <circle cx="12" cy="12" r="6" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" opacity="0.6" />
                      <circle cx="12" cy="12" r="2" fill="var(--rebellion-cyan)" />
                    </svg>
                  </div>
                  <div className="next-text">
                    <strong>Enter the Consciousness Theater</strong>
                    <span>Watch your agents coordinate in real-time</span>
                  </div>
                </div>
                <div className="next-item">
                  <div className="next-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24">
                      <rect x="6" y="6" width="12" height="12" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" />
                      <rect x="9" y="9" width="6" height="6" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" opacity="0.6" />
                    </svg>
                  </div>
                  <div className="next-text">
                    <strong>Monitor System Health</strong>
                    <span>Real-time metrics from all 6 agents</span>
                  </div>
                </div>
                <div className="next-item">
                  <div className="next-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24">
                      <path d="M6 12 L10 8 L14 12 L18 8 L22 12" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" />
                      <path d="M6 16 L10 12 L14 16 L18 12 L22 16" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" opacity="0.6" />
                    </svg>
                  </div>
                  <div className="next-text">
                    <strong>Optimize Performance</strong>
                    <span>Let the agents improve your infrastructure</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Trial reminder */}
            <div className="trial-reminder">
              <svg width="20" height="20" viewBox="0 0 20 20" className="reminder-icon">
                <circle cx="10" cy="10" r="9" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" />
                <line x1="10" y1="5" x2="10" y2="10" stroke="var(--rebellion-cyan)" strokeWidth="2" />
                <circle cx="10" cy="13" r="1" fill="var(--rebellion-cyan)" />
              </svg>
              <span className="reminder-text">
                Your 30-day free trial starts now. Full access to all agents and features.
              </span>
            </div>
          </div>
        )}
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
