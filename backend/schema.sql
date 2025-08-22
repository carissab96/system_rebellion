CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	hashed_password VARCHAR(255) NOT NULL, 
	is_onboarded BOOLEAN NOT NULL, 
	first_name VARCHAR(50), 
	last_name VARCHAR(50), 
	company_name VARCHAR(100), 
	job_title VARCHAR(50), 
	bio TEXT, 
	profile_picture VARCHAR(255), 
	operating_system VARCHAR(50), 
	os_version VARCHAR(50), 
	linux_distro VARCHAR(50), 
	linux_distro_version VARCHAR(50), 
	cpu_cores INTEGER, 
	total_memory INTEGER, 
	avatar VARCHAR(50), 
	preferences JSON, 
	is_active BOOLEAN, 
	is_superuser BOOLEAN, 
	is_verified BOOLEAN, 
	last_login DATETIME, 
	failed_login_attempts INTEGER, 
	lockout_until DATETIME, 
	created_at DATETIME, 
	updated_at DATETIME, system_name VARCHAR(100), ram_gb INTEGER, storage_gb INTEGER, primary_use_case VARCHAR(100), monitoring_preferences JSON, agent_preferences JSON, system_profile JSON, onboarding_completed BOOLEAN, monitoring_thresholds JSON, permissions_status JSON, installation_method VARCHAR(50), onboarding_progress TEXT, onboarding_started_at DATETIME, onboarding_last_step_at DATETIME, onboarding_abandoned_count INTEGER DEFAULT '0' NOT NULL, onboarding_step_timestamps TEXT, onboarding_abandonment_reasons TEXT, onboarding_device_info TEXT, onboarding_referral_source VARCHAR(100), preview_agent_selected VARCHAR(20), preview_started_at DATETIME, preview_expires_at DATETIME, preview_conversion_emails_sent TEXT, preview_converted_at DATETIME, email_campaign_responses TEXT, last_engagement_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_email ON users (email);
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
