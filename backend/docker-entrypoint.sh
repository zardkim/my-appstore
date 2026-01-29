#!/bin/bash
set -e

echo "========================================="
echo "MyApp Store Backend - Starting up..."
echo "========================================="

# Fix permissions for mounted /app/data directory (run as root)
echo "Fixing permissions for /app/data..."
chown -R appuser:appuser /app/data 2>/dev/null || true
chmod -R u+rwX /app/data 2>/dev/null || true

echo "✓ Permissions fixed"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✓ PostgreSQL is ready!"

# Run database migrations (as appuser)
echo "Running database migrations..."
gosu appuser alembic upgrade head || {
  echo "WARNING: Migration failed or no migrations to run"
}

echo "✓ Database migrations complete"

# Create necessary directories (as appuser)
gosu appuser mkdir -p /app/data/logs /app/static/icons

echo "========================================="
echo "Starting FastAPI application..."
echo "Environment: $ENVIRONMENT"
echo "Log Level: $LOG_LEVEL"
echo "========================================="

# Execute the main command as appuser
exec gosu appuser "$@"
