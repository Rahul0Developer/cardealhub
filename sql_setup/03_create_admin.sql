-- Connect to the database
\c cardealhub

-- Create admin user (password: admin123)
-- The password_hash is for the password 'admin123' using Werkzeug's generate_password_hash
INSERT INTO "user" (username, email, password_hash, is_admin, is_verified)
VALUES ('admin', 'admin@cardealhub.com', 'pbkdf2:sha256:600000$nLQAJ0ZkslBPqIxn$b35c0cc3dba53b3f07a69f11e5ea4aac6f2acb9affc0d7c27d7e297c4a72eb30', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;