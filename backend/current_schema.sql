CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
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
CREATE TABLE user_profiles (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	location VARCHAR(100), 
	website VARCHAR(200), 
	github_email VARCHAR(50), 
	linkedin_profile VARCHAR(200), 
	theme_preference VARCHAR(20), 
	notification_settings VARCHAR(100), 
	optimization_level VARCHAR(50), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
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
	PRIMARY KEY (id)
);
CREATE INDEX ix_system_metrics_id ON system_metrics (id);
CREATE TABLE tuning_history (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	parameter VARCHAR NOT NULL, 
	old_value VARCHAR, 
	new_value VARCHAR NOT NULL, 
	success BOOLEAN, 
	error VARCHAR, 
	metrics_before JSON, 
	metrics_after JSON, 
	timestamp DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_tuning_history_id ON tuning_history (id);
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
CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	email VARCHAR(50) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	hashed_password VARCHAR(255) NOT NULL, 
	needs_onboarding BOOLEAN, 
	first_name VARCHAR(50), 
	last_name VARCHAR(50), 
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
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_email ON users (email);
CREATE TABLE metrics_hourly (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	hour_start DATETIME NOT NULL, 
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
CREATE INDEX ix_metrics_hourly_id ON metrics_hourly (id);
CREATE INDEX ix_metrics_hourly_hour_start ON metrics_hourly (hour_start);
CREATE INDEX idx_user_hour ON metrics_hourly (user_id, hour_start);
CREATE INDEX ix_metrics_hourly_user_id ON metrics_hourly (user_id);
CREATE TABLE metrics_daily (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	date DATETIME NOT NULL, 
	cpu_avg FLOAT, 
	cpu_peak_time DATETIME, 
	cpu_peak_value FLOAT, 
	memory_avg FLOAT, 
	memory_peak_time DATETIME, 
	memory_peak_value FLOAT, 
	disk_avg FLOAT, 
	network_bytes_total FLOAT, 
	ai_summary JSON, 
	total_concerns INTEGER, 
	total_alerts INTEGER, 
	usage_pattern JSON, 
	PRIMARY KEY (id)
);
CREATE INDEX idx_user_date ON metrics_daily (user_id, date);
CREATE INDEX ix_metrics_daily_date ON metrics_daily (date);
CREATE INDEX ix_metrics_daily_id ON metrics_daily (id);
CREATE INDEX ix_metrics_daily_user_id ON metrics_daily (user_id);
