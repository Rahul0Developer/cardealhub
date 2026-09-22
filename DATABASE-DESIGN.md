# Car Deal Hub - Database Design Documentation

This document outlines the database design for the Car Deal Hub application, including table schemas, relationships, and setup processes.

## Database Technology

Car Deal Hub uses PostgreSQL, a powerful, open-source object-relational database system with a strong reputation for reliability, feature robustness, and performance.

## Entity Relationship Diagram (ERD)

Below is a simplified representation of the database relationships:

```
User (1) ----< Car (n)
User (1) ----< Prediction (n)
User (1) ----< LikedCar (n) >---- Car (1)
Car (1) ----< Transaction (n)
Car (1) ---- ListingStatus (1)
User (1) ----< Transaction (n) as buyer/seller
```

## Table Schemas

### User Table

Stores user account information and profile details.

| Column          | Type         | Constraints       | Description                               |
|-----------------|--------------|-------------------|-------------------------------------------|
| id              | Integer      | PK, Auto          | User identifier                           |
| username        | String(64)   | Unique, Not Null  | User's chosen username                    |
| email           | String(120)  | Unique, Not Null  | User's email address                      |
| password_hash   | String(256)  | Not Null          | Securely hashed password                  |
| created_at      | DateTime     | Default now       | Account creation timestamp                |
| is_admin        | Boolean      | Default False     | Administrator privilege flag              |
| is_verified     | Boolean      | Default False     | Email verification status                 |
| is_banned       | Boolean      | Default False     | Account ban status                        |
| last_login      | DateTime     | Default now       | Last login timestamp                      |

### Car Table

Stores details of car listings.

| Column          | Type         | Constraints       | Description                               |
|-----------------|--------------|-------------------|-------------------------------------------|
| id              | Integer      | PK, Auto          | Car identifier                            |
| name            | String(100)  | Not Null          | Car model name                            |
| company         | String(50)   | Not Null          | Car brand/manufacturer                    |
| year            | Integer      | Not Null          | Manufacturing year                        |
| price           | Integer      | Not Null          | Asking price (in rupees)                  |
| kms_driven      | Integer      | Not Null          | Kilometers on odometer                    |
| fuel_type       | String(20)   | Not Null          | Fuel type (Petrol, Diesel, etc.)          |
| transmission    | String(20)   |                   | Transmission type (Manual, Automatic)     |
| owners          | Integer      | Default 1         | Number of previous owners                 |
| color           | String(30)   |                   | Car color                                 |
| location        | String(100)  |                   | City where car is available               |
| description     | Text         |                   | Detailed car description                  |
| features        | Text         |                   | Car features as comma-separated list      |
| condition       | String(20)   |                   | Overall condition                         |
| contact_name    | String(100)  |                   | Seller contact name                       |
| contact_email   | String(120)  |                   | Seller contact email                      |
| contact_phone   | String(20)   |                   | Seller contact phone                      |
| show_phone      | Boolean      | Default True      | Option to show/hide phone number          |
| user_id         | Integer      | FK (User.id)      | Reference to the owner                    |
| created_at      | DateTime     | Default now       | Listing creation timestamp                |
| updated_at      | DateTime     | Default now       | Last update timestamp                     |
| image_path      | String(200)  |                   | Primary image path                        |
| image_path2     | String(200)  |                   | Secondary image path                      |
| image_path3     | String(200)  |                   | Tertiary image path                       |

### Prediction Table

Stores car price predictions made by users.

| Column          | Type         | Constraints       | Description                               |
|-----------------|--------------|-------------------|-------------------------------------------|
| id              | Integer      | PK, Auto          | Prediction identifier                     |
| company         | String(50)   | Not Null          | Car brand                                 |
| name            | String(100)  | Not Null          | Car model                                 |
| year            | Integer      | Not Null          | Manufacturing year                        |
| kms_driven      | Integer      | Not Null          | Kilometers driven                         |
| fuel_type       | String(20)   | Not Null          | Fuel type                                 |
| predicted_price | Integer      | Not Null          | Predicted price (in rupees)               |
| user_id         | Integer      | FK (User.id)      | Reference to the user                     |
| created_at      | DateTime     | Default now       | Prediction timestamp                      |

### LikedCar Table

Tracks cars liked by users (many-to-many relationship).

