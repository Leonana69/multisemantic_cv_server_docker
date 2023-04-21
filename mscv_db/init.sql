CREATE TABLE IF NOT EXISTS services (
	id SERIAL PRIMARY KEY,
	service_user VARCHAR(50) NOT NULL,
	user_group VARCHAR(50),
	func VARCHAR(50) NOT NULL,
	external_url VARCHAR(1000),
	last_touched TIMESTAMPTZ NOT NULL
);

CREATE UNIQUE INDEX idx_services_service_user_func ON services (service_user, func);
CREATE UNIQUE INDEX idx_services_user_group_func ON services (user_group, func);

