#!/bin/sh
set -e

# Run migrations
echo "alembic migration 실행"
alembic upgrade head

# Start the application
echo "uvicorn server 실행"
exec uvicorn main:app --host 0.0.0.0 --port 8000
