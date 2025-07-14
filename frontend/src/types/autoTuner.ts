// src/types/autoTuner.ts
import { SystemMetric } from './metrics';
import { OptimizationProfile } from '../store/slices/optimizationSlice';

export interface TuningParameter {
  name: string;
  description: string;
  current_value: any;
  possible_values: any[];
}

export interface TuningRecommendation {
  parameter: string;
  current_value: any;
  recommended_value: any;
  confidence: number;
  impact_score: number;
  reason: string;
}

export interface SystemPattern {
  type: string;
  pattern: string;
  confidence: number;
  details: Record<string, any>;
}

export interface TuningResult {
  parameter: string;
  timestamp: string; // <-- Add this line
  success: boolean;
  value_before: string;
  value_after: string;
  metrics_before: SystemMetric;
  metrics_after: SystemMetric;
  error?: string;
}

export interface AutoTunerState {
  currentMetrics: SystemMetric | null;
  recommendations: TuningRecommendation[];
  patterns: SystemPattern[];
  tuningHistory: TuningResult[];
  activeProfile: OptimizationProfile | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
  lastUpdated: string | null;
}

export interface MetricsApiResponse {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_usage: number;
  process_count: number;
  additional?: Record<string, any>;
  timestamp: string;
}

export interface RecommendationsApiResponse {
  parameter: string;
  current_value: any;
  recommended_value: any;
  confidence: number;
  impact_score: number;
  reason: string;
}

export interface PatternsApiResponse {
  detected_patterns: SystemPattern[];
  pattern_summary: {
    total_patterns: number;
    pattern_types: Record<string, number>;
    latest_analysis: string;
  };
}

export interface TuningHistoryApiResponse {
  history: TuningResult[];
  active_tunings: Record<string, any>;
}

export interface ApplyProfileResponse {
  profile_id: string;
  profile_name: string;
  applied_settings: TuningResult[];
}

export interface ApplyRecommendationResponse {
  success: boolean;
  recommendation: {
    parameter: string;
    old_value: any;
    new_value: any;
    reason: string;
  };
  result: TuningResult;
}