| Column          | Type         | Constraints                  | Description                    |
|-----------------|--------------|------------------------------|--------------------------------|
| id              | Integer      | PK, Auto                     | Like identifier                |
| user_id         | Integer      | FK (User.id), Not Null       | Reference to the user          |
| car_id          | Integer      | FK (Car.id), Not Null        | Reference to the car           |
| created_at      | DateTime     | Default now                  | Like timestamp                 |
|                 |              | Unique(user_id, car_id)      | Prevents duplicate likes       |

### Transaction Table

Records car purchase transactions.

| Column          | Type         | Constraints       | Description                               |
|-----------------|--------------|-------------------|-------------------------------------------|
| id              | Integer      | PK, Auto          | Transaction identifier                    |
| car_id          | Integer      | FK (Car.id)       | Reference to the car                      |
| buyer_id        | Integer      | FK (User.id)      | Reference to the buyer                    |
| seller_id       | Integer      | FK (User.id)      | Reference to the seller                   |
| amount          | Float        | Not Null          | Transaction amount                        |
| status          | Enum         | Not Null          | 'Success', 'Failed', 'Pending'            |
| payment_method  | String(50)   | Not Null          | Payment method used                       |
| transaction_id  | String(100)  | Unique            | External payment reference                |
| timestamp       | DateTime     | Default now       | Transaction timestamp                     |
| receipt_url     | String(255)  |                   | URL to transaction receipt                |

### ListingStatus Table

Manages approval and sale status for car listings.

| Column          | Type         | Constraints            | Description                    |
|-----------------|--------------|------------------------|--------------------------------|
| id              | Integer      | PK, Auto               | Status identifier              |
| car_id          | Integer      | FK (Car.id), Unique    | Reference to the car           |
| is_approved     | Boolean      | Default False          | Admin approval status          |
| is_featured     | Boolean      | Default False          | Featured listing flag          |
| is_sold         | Boolean      | Default False          | Sale completion status         |
| updated_at      | DateTime     | Default now            | Last update timestamp          |
| admin_notes     | Text         |                        | Admin comments on listing      |

## Database Setup Process

### Step 1: Setup PostgreSQL

1. Install PostgreSQL on your system
2. Create a new database named 'cardealhub':
   ```sql
   CREATE DATABASE cardealhub;
   ```
3. Create a user (optional):
   ```sql
   CREATE USER cardealhub_user WITH ENCRYPTED PASSWORD 'Manav5465';
   GRANT ALL PRIVILEGES ON DATABASE cardealhub TO cardealhub_user;
   ```

### Step 2: Configure Database Connection

1. Set the DATABASE_URL environment variable:
   ```
   postgresql://username:Manav5465@localhost:5432/cardealhub
   ```
2. This URL is automatically loaded in `app.py` to establish the database connection

### Step 3: Run Database Migrations

The project uses SQLAlchemy to manage database schema and migrations:

1. Initialize the database schema:
   ```
   python db_migrate.py
   ```

This script performs the following operations:
- Creates all tables if they don't exist
- Adds any new columns to existing tables
- Sets up proper relationships between tables
- Creates default admin user if needed

### Step 4: Database Maintenance

For ongoing database maintenance:

1. Backup regularly:
   ```bash
   pg_dump -U username cardealhub > backup.sql
   ```

2. Restore when needed:
   ```bash
   psql -U username cardealhub < backup.sql
   ```

3. To reset admin password:
   ```
   python reset_admin.py
   ```

## Database Security Considerations

1. **Password Hashing**: User passwords are never stored in plain text. They are hashed using Werkzeug's security functions.

2. **Input Validation**: All user inputs are validated before database operations to prevent SQL injection.

3. **Connection Pooling**: The database configuration includes connection pooling to efficiently manage connections:
   ```python
   app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
       "pool_recycle": 300,
       "pool_pre_ping": True,
   }
   ```

4. **Environment Variables**: Sensitive connection information is stored in environment variables, not in the code.

## Database Performance Optimization

1. **Indexes**: Important columns are indexed for faster queries:
   - Foreign key columns (user_id, car_id)
   - Frequently searched columns (company, fuel_type)
   - Timestamp columns for sorting (created_at)

2. **Query Optimization**: Complex queries use joins and filtering to minimize database load.

3. **Pagination**: Results are paginated to limit the amount of data transferred in each request.

## Database Backup and Recovery

For production environments, implement regular backups:

1. **Daily Automated Backups**: Use cron jobs to run pg_dump daily
2. **Point-in-Time Recovery**: Enable WAL (Write-Ahead Logging) for incremental backups
3. **Off-site Storage**: Store backups in a separate location from the production server