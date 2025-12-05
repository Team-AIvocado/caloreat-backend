#!/bin/sh
set -e

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start the application
echo "Starting Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
