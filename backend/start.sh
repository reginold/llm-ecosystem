#!/bin/bash

# Load environment variables
set -a
source .env
set +a

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U admin -d llm_ecosystem; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! redis-cli -h redis ping; do
    sleep 1
done
echo "Redis is ready!"

# Initialize the database
echo "Initializing database..."
python init_db.py

# Start the Flask application
echo "Starting Flask application..."
flask run --host=0.0.0.0 