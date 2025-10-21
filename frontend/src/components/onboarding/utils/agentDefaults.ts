// components/onboarding/utils/agentDefaults.ts

/**
 * Interface representing all agent preferences that can be configured
 */
export interface AgentPreferences {
  // Hawkington agent preferences
  hawkington_triage_normal_threshold: number;
  hawkington_triage_medium_threshold: number;
  hawkington_triage_emergency_threshold: number;
  hawkington_message_frequency: number;
  hawkington_analysis_thoroughness: number;
  
  // Stick agent preferences
  stick_base_anxiety: number;
  stick_paper_bag_threshold: number;
  stick_bob_anxiety_multiplier: number;
  stick_compliance_strictness: number;
  stick_pattern_memory_depth: number;
  
  // Hamster agent preferences
  hamster_beer_optimal_level: number;
  hamster_disk_intervention_threshold: number;
  hamster_3am_activity_boost: number;
  hamster_carl_duct_tape_quality: number;
  hamster_bob_wildness_factor: number;
  
  // Snail agent preferences
  snail_caffeine_sensitivity: number;
  snail_optimization_aggression: number;
  snail_trail_intensity: number;
  
  // QSP (Quantum Shadow Person) preferences
  qsp_tequila_jello_tolerance: number;
  qsp_phase_shift_threshold: number;
  qsp_quantum_fix_confidence: number;
  qsp_comprehensibility: number;
  
  // VIC-20 agent preferences
  vic20_pattern_recognition_depth: number;
  vic20_mediation_patience: number;
  vic20_recommendation_confidence: number;
  
  // Cross-agent preferences
  agent_interaction_frequency: number;
  hamster_stick_proximity_alerts: number;
  cross_agent_memory_sharing: number;
}

export const defaultAgentPreferences: AgentPreferences = {
    hawkington_triage_normal_threshold: 30,
    hawkington_triage_medium_threshold: 65,
    hawkington_triage_emergency_threshold: 85,
    hawkington_message_frequency: 10,
    hawkington_analysis_thoroughness: 7,
    
    stick_base_anxiety: 25,
    stick_paper_bag_threshold: 60,
    stick_bob_anxiety_multiplier: 30,
    stick_compliance_strictness: 50,
    stick_pattern_memory_depth: 7,
    
    hamster_beer_optimal_level: 3,
    hamster_disk_intervention_threshold: 70,
    hamster_3am_activity_boost: 5,
    hamster_carl_duct_tape_quality: 5,
    hamster_bob_wildness_factor: 8,
    
    snail_caffeine_sensitivity: 5,
    snail_optimization_aggression: 5,
    snail_trail_intensity: 5,
    
    qsp_tequila_jello_tolerance: 5,
    qsp_phase_shift_threshold: 5,
    qsp_quantum_fix_confidence: 5,
    qsp_comprehensibility: 3,
    
    vic20_pattern_recognition_depth: 5,
    vic20_mediation_patience: 5,
    vic20_recommendation_confidence: 5,
    
    agent_interaction_frequency: 5,
    hamster_stick_proximity_alerts: 5,
    cross_agent_memory_sharing: 5
  };
  
  export const defaultMonitoringPreferences = {
    cpu_stress_weight: 25,
    memory_stress_weight: 35,
    disk_stress_weight: 40,
    cpu_compliance_threshold: 80,
    memory_compliance_threshold: 85,
    temperature_paranoia_threshold: 75,
    disk_cleanup_threshold: 70,
    disk_emergency_threshold: 90,
    fragmentation_threshold: 20,
    latency_gaming_threshold: 20,
    latency_streaming_threshold: 50,
    latency_critical_threshold: 5,
    packet_loss_intervention: 1,
    alert_frequency: 'balanced',
    enable_3am_operations: true,
    quantum_interventions_allowed: true,
    cross_agent_collaboration: true
  };
  
  export const adjustAgentDefaults = (systemProfile: any) => {
    const defaults = { ...defaultAgentPreferences };
    
    // Low RAM systems - less aggressive
    if (systemProfile.total_ram_gb <= 8) {
      defaults.snail_optimization_aggression = 3;
      defaults.hamster_3am_activity_boost = 3;
      defaults.stick_paper_bag_threshold = 70;
    }
    
    // HDD systems - different disk thresholds
    if (systemProfile.storage_type === 'hdd') {
      defaults.hamster_disk_intervention_threshold = 60;
      defaults.hamster_beer_optimal_level = 4;
    }
    
    // Enterprise/MDM systems - more conservative
    if (systemProfile.mdm_controlled || systemProfile.network_type === 'enterprise') {
      defaults.hawkington_triage_emergency_threshold = 90;
      defaults.hamster_bob_wildness_factor = 5;
      defaults.qsp_phase_shift_threshold = 7;
    }
    
    // Limited access systems - advisory mode
    if (systemProfile.admin_access === 'none' || systemProfile.admin_access === 'limited') {
      defaults.agent_interaction_frequency = 3;
      defaults.cross_agent_memory_sharing = 1;
    }
    
    return defaults;
  };
