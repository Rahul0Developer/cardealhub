import os
import sys
from sqlalchemy import create_engine, text
from app import db

# Connect to the database
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set.")
    sys.exit(1)

try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("Connected to database successfully!")
except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)

def check_column_exists(table_name, column_name):
    """Check if column exists in table"""
    sql = text(f"""
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        AND column_name = '{column_name}'
    );
    """)
    result = connection.execute(sql).fetchone()[0]
    return result

def add_column(table_name, column_name, column_type):
    """Add column if it doesn't exist"""
    if not check_column_exists(table_name, column_name):
        print(f"Adding column {column_name} to {table_name}")
        sql = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
        connection.execute(sql)
        connection.commit()
        print(f"Added column {column_name} to {table_name}")
    else:
        print(f"Column {column_name} already exists in {table_name}")

def check_table_exists(table_name):
    """Check if table exists in database"""
    sql = text(f"""
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_name = '{table_name}'
    );
    """)
    result = connection.execute(sql).fetchone()[0]
    return result

def run_migrations():
    """Run all database migrations"""
    print("Running database migrations...")
    
    # Add Car model new fields
    add_column('car', 'transmission', 'VARCHAR(20)')
    add_column('car', 'owners', 'INTEGER DEFAULT 1')
    add_column('car', 'color', 'VARCHAR(30)')
    add_column('car', 'location', 'VARCHAR(100)')
    add_column('car', 'features', 'TEXT')
    add_column('car', 'condition', 'VARCHAR(20)')
    add_column('car', 'contact_name', 'VARCHAR(100)')
    add_column('car', 'contact_email', 'VARCHAR(120)')
    add_column('car', 'contact_phone', 'VARCHAR(20)')
    add_column('car', 'show_phone', 'BOOLEAN DEFAULT TRUE')
    add_column('car', 'updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    add_column('car', 'image_path2', 'VARCHAR(200)')
    add_column('car', 'image_path3', 'VARCHAR(200)')
    
    # Create Transaction table if it doesn't exist
    if not check_table_exists('transaction'):
        print("Creating transaction table...")
        
        # Check if enum type already exists
        enum_exists = connection.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type 
                WHERE typname = 'transaction_status'
            )
        """)).fetchone()[0]
        
        if not enum_exists:
            print("Creating transaction_status enum type...")
            connection.execute(text("""
                CREATE TYPE transaction_status AS ENUM ('Success', 'Failed', 'Pending')
            """))
            connection.commit()
            print("Created transaction_status enum type")
        
        # Create transaction table
        connection.execute(text("""
            CREATE TABLE transaction (
                id SERIAL PRIMARY KEY,
                car_id INTEGER NOT NULL REFERENCES car(id),
                buyer_id INTEGER NOT NULL REFERENCES "user"(id),
                seller_id INTEGER NOT NULL REFERENCES "user"(id),
                amount FLOAT NOT NULL,
                status transaction_status NOT NULL DEFAULT 'Pending',
                payment_method VARCHAR(50) NOT NULL,
                transaction_id VARCHAR(100) UNIQUE,
                timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                receipt_url VARCHAR(255)
            )
        """))
        connection.commit()
        print("Created transaction table successfully!")
    else:
        print("Transaction table already exists")
    
    print("Database migrations completed!")

if __name__ == "__main__":
    run_migrations()
    connection.close()
    print("Migration script completed successfully!")