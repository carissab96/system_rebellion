// src/types/auth.ts

// Shared User interface to avoid repetition
export interface User {
    token: any;
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    is_onboarded: boolean;
    company_name?: string;
    job_title?: string;
    created_at?: string;
    updated_at?: string;
    is_active?: boolean;
    system_name?: string;
    system_profile?: string;
    permissions_granted?: boolean;
    installation_method?: string;
      
  }
  
  // Base response with token
  export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User;
  }
  
  // All your auth responses can extend this base
  export interface LoginResponse extends AuthResponse {}
  export interface SignUpResponse extends AuthResponse {}
  export interface RefreshTokenResponse extends AuthResponse {}
  export interface ValidateTokenResponse extends AuthResponse {}
  
  // Simple responses
  export interface LogoutResponse {
    message: string;
    success: boolean;
  }
  
  export interface CSRFTokenResponse {
    csrf_token: string;
  }
  
  export interface ActivateProfileResponse {
    message: string;
    success: boolean;
  }
  
  // User creation responses
  export interface CreateUserResponse extends User {}
  export interface CreateProfileResponse extends User {
    email: string;
  }
  
  // Form data interfaces
  export interface LoginFormData {
    email: string;
    password: string;
    rememberMe: boolean;
  }
  
  export interface SignUpFormData {
    first_Name: string;
    last_name: string;
    email: string;
    password: string;
    confirmPassword: string;
    company_name: string;
    job_title: string;
  }
  
  // Error response interface
  export interface ApiError {
    detail: string;
    status_code: number;
    timestamp: string;
  }
  
  // Onboarding types
  export interface OnboardingFormData {
    systemName: string;
    operatingSystem: string;
    cpuCores: number;
    ramGB: number;
    storageGB: number;
    primaryUseCase: string;
    monitoringPreferences: {
      alertThreshold: string;
      reportFrequency: string;
      autoOptimization: boolean;
      realTimeAlerts: boolean;
    };
    agentPreferences: {
      hawkingtonSensitivity: string;
      snailAggressiveness: string;
      hamsterResponseLevel: string;
      stickComplianceLevel: string;
      qspNetworkFocus: string;
      vic20CoordinationMode: string;
    };
  }
  
  export interface OnboardingResponse {
    success: boolean;
    message: string;
    user: User;
  }