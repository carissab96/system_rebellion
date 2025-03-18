// frontend/src/types/models.ts

// Match your Django User model
export interface User {
    id: string;  // UUID
    system_id: string;  // UUID
    username: string;
    created_at: string;
    updated_at: string;
    optimization_preferences: Record<string, any>;
    is_active: boolean;
}

// Match UserProfile
export interface UserProfile {
    user: string;  // UUID reference
    operating_system: 'linux' | 'windows' | 'macos';
    os_version: string;
    linux_distro?: string;
    linux_distro_version?: string;
    cpu_cores?: number;
    total_memory?: number;  // in MB
    created_at: string;
    updated_at: string;
}

// Match SystemMetrics
export interface SystemMetric {
    id: string;  // UUID
    timestamp: string;
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_usage: number;
    process_count: number;
    additional_metrics?: Record<string, any>;
}

// Match OptimizationProfile
export interface OptimizationProfile {
    id: string;  // UUID
    user: string;  // UUID reference
    name: string;
    description?: string;
    settings: Record<string, any>;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

// Match SystemAlert
export enum AlertSeverity {
    LOW = 'LOW',
    MEDIUM = 'MEDIUM',
    HIGH = 'HIGH',
    CRITICAL = 'CRITICAL'
}

export interface SystemAlert {
    id: string;  // UUID
    user: string;  // UUID reference
    timestamp: string;
    title: string;
    message: string;
    severity: AlertSeverity;
    is_read: boolean;
    related_metrics?: Record<string, any>;
}

// State interfaces for Redux
export interface MetricsState {
    current: SystemMetric | null;
    historical: SystemMetric[];
    loading: boolean;
    error: string | null;
    lastUpdated: string | null;
}

export interface UserState {
    user: User | null;
    profile: UserProfile | null;
    loading: boolean;
    error: string | null;
}

export interface AlertState {
    alerts: SystemAlert[];
    loading: boolean;
    error: string | null;
}