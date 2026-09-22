-- Connect to the database
\c cardealhub

-- Create Users table
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_banned BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Cars table
CREATE TABLE IF NOT EXISTS car (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    price INTEGER NOT NULL,
    kms_driven INTEGER NOT NULL,
    fuel_type VARCHAR(20) NOT NULL,
    transmission VARCHAR(20),
    owners INTEGER DEFAULT 1,
    color VARCHAR(30),
    location VARCHAR(100),
    description TEXT,
    features TEXT,
    condition VARCHAR(20),
    contact_name VARCHAR(100),
    contact_email VARCHAR(120),
    contact_phone VARCHAR(20),
    show_phone BOOLEAN DEFAULT TRUE,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_path VARCHAR(200),
    image_path2 VARCHAR(200),
    image_path3 VARCHAR(200)
);

-- Create Prediction table
CREATE TABLE IF NOT EXISTS prediction (
    id SERIAL PRIMARY KEY,
    company VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    kms_driven INTEGER NOT NULL,
    fuel_type VARCHAR(20) NOT NULL,
    predicted_price INTEGER NOT NULL,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create LikedCar table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS liked_car (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    car_id INTEGER REFERENCES car(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, car_id)
);

-- Create Transaction table
CREATE TABLE IF NOT EXISTS transaction (
    id SERIAL PRIMARY KEY,
    car_id INTEGER REFERENCES car(id) ON DELETE SET NULL,
    buyer_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
    seller_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
    amount FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Success', 'Failed', 'Pending')),
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(100) UNIQUE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    receipt_url VARCHAR(255)
);

-- Create ListingStatus table
CREATE TABLE IF NOT EXISTS listing_status (
    id SERIAL PRIMARY KEY,
    car_id INTEGER REFERENCES car(id) ON DELETE CASCADE UNIQUE,
    is_approved BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_sold BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_notes TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_car_user_id ON car(user_id);
CREATE INDEX IF NOT EXISTS idx_car_company ON car(company);
CREATE INDEX IF NOT EXISTS idx_car_fuel_type ON car(fuel_type);
CREATE INDEX IF NOT EXISTS idx_car_created_at ON car(created_at);
CREATE INDEX IF NOT EXISTS idx_prediction_user_id ON prediction(user_id);
CREATE INDEX IF NOT EXISTS idx_liked_car_user_id ON liked_car(user_id);
CREATE INDEX IF NOT EXISTS idx_liked_car_car_id ON liked_car(car_id);
CREATE INDEX IF NOT EXISTS idx_transaction_car_id ON transaction(car_id);
CREATE INDEX IF NOT EXISTS idx_transaction_buyer_id ON transaction(buyer_id);
CREATE INDEX IF NOT EXISTS idx_transaction_seller_id ON transaction(seller_id);
CREATE INDEX IF NOT EXISTS idx_listing_status_car_id ON listing_status(car_id);