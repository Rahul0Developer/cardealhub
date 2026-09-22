-- Create CarDealHub database
CREATE DATABASE cardealhub;

-- Connect to the database
\c cardealhub

-- Create a user with appropriate permissions (optional)
-- CREATE USER cardealhub_user WITH ENCRYPTED PASSWORD 'your_secure_password';
-- GRANT ALL PRIVILEGES ON DATABASE cardealhub TO cardealhub_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cardealhub_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cardealhub_user;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";