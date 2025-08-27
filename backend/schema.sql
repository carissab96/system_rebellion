PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('93f94a61463c');
CREATE TABLE agent_global_patterns (
	id VARCHAR NOT NULL, 
	pattern_key VARCHAR NOT NULL, 
	value JSON NOT NULL, 
	updated_at DATETIME, 
	CONSTRAINT pk_agent_global_patterns PRIMARY KEY (id)
);
CREATE TABLE agent_learning_interactions (
	id INTEGER NOT NULL, 
	interaction_id VARCHAR(36), 
	timestamp DATETIME NOT NULL, 
	source_agent VARCHAR(50) NOT NULL, 
	target_agent VARCHAR(50) NOT NULL, 
	source_memory_id VARCHAR(36) NOT NULL, 
	learning_type VARCHAR(100) NOT NULL, 
	adaptation_method JSON, 
	application_context JSON, 
	transfer_success BOOLEAN, 
	effectiveness_score FLOAT, 
	improvement_measured FLOAT, 
	validated_by_stick BOOLEAN, 
	cross_validation_count INTEGER, 
	CONSTRAINT pk_agent_learning_interactions PRIMARY KEY (id), 
	CONSTRAINT uq_agent_learning_interactions_interaction_id UNIQUE (interaction_id)
);
CREATE TABLE memory_bank_metadata (
	id INTEGER NOT NULL, 
	timestamp DATETIME NOT NULL, 
	total_memories INTEGER, 
	central_bank_memories INTEGER, 
	cross_agent_learnings INTEGER, 
	hawkington_memories INTEGER, 
	snail_memories INTEGER, 
	hamsters_memories INTEGER, 
	qsp_memories INTEGER, 
	vic20_memories INTEGER, 
	stick_memories INTEGER, 
	successful_transfers INTEGER, 
	failed_transfers INTEGER, 
	average_effectiveness_score FLOAT, 
	memory_bank_health_score FLOAT, 
	stick_anxiety_level FLOAT, 
	memory_retrieval_speed_ms FLOAT, 
	cross_agent_query_speed_ms FLOAT, 
	learning_application_success_rate FLOAT, 
	CONSTRAINT pk_memory_bank_metadata PRIMARY KEY (id)
);
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
	CONSTRAINT pk_metrics_daily PRIMARY KEY (id)
);
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
	CONSTRAINT pk_metrics_hourly PRIMARY KEY (id)
);
CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	hashed_password VARCHAR(255) NOT NULL, 
	is_onboarded BOOLEAN, 
	onboarding_progress INTEGER, 
	onboarding_data JSON, 
	onboarding_started_at DATETIME, 
	onboarding_last_step_at DATETIME, 
	onboarding_abandoned_count INTEGER NOT NULL, 
	onboarding_step_timestamps JSON, 
	onboarding_abandonment_reasons JSON, 
	onboarding_device_info JSON, 
	onboarding_referral_source VARCHAR(100), 
	preview_agent_selected VARCHAR(20), 
	preview_started_at DATETIME, 
	preview_expires_at DATETIME, 
	preview_conversion_emails_sent JSON, 
	preview_converted_at DATETIME, 
	email_campaign_responses JSON, 
	last_engagement_at DATETIME, 
	first_name VARCHAR(50), 
	last_name VARCHAR(50), 
	company_name VARCHAR(100), 
	job_title VARCHAR(50), 
	system_name VARCHAR(100), 
	avatar VARCHAR(50), 
	agent_preferences JSON, 
	monitoring_preferences JSON, 
	system_profile JSON, 
	agent_installed BOOLEAN, 
	agent_version VARCHAR(20), 
	installation_method VARCHAR(50), 
	permissions_granted_at DATETIME, 
	is_active BOOLEAN, 
	is_verified BOOLEAN, 
	is_enterprise BOOLEAN, 
	last_login DATETIME, 
	failed_login_attempts INTEGER, 
	lockout_until DATETIME, 
	total_interactions INTEGER, 
	patterns_learned INTEGER, 
	decisions_made INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	CONSTRAINT pk_users PRIMARY KEY (id)
);
CREATE TABLE agent_memories (
	id UUID NOT NULL, 
	user_id VARCHAR NOT NULL, 
	agent_name VARCHAR NOT NULL, 
	memory_type VARCHAR NOT NULL, 
	content JSON NOT NULL, 
	importance INTEGER, 
	timestamp DATETIME, 
	last_accessed DATETIME, 
	access_count INTEGER, 
	CONSTRAINT pk_agent_memories PRIMARY KEY (id), 
	CONSTRAINT fk_agent_memories_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE TABLE central_memory_bank (
	id INTEGER NOT NULL, 
	memory_id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	occurred_at DATETIME NOT NULL, 
	agent_name VARCHAR(50) NOT NULL, 
	user_id VARCHAR, 
	event_type VARCHAR(100) NOT NULL, 
	subject_kind VARCHAR(50), 
	subject_id VARCHAR(36), 
	priority INTEGER, 
	title VARCHAR(255), 
	description TEXT, 
	details JSON, 
	metadata JSON, 
	correlation_id VARCHAR(36), 
	trace_id VARCHAR(36), 
	parent_memory_id VARCHAR(36), 
	numeric_value FLOAT, 
	string_value TEXT, 
	tags JSON, 
	agent_metadata JSON, 
	relevant_agents VARCHAR(255), 
	cross_agent_validated BOOLEAN, 
	validation_count INTEGER, 
	stick_anxiety_level FLOAT, 
	never_forget BOOLEAN, 
	times_referenced INTEGER, 
	last_referenced DATETIME, 
	successful_applications INTEGER, 
	CONSTRAINT pk_central_memory_bank PRIMARY KEY (id), 
	CONSTRAINT fk_central_memory_bank_parent_memory_id_central_memory_bank FOREIGN KEY(parent_memory_id) REFERENCES central_memory_bank (memory_id), 
	CONSTRAINT fk_central_memory_bank_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	CONSTRAINT uq_central_memory_bank_memory_id UNIQUE (memory_id)
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
	CONSTRAINT pk_system_metrics PRIMARY KEY (id), 
	CONSTRAINT fk_system_metrics_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE user_learning_patterns (
	id INTEGER NOT NULL, 
	pattern_id VARCHAR(36), 
	user_id VARCHAR NOT NULL, 
	timestamp DATETIME NOT NULL, 
	interaction_pattern JSON, 
	learning_preference JSON, 
	response_patterns JSON, 
	most_effective_agent VARCHAR(50), 
	communication_style_preference JSON, 
	complexity_tolerance FLOAT, 
	skill_improvement_areas JSON, 
	knowledge_gaps JSON, 
	success_patterns JSON, 
	agent_effectiveness_ranking JSON, 
	collaborative_preferences JSON, 
	CONSTRAINT pk_user_learning_patterns PRIMARY KEY (id), 
	CONSTRAINT fk_user_learning_patterns_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	CONSTRAINT uq_user_learning_patterns_pattern_id UNIQUE (pattern_id)
);
CREATE INDEX ix_agent_global_patterns_pattern_key ON agent_global_patterns (pattern_key);
CREATE INDEX idx_ali_adaptation_gin ON agent_learning_interactions (adaptation_method);
CREATE INDEX idx_ali_appctx_gin ON agent_learning_interactions (application_context);
CREATE INDEX idx_learning_effectiveness ON agent_learning_interactions (effectiveness_score, transfer_success);
CREATE INDEX idx_learning_transfer ON agent_learning_interactions (source_agent, target_agent, learning_type);
CREATE INDEX ix_agent_learning_interactions_source_agent ON agent_learning_interactions (source_agent);
CREATE INDEX ix_agent_learning_interactions_target_agent ON agent_learning_interactions (target_agent);
CREATE INDEX ix_agent_learning_interactions_timestamp ON agent_learning_interactions (timestamp);
CREATE INDEX idx_mb_effectiveness ON memory_bank_metadata (average_effectiveness_score, successful_transfers);
CREATE INDEX idx_memory_health ON memory_bank_metadata (memory_bank_health_score, timestamp);
CREATE INDEX ix_memory_bank_metadata_timestamp ON memory_bank_metadata (timestamp);
CREATE INDEX idx_ai_incident_count ON metrics_daily (daily_ai_incident_count, daily_ai_incident_type, daily_ai_incident_reason);
CREATE INDEX idx_user_date ON metrics_daily (user_id, date);
CREATE INDEX ix_metrics_daily_date ON metrics_daily (date);
CREATE INDEX ix_metrics_daily_id ON metrics_daily (id);
CREATE INDEX ix_metrics_daily_user_id ON metrics_daily (user_id);
CREATE INDEX idx_user_hour ON metrics_hourly (user_id, hour_start);
CREATE INDEX ix_metrics_hourly_hour_start ON metrics_hourly (hour_start);
CREATE INDEX ix_metrics_hourly_id ON metrics_hourly (id);
CREATE INDEX ix_metrics_hourly_user_id ON metrics_hourly (user_id);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE INDEX ix_agent_memories_agent_name ON agent_memories (agent_name);
CREATE INDEX ix_agent_memories_memory_type ON agent_memories (memory_type);
CREATE INDEX ix_agent_memories_timestamp ON agent_memories (timestamp);
CREATE INDEX ix_agent_memories_user_id ON agent_memories (user_id);
CREATE INDEX ix_mem_user_agent_type_time ON agent_memories (user_id, agent_name, memory_type, timestamp);
CREATE INDEX idx_agent_event_time ON central_memory_bank (agent_name, event_type, occurred_at);
CREATE INDEX idx_agent_user ON central_memory_bank (agent_name, user_id);
CREATE INDEX idx_cmb_details_gin ON central_memory_bank (details);
CREATE INDEX idx_cmb_metadata_gin ON central_memory_bank (metadata);
CREATE INDEX idx_cmb_tags_gin ON central_memory_bank (tags);
CREATE INDEX idx_correlation ON central_memory_bank (correlation_id, trace_id);
CREATE INDEX idx_event_timestamp ON central_memory_bank (event_type, occurred_at);
CREATE INDEX idx_memory_importance ON central_memory_bank (priority, never_forget);
CREATE INDEX idx_metric_queries ON central_memory_bank (event_type, occurred_at, subject_kind);
CREATE INDEX idx_priority_access ON central_memory_bank (priority, last_referenced);
CREATE INDEX idx_subject_reference ON central_memory_bank (subject_kind, subject_id);
CREATE INDEX idx_user_events ON central_memory_bank (user_id, occurred_at);
CREATE INDEX ix_central_memory_bank_agent_name ON central_memory_bank (agent_name);
CREATE INDEX ix_central_memory_bank_created_at ON central_memory_bank (created_at);
CREATE INDEX ix_central_memory_bank_event_type ON central_memory_bank (event_type);
CREATE INDEX ix_central_memory_bank_occurred_at ON central_memory_bank (occurred_at);
CREATE INDEX ix_central_memory_bank_priority ON central_memory_bank (priority);
CREATE INDEX ix_central_memory_bank_subject_id ON central_memory_bank (subject_id);
CREATE INDEX ix_central_memory_bank_subject_kind ON central_memory_bank (subject_kind);
CREATE INDEX ix_central_memory_bank_user_id ON central_memory_bank (user_id);
CREATE INDEX ix_system_metrics_id ON system_metrics (id);
CREATE INDEX idx_ulp_learning_pref_gin ON user_learning_patterns (learning_preference);
CREATE INDEX idx_user_complexity ON user_learning_patterns (user_id, complexity_tolerance);
CREATE INDEX idx_user_patterns ON user_learning_patterns (user_id, most_effective_agent);
CREATE INDEX ix_user_learning_patterns_timestamp ON user_learning_patterns (timestamp);
CREATE INDEX ix_user_learning_patterns_user_id ON user_learning_patterns (user_id);
COMMIT;
