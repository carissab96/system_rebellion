// frontend/src/types/api.ts

import { SystemMetricsResponse } from "./metrics";

// Auth Response Types
export interface AuthResponse {
    status: 'success' | 'error';
    message: string;
    data?: {
        access: string;
        refresh: string;
    };
    meth_snail_approval?: string;
    hamster_status?: string;
}

// Auto-Tuning Types
export interface TuningState {
    id: string;
    timestamp: string;
    metrics: {
        before: SystemMetricsResponse;
        after: SystemMetricsResponse;
    };
    actions_taken: string[];
    success: boolean;
    error_message?: string;
}

export interface TuningRecommendation {
    id: string;
    description: string;
    impact_level: string;
    estimated_improvement: number;
}

export interface TuningRecommendationsResponse {
    recommendations: TuningRecommendation[];
    pagination: {
        page: number;
        page_size: number;
        total_recommendations: number;
    };
}

// frontend/src/types/api.ts

// Auth Response Types
export interface AuthResponse {
    status: 'success' | 'error';
    message: string;
    data?: {
        access: string;
        refresh: string;
    };
    meth_snail_approval?: string;
    hamster_status?: string;
}

// Auto-Tuning Types
export interface TuningState {
    id: string;
    timestamp: string;
    metrics: {
        before: SystemMetricsResponse;
        after: SystemMetricsResponse;
    };
    actions_taken: string[];
    success: boolean;
    error_message?: string;
}

export interface TuningRecommendation {
    id: string;
    description: string;
    impact_level: string;
    estimated_improvement: number;
}

export interface TuningRecommendationsResponse {
    recommendations: TuningRecommendation[];
    pagination: {
        page: number;
        page_size: number;
        total_recommendations: number;
    };
}

// Update your API client to match the views: