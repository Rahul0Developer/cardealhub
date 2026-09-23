#!/bin/bash
# Automated startup script for Render deployment

set -e

echo "🚀 Starting Car Deal Hub deployment..."

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Run database migrations if script exists
if [ -f "db_migrate.py" ]; then
    echo "🗄️  Running database migrations..."
    python db_migrate.py || echo "⚠️  Migration failed, continuing anyway..."
fi

# Start the application with Gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn --config gunicorn.conf.py main:app
