#!/bin/bash
set -e

echo "========================================="
echo "MyApp Store Backend - Starting up..."
echo "========================================="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✓ PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || {
  echo "WARNING: Migration failed or no migrations to run"
}

echo "✓ Database migrations complete"

# Create necessary directories
mkdir -p /app/data/logs /app/static/icons

echo "========================================="
echo "Starting FastAPI application..."
echo "Environment: $ENVIRONMENT"
echo "Log Level: $LOG_LEVEL"
echo "========================================="

# Execute the main command
exec "$@"
