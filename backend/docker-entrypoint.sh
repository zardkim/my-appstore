#!/bin/bash
set -e

echo "========================================="
echo "MyApp Store Backend - Starting up..."
echo "========================================="

# Create necessary directories first (as root)
echo "Creating directories..."
mkdir -p /app/data/logs /app/data/icons /app/data/screenshots /app/data/library /app/static/icons

# Fix permissions for mounted /app/data directory (run as root)
echo "Fixing permissions for /app/data..."
if [ -d "/app/data" ]; then
  chown -R appuser:appuser /app/data 2>/dev/null || echo "Warning: Could not change ownership"
  chmod -R u+rwX /app/data 2>/dev/null || echo "Warning: Could not change permissions"
fi

echo "✓ Permissions fixed"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
if [ -n "$DB_HOST" ] && [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_DB" ]; then
  until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
  done
  echo "✓ PostgreSQL is ready!"
else
  echo "WARNING: Database environment variables not set properly"
  echo "DB_HOST=$DB_HOST, POSTGRES_USER=$POSTGRES_USER, POSTGRES_DB=$POSTGRES_DB"
fi

# Run database migrations (as appuser)
echo "Running database migrations..."
gosu appuser alembic upgrade head || {
  echo "WARNING: Migration failed or no migrations to run"
}

echo "✓ Database migrations complete"

echo "========================================="
echo "Starting FastAPI application..."
echo "Environment: $ENVIRONMENT"
echo "Log Level: $LOG_LEVEL"
echo "========================================="

# Execute the main command as appuser
exec gosu appuser "$@"
