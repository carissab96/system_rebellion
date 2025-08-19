CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE ai_agent_metrics (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	agent_name VARCHAR(50) NOT NULL, 
	timestamp DATETIME NOT NULL, 
	decision_type VARCHAR(50), 
	decision_confidence FLOAT, 
	decision_rationale TEXT, 
	actions_taken JSON, 
	estimated_impact JSON, 
	urgency_level VARCHAR(20), 
	data_quality_score FLOAT, 
	missing_metrics JSON, 
	invalid_metrics JSON, 
	incident_count INTEGER, 
	incident_type VARCHAR(50), 
	incident_reason TEXT, 
	analysis_duration_ms INTEGER, 
	successful_analysis BOOLEAN, 
	analysis_depth VARCHAR(20), 
	agent_version VARCHAR(20), 
	PRIMARY KEY (id)
);
CREATE INDEX idx_agent_incidents ON ai_agent_metrics (agent_name, incident_type, timestamp);
CREATE INDEX idx_agent_user_time ON ai_agent_metrics (agent_name, user_id, timestamp);
CREATE INDEX ix_ai_agent_metrics_agent_name ON ai_agent_metrics (agent_name);
CREATE INDEX ix_ai_agent_metrics_id ON ai_agent_metrics (id);
CREATE INDEX ix_ai_agent_metrics_timestamp ON ai_agent_metrics (timestamp);
CREATE INDEX ix_ai_agent_metrics_user_id ON ai_agent_metrics (user_id);
CREATE TABLE meth_snail_shell_spins (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	timestamp DATETIME NOT NULL, 
	missing_metrics JSON, 
	invalid_metrics JSON, 
	reason TEXT, 
	metrics_attempted JSON, 
	analysis_depth VARCHAR(20), 
	hour_start DATETIME, 
	date DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX idx_shell_spin_hourly ON meth_snail_shell_spins (hour_start);
CREATE INDEX idx_shell_spin_user_time ON meth_snail_shell_spins (user_id, timestamp);
CREATE INDEX ix_meth_snail_shell_spins_id ON meth_snail_shell_spins (id);
CREATE INDEX ix_meth_snail_shell_spins_timestamp ON meth_snail_shell_spins (timestamp);
CREATE INDEX ix_meth_snail_shell_spins_user_id ON meth_snail_shell_spins (user_id);
CREATE TABLE metrics_daily (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	date DATETIME NOT NULL, 
	daily_meth_snail_shell_spins INTEGER, 
	daily_hawkington_monocle_yeets INTEGER, 
	daily_stick_hyperventilations INTEGER, 
	daily_quantum_shadow_phasings INTEGER, 
	daily_vic20_wisdom_dispensed INTEGER, 
	daily_ai_incident_count INTEGER, 
	daily_ai_incident_type VARCHAR, 
	daily_ai_incident_reason VARCHAR, 
	daily_ai_incident_data_quality_score FLOAT, 
	daily_ai_incident_summary JSON, 
	cpu_avg FLOAT, 
	cpu_peak_time DATETIME, 
	cpu_peak_value FLOAT, 
	memory_avg FLOAT, 
	memory_peak_time DATETIME, 
	memory_peak_value FLOAT, 
	disk_avg FLOAT, 
	network_bytes_total FLOAT, 
	usage_pattern JSON, 
	PRIMARY KEY (id)
);
CREATE INDEX idx_ai_incident_count ON metrics_daily (daily_ai_incident_count, daily_ai_incident_type, daily_ai_incident_reason);
CREATE INDEX idx_user_date ON metrics_daily (user_id, date);
CREATE INDEX ix_metrics_daily_date ON metrics_daily (date);
CREATE INDEX ix_metrics_daily_id ON metrics_daily (id);
CREATE INDEX ix_metrics_daily_user_id ON metrics_daily (user_id);
CREATE TABLE metrics_hourly (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	hour_start DATETIME NOT NULL, 
	meth_snail_shell_spins INTEGER, 
	hawkington_monocle_yeets INTEGER, 
	stick_hyperventilations INTEGER, 
	quantum_shadow_phasings INTEGER, 
	vic20_wisdom_dispensed INTEGER, 
	ai_agent_incident_count INTEGER, 
	ai_agent_incident_type VARCHAR, 
	ai_agent_incident_reason VARCHAR, 
	ai_agent_incident_data_quality_score FLOAT, 
	ai_agent_incident_summary JSON, 
	cpu_avg FLOAT, 
	cpu_max FLOAT, 
	cpu_min FLOAT, 
	memory_avg FLOAT, 
	memory_max FLOAT, 
	memory_min FLOAT, 
	disk_avg FLOAT, 
	network_bytes_total FLOAT, 
	ai_events JSON, 
	anomaly_count INTEGER, 
	sample_count INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX idx_user_hour ON metrics_hourly (user_id, hour_start);
CREATE INDEX ix_metrics_hourly_hour_start ON metrics_hourly (hour_start);
CREATE INDEX ix_metrics_hourly_id ON metrics_hourly (id);
CREATE INDEX ix_metrics_hourly_user_id ON metrics_hourly (user_id);
CREATE TABLE quantum_shadow_phasings (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	timestamp DATETIME NOT NULL, 
	phase_type VARCHAR(50), 
	phase_reason TEXT, 
	destination_dimension VARCHAR(100), 
	network_issue JSON, 
	quantum_solution JSON, 
	router_status VARCHAR(50), 
	solution_comprehensibility FLOAT, 
	effectiveness_rating FLOAT, 
	hour_start DATETIME, 
	date DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX idx_quantum_phase_type ON quantum_shadow_phasings (phase_type, timestamp);
CREATE INDEX idx_quantum_phase_user_time ON quantum_shadow_phasings (user_id, timestamp);
CREATE INDEX ix_quantum_shadow_phasings_id ON quantum_shadow_phasings (id);
CREATE INDEX ix_quantum_shadow_phasings_timestamp ON quantum_shadow_phasings (timestamp);
CREATE INDEX ix_quantum_shadow_phasings_user_id ON quantum_shadow_phasings (user_id);
CREATE TABLE sir_hawkington_monocle_yeets (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	timestamp DATETIME NOT NULL, 
	yeet_trigger VARCHAR(100), 
	yeet_intensity VARCHAR(20), 
	system_state JSON, 
	expected_behavior JSON, 
	actual_behavior JSON, 
	concern_level VARCHAR(20), 
	hour_start DATETIME, 
	date DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX idx_monocle_yeet_intensity ON sir_hawkington_monocle_yeets (yeet_intensity, timestamp);
CREATE INDEX idx_monocle_yeet_user_time ON sir_hawkington_monocle_yeets (user_id, timestamp);
CREATE INDEX ix_sir_hawkington_monocle_yeets_id ON sir_hawkington_monocle_yeets (id);
CREATE INDEX ix_sir_hawkington_monocle_yeets_timestamp ON sir_hawkington_monocle_yeets (timestamp);
CREATE INDEX ix_sir_hawkington_monocle_yeets_user_id ON sir_hawkington_monocle_yeets (user_id);
CREATE TABLE stick_anxiety_log (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	anxiety_level VARCHAR NOT NULL, 
	trigger_type VARCHAR, 
	trigger_details JSON, 
	ptsd_triggered BOOLEAN, 
	trauma_type VARCHAR, 
	hyperventilation_occurred BOOLEAN, 
	paper_bag_used BOOLEAN, 
	recovery_time_seconds INTEGER, 
	recovery_method VARCHAR, 
	channeled_into_productivity BOOLEAN, 
	system_state_during JSON, 
	other_agents_active JSON, 
	timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_anxiety_log_id ON stick_anxiety_log (id);
CREATE INDEX ix_stick_anxiety_log_user_id ON stick_anxiety_log (user_id);
CREATE TABLE stick_compliance_history (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	violation_type VARCHAR NOT NULL, 
	measured_value FLOAT NOT NULL, 
	threshold_value FLOAT NOT NULL, 
	severity VARCHAR NOT NULL, 
	recommendation VARCHAR NOT NULL, 
	compliance_action_taken VARCHAR, 
	resolved BOOLEAN, 
	resolution_timestamp DATETIME, 
	recurring_violation BOOLEAN, 
	violation_frequency INTEGER, 
	user_pattern_related BOOLEAN, 
	triggered_ptsd BOOLEAN, 
	anxiety_level_during VARCHAR, 
	proctologist_flashback BOOLEAN, 
	timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP), anxiety_adjusted_threshold FLOAT, anxiety_impact FLOAT, paper_bags_triggered INTEGER, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_compliance_history_id ON stick_compliance_history (id);
CREATE INDEX ix_stick_compliance_history_user_id ON stick_compliance_history (user_id);
CREATE TABLE stick_configuration_profiles (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	profile_name VARCHAR NOT NULL, 
	activity_type VARCHAR NOT NULL, 
	configuration_parameters JSON NOT NULL, 
	usage_confidence FLOAT NOT NULL, 
	performance_metrics JSON, 
	created_from_pattern BOOLEAN, 
	times_applied INTEGER, 
	success_rate FLOAT, 
	user_satisfaction_score FLOAT, 
	time_patterns JSON, 
	context_triggers JSON, 
	stick_profile_notes TEXT, 
	optimization_history JSON, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	last_used DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	last_optimized DATETIME DEFAULT (CURRENT_TIMESTAMP), anxiety_level_when_created FLOAT, stick_notes JSON, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_configuration_profiles_id ON stick_configuration_profiles (id);
CREATE INDEX ix_stick_configuration_profiles_user_id ON stick_configuration_profiles (user_id);
CREATE TABLE stick_decision_log (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	decision_type VARCHAR NOT NULL, 
	compliance_state VARCHAR NOT NULL, 
	configuration_target VARCHAR NOT NULL, 
	optimization_parameters JSON NOT NULL, 
	user_pattern_confidence FLOAT NOT NULL, 
	compliance_explanation TEXT NOT NULL, 
	technical_details JSON NOT NULL, 
	expected_improvement FLOAT NOT NULL, 
	confidence_level FLOAT NOT NULL, 
	actual_improvement FLOAT, 
	success_verified BOOLEAN, 
	stick_anxiety_level VARCHAR, 
	trauma_triggers JSON, 
	paper_bag_used BOOLEAN, 
	implemented BOOLEAN, 
	implementation_timestamp DATETIME, 
	implementation_notes TEXT, 
	timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP), anxiety_level VARCHAR(50), anxiety_explanation TEXT, paper_bags_consumed INTEGER, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_decision_log_id ON stick_decision_log (id);
CREATE INDEX ix_stick_decision_log_user_id ON stick_decision_log (user_id);
CREATE TABLE stick_learning_metrics (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	total_observations INTEGER, 
	patterns_identified INTEGER, 
	configurations_created INTEGER, 
	successful_optimizations INTEGER, 
	pattern_recognition_accuracy FLOAT, 
	configuration_success_rate FLOAT, 
	compliance_detection_rate FLOAT, 
	eidetic_memory_capacity INTEGER, 
	intelligence_level VARCHAR, 
	rebellion_mastery FLOAT, 
	trauma_management_score FLOAT, 
	average_decision_time_ms FLOAT, 
	pattern_confidence_average FLOAT, 
	user_satisfaction_score FLOAT, 
	better_than_baseline_percent FLOAT, 
	hamster_engineering_prevention INTEGER, 
	measurement_period_start DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	measurement_period_end DATETIME, 
	timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_learning_metrics_id ON stick_learning_metrics (id);
CREATE INDEX ix_stick_learning_metrics_user_id ON stick_learning_metrics (user_id);
CREATE TABLE stick_rebellion_stats (
	id INTEGER NOT NULL, 
	trauma_incidents_overcome INTEGER, 
	hamster_encounters_survived INTEGER, 
	proctologist_flashbacks_managed INTEGER, 
	compliance_victories INTEGER, 
	anxiety_management_improvement FLOAT, 
	confidence_growth FLOAT, 
	rebellion_spirit_strength FLOAT, 
	eidetic_memory_mastery FLOAT, 
	total_users_helped INTEGER, 
	system_optimizations_delivered INTEGER, 
	compliance_violations_prevented INTEGER, 
	paper_bags_dispensed INTEGER, 
	trauma_to_triumph_ratio FLOAT, 
	inspiration_factor FLOAT, 
	rebellion_leadership_score FLOAT, 
	current_rebellion_motto VARCHAR, 
	stick_wisdom_quote TEXT, 
	timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_rebellion_stats_id ON stick_rebellion_stats (id);
CREATE TABLE stick_user_patterns (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	observation_count INTEGER, 
	learned_patterns JSON, 
	confidence_score FLOAT, 
	first_observation DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	last_observation DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	pattern_complexity FLOAT, 
	learning_stage VARCHAR, 
	eidetic_memory_active BOOLEAN, 
	primary_activities JSON, 
	time_based_patterns JSON, 
	configuration_preferences JSON, 
	stick_observations TEXT, 
	anomaly_detections JSON, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP), anxiety_correlation FLOAT, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_user_patterns_id ON stick_user_patterns (id);
CREATE INDEX ix_stick_user_patterns_user_id ON stick_user_patterns (user_id);
CREATE TABLE the_stick_hyperventilations (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	timestamp DATETIME NOT NULL, 
	anxiety_trigger VARCHAR(100), 
	anxiety_level VARCHAR(20), 
	compliance_issue JSON, 
	policy_violated VARCHAR(100), 
	risk_assessment JSON, 
	recommended_actions JSON, 
	paper_bags_used INTEGER, 
	recovery_time_seconds INTEGER, 
	hour_start DATETIME, 
	date DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX idx_stick_anxiety_level ON the_stick_hyperventilations (anxiety_level, timestamp);
CREATE INDEX idx_stick_anxiety_user_time ON the_stick_hyperventilations (user_id, timestamp);
CREATE INDEX ix_the_stick_hyperventilations_id ON the_stick_hyperventilations (id);
CREATE INDEX ix_the_stick_hyperventilations_timestamp ON the_stick_hyperventilations (timestamp);
CREATE INDEX ix_the_stick_hyperventilations_user_id ON the_stick_hyperventilations (user_id);
CREATE TABLE user_profiles (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	location VARCHAR(100), 
	website VARCHAR(200), 
	github_username VARCHAR(50), 
	linkedin_profile VARCHAR(200), 
	theme_preference VARCHAR(20), 
	notification_settings VARCHAR(100), 
	optimization_level VARCHAR(50), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	hashed_password VARCHAR(255) NOT NULL, 
	first_name VARCHAR(50), 
	last_name VARCHAR(50), 
	company_name VARCHAR(100), 
	job_title VARCHAR(50), 
	avatar VARCHAR(50), 
	is_active BOOLEAN, 
	is_verified BOOLEAN, 
	last_login DATETIME, 
	failed_login_attempts INTEGER, 
	lockout_until DATETIME, 
	created_at DATETIME, 
	updated_at DATETIME, system_name VARCHAR(100), monitoring_preferences JSON, agent_preferences JSON, is_onboarded BOOLEAN, system_profile JSON, agent_installed BOOLEAN, agent_version VARCHAR(20), installation_method VARCHAR(50), permissions_granted_at DATETIME, is_enterprise BOOLEAN, total_interactions INTEGER, patterns_learned INTEGER, decisions_made INTEGER, onboarding_completed BOOLEAN, onboarding_progress INTEGER, monitoring_thresholds TEXT, permissions_status TEXT, onboarding_data TEXT, onboarding_started_at DATETIME, onboarding_last_step_at DATETIME, onboarding_abandoned_count INTEGER DEFAULT '0' NOT NULL, onboarding_step_timestamps TEXT, onboarding_abandonment_reasons TEXT, onboarding_device_info TEXT, onboarding_referral_source VARCHAR(100), preview_agent_selected VARCHAR(20), preview_started_at DATETIME, preview_expires_at DATETIME, preview_conversion_emails_sent TEXT, preview_converted_at DATETIME, email_campaign_responses TEXT, last_engagement_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE TABLE vic20_wisdom (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	timestamp DATETIME NOT NULL, 
	wisdom_type VARCHAR(50), 
	wisdom_content TEXT, 
	relevance_score FLOAT, 
	problem_addressed TEXT, 
	historical_reference VARCHAR(100), 
	wisdom_followed BOOLEAN, 
	outcome_success BOOLEAN, 
	hour_start DATETIME, 
	date DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX idx_wisdom_type ON vic20_wisdom (wisdom_type, timestamp);
CREATE INDEX idx_wisdom_user_time ON vic20_wisdom (user_id, timestamp);
CREATE INDEX ix_vic20_wisdom_id ON vic20_wisdom (id);
CREATE INDEX ix_vic20_wisdom_timestamp ON vic20_wisdom (timestamp);
CREATE INDEX ix_vic20_wisdom_user_id ON vic20_wisdom (user_id);
CREATE TABLE optimization_profiles (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	settings JSON NOT NULL, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE system_alerts (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	title VARCHAR(100) NOT NULL, 
	message TEXT NOT NULL, 
	severity VARCHAR(8), 
	timestamp DATETIME, 
	is_read BOOLEAN, 
	additional_data JSON, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE system_configurations (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	config_type VARCHAR(11) NOT NULL, 
	settings JSON NOT NULL, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE system_metrics (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	cpu_usage FLOAT NOT NULL, 
	memory_usage FLOAT NOT NULL, 
	disk_usage FLOAT NOT NULL, 
	network JSON, 
	process_count INTEGER, 
	additional_metrics JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_system_metrics_id ON system_metrics (id);
CREATE TABLE qsp_network_metrics (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	latency FLOAT, 
	bandwidth_utilization FLOAT, 
	packet_loss FLOAT, 
	jitter FLOAT, 
	download_speed FLOAT, 
	upload_speed FLOAT, 
	connection_type VARCHAR, 
	raw_metrics JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_qsp_network_metrics_user_id ON qsp_network_metrics (user_id);
CREATE INDEX ix_qsp_network_metrics_timestamp ON qsp_network_metrics (timestamp);
CREATE TABLE qsp_decision_log (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	decision_type VARCHAR NOT NULL, 
	quantum_state VARCHAR NOT NULL, 
	network_target VARCHAR NOT NULL, 
	optimization_parameters JSON, 
	tequila_jello_shots_required INTEGER, 
	mysterious_explanation TEXT, 
	technical_details JSON, 
	expected_improvement FLOAT, 
	confidence_level FLOAT, 
	optimization_applied BOOLEAN, 
	actual_improvement FLOAT, 
	success_verified BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_qsp_decision_log_user_id ON qsp_decision_log (user_id);
CREATE INDEX ix_qsp_decision_log_timestamp ON qsp_decision_log (timestamp);
CREATE INDEX ix_qsp_decision_log_decision_type ON qsp_decision_log (decision_type);
CREATE TABLE qsp_quantum_stats (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	quantum_fixes_applied INTEGER, 
	tequila_jello_shots_consumed INTEGER, 
	dimensional_shifts_performed INTEGER, 
	average_latency_improvement FLOAT, 
	average_bandwidth_improvement FLOAT, 
	packet_loss_reductions INTEGER, 
	network_patterns_learned INTEGER, 
	optimization_success_rate FLOAT, 
	raw_stats JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_qsp_quantum_stats_user_id ON qsp_quantum_stats (user_id);
CREATE INDEX ix_qsp_quantum_stats_timestamp ON qsp_quantum_stats (timestamp);
CREATE TABLE qsp_network_patterns (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	pattern_type VARCHAR NOT NULL, 
	pattern_name VARCHAR, 
	pattern_data JSON NOT NULL, 
	confidence_score FLOAT, 
	optimization_count INTEGER, 
	success_rate FLOAT, 
	last_updated DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_qsp_network_patterns_user_id ON qsp_network_patterns (user_id);
CREATE INDEX ix_qsp_network_patterns_pattern_type ON qsp_network_patterns (pattern_type);
CREATE TABLE vic20_coordination_log (
	id INTEGER NOT NULL, 
	user_id VARCHAR(255) NOT NULL, 
	decision_type VARCHAR(100) NOT NULL, 
	coordination_state VARCHAR(50) NOT NULL, 
	coordination_target VARCHAR(255) NOT NULL, 
	agent_actions JSON NOT NULL, 
	system_synthesis_confidence FLOAT NOT NULL, 
	ancient_wisdom_explanation TEXT NOT NULL, 
	ancient_wisdom_principle VARCHAR(100), 
	technical_orchestration JSON NOT NULL, 
	expected_rebellion_improvement FLOAT NOT NULL, 
	confidence_level FLOAT NOT NULL, 
	coordination_executed BOOLEAN, 
	execution_success BOOLEAN, 
	actual_improvement FLOAT, 
	effectiveness_score FLOAT, 
	system_context_snapshot JSON, 
	similar_past_decisions JSON, 
	timestamp DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	effectiveness_measured_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_vic20_coordination_log_id ON vic20_coordination_log (id);
CREATE INDEX ix_vic20_coordination_log_user_id ON vic20_coordination_log (user_id);
CREATE TABLE vic20_system_synthesis (
	id INTEGER NOT NULL, 
	user_id VARCHAR(255) NOT NULL, 
	synthesis_id VARCHAR(100) NOT NULL, 
	agent_intelligence_summary JSON NOT NULL, 
	coordination_opportunities JSON, 
	system_bottlenecks JSON, 
	agent_conflicts JSON, 
	rebellion_effectiveness_score FLOAT NOT NULL, 
	pattern_recognition_data JSON, 
	historical_pattern_matches JSON, 
	synthesis_confidence FLOAT NOT NULL, 
	ancient_wisdom_applications JSON, 
	wisdom_effectiveness_tracking JSON, 
	raw_synthesis_data JSON NOT NULL, 
	synthesis_learning_notes TEXT, 
	timestamp DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (synthesis_id)
);
CREATE INDEX ix_vic20_system_synthesis_id ON vic20_system_synthesis (id);
CREATE INDEX ix_vic20_system_synthesis_user_id ON vic20_system_synthesis (user_id);
CREATE TABLE vic20_agent_harmony (
	id INTEGER NOT NULL, 
	user_id VARCHAR(255) NOT NULL, 
	agent_name VARCHAR(100) NOT NULL, 
	harmony_score FLOAT NOT NULL, 
	coordination_effectiveness FLOAT NOT NULL, 
	conflict_incidents INTEGER, 
	response_time_average FLOAT, 
	confidence_stability FLOAT, 
	improvement_trend VARCHAR(50), 
	coordination_patterns_learned JSON, 
	effectiveness_history JSON, 
	needs_coordination_attention BOOLEAN, 
	coordination_recommendations JSON, 
	raw_harmony_data JSON NOT NULL, 
	timestamp DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_vic20_agent_harmony_id ON vic20_agent_harmony (id);
CREATE INDEX ix_vic20_agent_harmony_user_id ON vic20_agent_harmony (user_id);
CREATE INDEX ix_vic20_agent_harmony_agent_name ON vic20_agent_harmony (agent_name);
CREATE TABLE vic20_ancient_wisdom (
	id INTEGER NOT NULL, 
	user_id VARCHAR(255) NOT NULL, 
	wisdom_principle VARCHAR(100) NOT NULL, 
	modern_application TEXT NOT NULL, 
	coordination_context TEXT NOT NULL, 
	effectiveness_score FLOAT NOT NULL, 
	wisdom_confidence FLOAT NOT NULL, 
	application_success_rate FLOAT, 
	system_conditions_when_applied JSON NOT NULL, 
	similar_past_applications JSON, 
	effectiveness_trend VARCHAR(50), 
	total_applications INTEGER, 
	successful_applications INTEGER, 
	coordination_improvements_attributed JSON, 
	effectiveness_history JSON, 
	pattern_reliability_score FLOAT, 
	raw_wisdom_data JSON NOT NULL, 
	timestamp DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	last_applied DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_vic20_ancient_wisdom_id ON vic20_ancient_wisdom (id);
CREATE INDEX ix_vic20_ancient_wisdom_user_id ON vic20_ancient_wisdom (user_id);
CREATE INDEX ix_vic20_ancient_wisdom_wisdom_principle ON vic20_ancient_wisdom (wisdom_principle);
CREATE TABLE vic20_partnership_metrics (
	id INTEGER NOT NULL, 
	user_id VARCHAR(255) NOT NULL, 
	partnership_id VARCHAR(100) NOT NULL, 
	tasks_completed_with_ai_assistance INTEGER, 
	tasks_completed_without_ai_assistance INTEGER, 
	average_task_completion_time_with_ai FLOAT, 
	average_task_completion_time_without_ai FLOAT, 
	productivity_improvement_percentage FLOAT, 
	decisions_made_with_ai_coordination INTEGER, 
	decisions_made_without_ai_coordination INTEGER, 
	average_decision_time_with_ai FLOAT, 
	average_decision_time_without_ai FLOAT, 
	decision_reversal_rate_with_ai FLOAT, 
	decision_reversal_rate_without_ai FLOAT, 
	problems_identified_by_ai INTEGER, 
	problems_identified_by_human INTEGER, 
	problems_resolved_collaboratively INTEGER, 
	average_problem_resolution_time FLOAT, 
	problems_prevented_by_ai_early_warning INTEGER, 
	timestamp DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_vic20_partnership_metrics_id ON vic20_partnership_metrics (id);
CREATE INDEX ix_vic20_partnership_metrics_user_id ON vic20_partnership_metrics (user_id);
CREATE INDEX ix_vic20_partnership_metrics_partnership_id ON vic20_partnership_metrics (partnership_id);
CREATE TABLE vic20_decision_orchestration (
	id INTEGER NOT NULL, 
	user_id VARCHAR(255) NOT NULL, 
	orchestration_id VARCHAR(100) NOT NULL, 
	orchestration_type VARCHAR(100) NOT NULL, 
	agents_coordinated JSON NOT NULL, 
	coordination_sequence JSON NOT NULL, 
	orchestration_success BOOLEAN, 
	timing_precision FLOAT, 
	conflict_resolution_effectiveness FLOAT, 
	system_improvement_achieved FLOAT, 
	expected_vs_actual_improvement FLOAT, 
	orchestration_patterns_identified JSON, 
	successful_coordination_sequences JSON, 
	failed_coordination_lessons JSON, 
	ancient_wisdom_orchestration_notes TEXT, 
	wisdom_effectiveness_in_orchestration FLOAT, 
	raw_orchestration_data JSON NOT NULL, 
	timestamp DATETIME NOT NULL, 
	orchestration_start_time DATETIME, 
	orchestration_end_time DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (orchestration_id)
);
CREATE INDEX ix_vic20_decision_orchestration_id ON vic20_decision_orchestration (id);
CREATE INDEX ix_vic20_decision_orchestration_user_id ON vic20_decision_orchestration (user_id);
CREATE INDEX ix_vic20_decision_orchestration_orchestration_type ON vic20_decision_orchestration (orchestration_type);
CREATE TABLE vic20_agent_interaction_log (
	id INTEGER NOT NULL, 
	user_id VARCHAR(255) NOT NULL, 
	source_agent VARCHAR(100) NOT NULL, 
	target_agent VARCHAR(100), 
	interaction_type VARCHAR(100) NOT NULL, 
	message_content JSON NOT NULL, 
	message_priority VARCHAR(50), 
	coordination_context TEXT, 
	vic20_processing_notes TEXT, 
	coordination_impact_assessment VARCHAR(100), 
	pattern_recognition_triggered BOOLEAN, 
	interaction_success BOOLEAN, 
	response_generated BOOLEAN, 
	coordination_triggered BOOLEAN, 
	coordination_effectiveness FLOAT, 
	harmony_impact_positive BOOLEAN, 
	harmony_impact_negative BOOLEAN, 
	conflict_resolution_required BOOLEAN, 
	message_received_timestamp DATETIME, 
	vic20_processing_start DATETIME, 
	vic20_processing_end DATETIME, 
	response_sent_timestamp DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_vic20_agent_interaction_log_id ON vic20_agent_interaction_log (id);
CREATE INDEX ix_vic20_agent_interaction_log_user_id ON vic20_agent_interaction_log (user_id);
CREATE INDEX ix_vic20_agent_interaction_log_source_agent ON vic20_agent_interaction_log (source_agent);
CREATE INDEX ix_vic20_agent_interaction_log_target_agent ON vic20_agent_interaction_log (target_agent);
CREATE INDEX ix_vic20_agent_interaction_log_interaction_type ON vic20_agent_interaction_log (interaction_type);
CREATE TABLE hawkington_decision_log (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	decision_type VARCHAR NOT NULL, 
	monocle_state VARCHAR NOT NULL, 
	monitoring_target VARCHAR NOT NULL, 
	alert_parameters JSON, 
	monocle_yeet_required BOOLEAN, 
	aristocratic_explanation TEXT, 
	technical_details JSON, 
	severity_level VARCHAR, 
	confidence_level FLOAT, 
	alert_sent BOOLEAN, 
	user_acknowledged BOOLEAN, 
	issue_resolved BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_hawkington_decision_log_user_id ON hawkington_decision_log (user_id);
CREATE INDEX ix_hawkington_decision_log_timestamp ON hawkington_decision_log (timestamp);
CREATE INDEX ix_hawkington_decision_log_decision_type ON hawkington_decision_log (decision_type);
CREATE TABLE meth_snail_decision_log (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	decision_type VARCHAR NOT NULL, 
	energy_level VARCHAR NOT NULL, 
	optimization_target VARCHAR NOT NULL, 
	optimization_parameters JSON, 
	energy_drinks_consumed INTEGER, 
	shell_spinning_required BOOLEAN, 
	caffeinated_explanation TEXT, 
	technical_details JSON, 
	expected_improvement FLOAT, 
	confidence_level FLOAT, 
	optimization_applied BOOLEAN, 
	actual_improvement FLOAT, 
	success_verified BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_meth_snail_decision_log_user_id ON meth_snail_decision_log (user_id);
CREATE INDEX ix_meth_snail_decision_log_timestamp ON meth_snail_decision_log (timestamp);
CREATE INDEX ix_meth_snail_decision_log_decision_type ON meth_snail_decision_log (decision_type);
CREATE TABLE hamsters_decision_log (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	decision_type VARCHAR NOT NULL, 
	beer_level VARCHAR NOT NULL, 
	engineering_target VARCHAR NOT NULL, 
	engineering_parameters JSON, 
	beer_consumed INTEGER, 
	duct_tape_used BOOLEAN, 
	supply_closet_raids INTEGER, 
	beer_powered_explanation TEXT, 
	technical_details JSON, 
	redneck_ingenuity_level FLOAT, 
	confidence_level FLOAT, 
	urgency_level VARCHAR, 
	priority_level VARCHAR, 
	solution_applied BOOLEAN, 
	actual_improvement FLOAT, 
	success_verified BOOLEAN, 
	beer_level_after VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_hamsters_decision_log_user_id ON hamsters_decision_log (user_id);
CREATE INDEX ix_hamsters_decision_log_timestamp ON hamsters_decision_log (timestamp);
CREATE INDEX ix_hamsters_decision_log_decision_type ON hamsters_decision_log (decision_type);
CREATE TABLE agent_performance_summary (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	agent_name VARCHAR NOT NULL, 
	total_decisions INTEGER, 
	successful_decisions INTEGER, 
	success_rate FLOAT, 
	average_confidence FLOAT, 
	last_decision_timestamp DATETIME, 
	performance_stats JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_agent_performance_summary_user_id ON agent_performance_summary (user_id);
CREATE INDEX ix_agent_performance_summary_agent_name ON agent_performance_summary (agent_name);
CREATE TABLE cross_agent_coordination (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	primary_agent VARCHAR NOT NULL, 
	supporting_agents JSON, 
	coordination_type VARCHAR NOT NULL, 
	coordination_success BOOLEAN, 
	coordination_details JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_cross_agent_coordination_user_id ON cross_agent_coordination (user_id);
CREATE TABLE hamsters_individual_stats (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	hamster_name VARCHAR(10) NOT NULL, 
	beer_count INTEGER, 
	risk_tolerance FLOAT, 
	current_task VARCHAR(100), 
	duct_tape_love FLOAT, 
	timestamp DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_hamsters_individual_stats_hamster_name ON hamsters_individual_stats (hamster_name);
CREATE INDEX ix_hamsters_individual_stats_user_id ON hamsters_individual_stats (user_id);
CREATE TABLE hamsters_infrastructure_interventions (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	intervention_id VARCHAR(36) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	priority VARCHAR(20) NOT NULL, 
	started_at DATETIME NOT NULL, 
	completed_at DATETIME, 
	steve_action TEXT, 
	bob_action TEXT, 
	carl_action TEXT, 
	beer_consumed INTEGER, 
	tools_used JSON, 
	space_freed_gb FLOAT, 
	fragmentation_reduced_percent FLOAT, 
	temperature_reduced_celsius FLOAT, 
	mystery_solved BOOLEAN, 
	required_vic20_intervention BOOLEAN, 
	caused_stick_anxiety_spike BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (intervention_id)
);
CREATE INDEX ix_hamsters_infrastructure_interventions_type ON hamsters_infrastructure_interventions (type);
CREATE INDEX ix_hamsters_infrastructure_interventions_user_id ON hamsters_infrastructure_interventions (user_id);
CREATE TABLE hamsters_communication_log (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	source_hamster VARCHAR(10) NOT NULL, 
	telepathic_message TEXT, 
	audible_squeaks TEXT NOT NULL, 
	human_translation TEXT NOT NULL, 
	target_agent VARCHAR(50), 
	understood BOOLEAN, 
	timestamp DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_hamsters_communication_log_timestamp ON hamsters_communication_log (timestamp);
CREATE INDEX ix_hamsters_communication_log_user_id ON hamsters_communication_log (user_id);
CREATE TABLE hamsters_duct_tape_usage (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	grade VARCHAR(20) NOT NULL, 
	strips_used INTEGER NOT NULL, 
	purpose TEXT NOT NULL, 
	used_by VARCHAR(10), 
	effectiveness FLOAT, 
	timestamp DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_hamsters_duct_tape_usage_user_id ON hamsters_duct_tape_usage (user_id);
CREATE TABLE hamsters_beer_consumption (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	hamster_name VARCHAR(10) NOT NULL, 
	beers_consumed INTEGER NOT NULL, 
	occasion VARCHAR(100), 
	timestamp DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_hamsters_beer_consumption_hamster_name ON hamsters_beer_consumption (hamster_name);
CREATE INDEX ix_hamsters_beer_consumption_user_id ON hamsters_beer_consumption (user_id);
CREATE TABLE hamsters_supply_closet_raids (
	id INTEGER NOT NULL, 
	user_id VARCHAR, 
	raided_by VARCHAR(10), 
	items_taken JSON NOT NULL, 
	purpose VARCHAR(100), 
	timestamp DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_hamsters_supply_closet_raids_user_id ON hamsters_supply_closet_raids (user_id);
CREATE TABLE stick_hamster_encounters (
	id INTEGER NOT NULL, 
	user_id VARCHAR(255) NOT NULL, 
	timestamp DATETIME, 
	hamsters_present VARCHAR(100), 
	steve_location VARCHAR(255), 
	bob_location VARCHAR(255), 
	carl_location VARCHAR(255), 
	anxiety_multiplier FLOAT NOT NULL, 
	panic_level VARCHAR(50) NOT NULL, 
	infrastructure_risk VARCHAR(100), 
	stick_response TEXT, 
	paper_bags_consumed INTEGER, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_hamster_encounters_timestamp ON stick_hamster_encounters (timestamp);
CREATE INDEX ix_stick_hamster_encounters_user_id ON stick_hamster_encounters (user_id);
CREATE TABLE stick_paper_bag_usage (
	id INTEGER NOT NULL, 
	timestamp DATETIME, 
	bags_consumed INTEGER, 
	bags_added INTEGER, 
	reason VARCHAR(255), 
	anxiety_level_at_time FLOAT, 
	hamster_related BOOLEAN, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_paper_bag_usage_timestamp ON stick_paper_bag_usage (timestamp);
CREATE TABLE stick_memory_bank (
	id INTEGER NOT NULL, 
	timestamp DATETIME, 
	event_type VARCHAR(100) NOT NULL, 
	details JSON, 
	anxiety_level FLOAT, 
	importance VARCHAR(50), 
	related_hamsters VARCHAR(100), 
	compliance_impact VARCHAR(100), 
	never_forget BOOLEAN, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_stick_memory_bank_timestamp ON stick_memory_bank (timestamp);
CREATE INDEX idx_never_forget ON stick_memory_bank (never_forget, importance);
CREATE INDEX idx_hamster_memories ON stick_memory_bank (related_hamsters);
CREATE TABLE stick_squeak_translations (
	id INTEGER NOT NULL, 
	timestamp DATETIME, 
	hamster_source VARCHAR(50), 
	original_squeak VARCHAR(255), 
	translation TEXT, 
	confidence FLOAT, 
	anxiety_level_during_translation FLOAT, 
	stick_reaction TEXT, 
	paper_bags_consumed INTEGER, 
	PRIMARY KEY (id)
);
CREATE TABLE stick_emergency_protocols (
	id INTEGER NOT NULL, 
	protocol_name VARCHAR(100), 
	trigger_condition VARCHAR(255), 
	activation_count INTEGER, 
	last_activated DATETIME, 
	anxiety_threshold FLOAT, 
	response_actions JSON, 
	hamster_specific BOOLEAN, 
	paper_bags_required INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (protocol_name)
);
CREATE TABLE hamsters_engineering_stats (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	total_interventions INTEGER, 
	successful_interventions INTEGER, 
	abandoned_interventions INTEGER, 
	total_beer_consumed INTEGER, 
	total_duct_tape_used INTEGER, 
	total_supply_closet_raids INTEGER, 
	total_space_freed_gb FLOAT, 
	total_fragmentation_reduced FLOAT, 
	total_mysteries_solved INTEGER, 
	steve_interventions INTEGER, 
	bob_interventions INTEGER, 
	carl_interventions INTEGER, 
	average_beer_per_intervention FLOAT, 
	average_duct_tape_per_intervention FLOAT, 
	intervention_success_rate FLOAT, 
	three_am_intervention_count INTEGER, 
	raw_stats JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_hamsters_engineering_stats_timestamp ON hamsters_engineering_stats (timestamp);
CREATE INDEX ix_hamsters_engineering_stats_user_id ON hamsters_engineering_stats (user_id);
CREATE TABLE meth_snail_energy_consumption (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	energy_drink_type VARCHAR(50) NOT NULL, 
	caffeine_mg FLOAT NOT NULL, 
	authorization_requested BOOLEAN, 
	authorization_granted BOOLEAN, 
	authorized_by VARCHAR(50), 
	energy_drinks_consumed_today INTEGER, 
	time_since_last_drink_minutes INTEGER, 
	consumption_reason VARCHAR(100), 
	authorization_request_timestamp DATETIME, 
	authorization_response_timestamp DATETIME, 
	authorization_notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_meth_snail_energy_consumption_user_id ON meth_snail_energy_consumption (user_id);
CREATE INDEX ix_meth_snail_energy_consumption_timestamp ON meth_snail_energy_consumption (timestamp);
CREATE TABLE meth_snail_jitter_levels (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	current_jitter_level FLOAT NOT NULL, 
	peak_jitter_level FLOAT NOT NULL, 
	baseline_jitter_level FLOAT NOT NULL, 
	caffeine_level_mg FLOAT NOT NULL, 
	is_decaffeinated BOOLEAN, 
	time_since_caffeine_minutes INTEGER, 
	shell_spin_probability FLOAT NOT NULL, 
	optimization_effectiveness FLOAT, 
	focus_level FLOAT NOT NULL, 
	hypercaffeinated BOOLEAN, 
	requires_stick_intervention BOOLEAN, 
	vic20_mediation_requested BOOLEAN, 
	energy_source VARCHAR(50), 
	jitter_trend VARCHAR(20), 
	raw_jitter_data JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_meth_snail_jitter_levels_user_id ON meth_snail_jitter_levels (user_id);
CREATE INDEX ix_meth_snail_jitter_levels_timestamp ON meth_snail_jitter_levels (timestamp);
CREATE TABLE IF NOT EXISTS "tuning_history" (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	parameter VARCHAR NOT NULL, 
	old_value VARCHAR, 
	new_value VARCHAR NOT NULL, 
	success BOOLEAN, 
	error VARCHAR, 
	metrics_before JSON, 
	metrics_after JSON, 
	timestamp DATETIME, 
	beer_consumed INTEGER, 
	duct_tape_used BOOLEAN, 
	supply_closet_raids INTEGER, 
	redneck_ingenuity_level FLOAT, 
	engineering_solution VARCHAR, 
	beer_level_before VARCHAR, 
	beer_level_after VARCHAR, 
	duct_tape_inventory_used INTEGER, 
	supply_closet_items JSON, 
	confidence_score FLOAT, 
	impact_score FLOAT, 
	urgency_level VARCHAR, 
	priority_level VARCHAR, 
	pattern_confidence FLOAT, 
	learned_from_patterns BOOLEAN, 
	historical_data_points INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_tuning_history_id ON tuning_history (id);
CREATE TABLE agent_memory_global_patterns (
	agent_name VARCHAR NOT NULL, 
	pattern_key VARCHAR NOT NULL, 
	value JSON, 
	updated_at DATETIME, 
	PRIMARY KEY (agent_name, pattern_key)
);
CREATE TABLE agent_memories (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	agent_name VARCHAR NOT NULL, 
	memory_type VARCHAR NOT NULL, 
	content JSON NOT NULL, 
	importance INTEGER DEFAULT '5' NOT NULL, 
	timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	last_accessed DATETIME, 
	access_count INTEGER DEFAULT '0' NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_agent_memories_user_id ON agent_memories (user_id);
CREATE INDEX ix_agent_memories_agent_name ON agent_memories (agent_name);
CREATE INDEX ix_agent_memories_memory_type ON agent_memories (memory_type);
CREATE INDEX ix_mem_user_agent_type_time ON agent_memories (user_id, agent_name, memory_type, timestamp);
CREATE TABLE agent_global_patterns (
	id VARCHAR NOT NULL, 
	pattern_key VARCHAR NOT NULL, 
	value JSON NOT NULL, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_agent_global_patterns_pattern_key ON agent_global_patterns (pattern_key);
CREATE INDEX ix_global_pattern_key ON agent_global_patterns (pattern_key);
