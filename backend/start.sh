#!/bin/bash

# Load environment variables
set -a
source .env
set +a

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! redis-cli -h redis ping; do
    sleep 1
done
echo "Redis is ready!"

# Start the Flask application
echo "Starting Flask application..."
flask run --host=0.0.0.0 