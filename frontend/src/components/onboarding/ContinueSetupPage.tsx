/* eslint-disable react-hooks/exhaustive-deps */

// src/components/onboarding/ContinueSetupPage.tsx
import { useState, useEffect } from 'react'

import { useNavigate } from 'react-router-dom'

import apiService from '../../services/api'

export default function ContinueSetupPage() {
  const navigate = useNavigate()
  const [savedProgress, setSavedProgress] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fixed useEffect placement and dependencies
  useEffect(() => {
    loadSavedProgress()
  }, [])

  const loadSavedProgress = async () => {
    try {
      setLoading(true)
      const progress = await apiService.getOnboardingProgress()
      
      if (!progress || !progress.data.onboarding_progress) {
        // No saved progress, redirect to onboarding
        navigate('/onboarding', { replace: true })
        return
      }
      
      setSavedProgress(progress.data)
    } catch (err) {
      console.error('Error loading progress:', err)
      setError('Failed to load your saved progress')
    } finally {
      setLoading(false)
    }
  }

  // Fixed handleContinue syntax
  const handleContinue = () => {
    navigate('/onboarding', {
      state: { fromContinueSetupPage: true },
      replace: true 
    })
  }

  const handleStartFresh = async () => {
    try {
      await apiService.clearOnboardingProgress()
      navigate('/onboarding', {
        state: { fromContinueSetup: true },
        replace: true
      })
    } catch (err) {
      console.error('Error clearing progress:', err)
      setError('Failed to clear progress')
    }
  }

  const getProgressPercentage = () => {
    if (!savedProgress) return 0
    const currentStep = savedProgress.onboarding_progress || 0
    const totalSteps = 6
    return Math.round((currentStep / totalSteps) * 100)
  }

  const getStepName = (step: number) => {
    const stepNames = {
      1: 'Welcome & Introduction',
      2: 'System Detection', 
      3: 'Agent Selection',
      4: 'Preferences Setup',
      5: 'Final Configuration',
      6: 'Complete Setup'
    }
    return stepNames[step as keyof typeof stepNames] || `Step ${step}`
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <div className="vic20-text">Loading your progress...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="card max-w-md mx-auto">
          <div className="card-body text-center">
            <h2 className="card-title vic20-text text-error">Error</h2>
            <p className="mt-2">{error}</p>
            <button 
              onClick={() => navigate('/onboarding', { state: { fromContinueSetup: true } })}
              className="btn btn-primary mt-4"
            >
              Start Over
            </button>
          </div>
        </div>
      </div>
    )
  }

  const progressPercentage = getProgressPercentage()
  const currentStep = savedProgress?.onboarding_progress || 0
  const stepName = getStepName(currentStep)

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="card max-w-lg mx-auto">
        <header className="card-header text-center">
          <h1 className="card-title vic20-text">Welcome Back, Rebel!</h1>
          <p className="card-subtitle mt-1">Ready to continue your journey?</p>
        </header>

        <div className="card-body">
          <div className="mb-6">
            <div className="d-flex justify-between align-center mb-2">
              <span className="text-sm font-medium">Progress</span>
              <span className="text-sm font-medium">{progressPercentage}% Complete</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
          </div>

          <div className="alert alert-info mb-6">
            <div className="d-flex align-center gap-2">
              <span className="text-primary">●</span>
              <div>
                <strong>Continue where you left off:</strong>
                <div className="text-sm mt-1">{stepName}</div>
              </div>
            </div>
          </div>

          {savedProgress?.onboarding_data && (
            <div className="mb-6">
              <h3 className="text-sm font-medium mb-2">Your Saved Preferences:</h3>
              <div className="bg-base-200 p-3 rounded text-sm">
                {JSON.parse(savedProgress.onboarding_data).agentPreference && (
                  <div>Agent Preference: {JSON.parse(savedProgress.onboarding_data).agentPreference}</div>
                )}
              </div>
            </div>
          )}
        </div>

        <footer className="card-footer d-flex justify-between align-center">
          <button 
            onClick={handleStartFresh}
            className="btn btn-outline"
          >
            Start Fresh
          </button>
          <button 
            onClick={handleContinue}
            className="btn btn-primary"
          >
            Continue Setup
          </button>
        </footer>
      </div>
    </div>
  )
}