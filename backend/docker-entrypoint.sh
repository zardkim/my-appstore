#!/bin/bash
set -e

echo "========================================="
echo "MyApp Store Backend - Starting up..."
echo "Version: ${APP_VERSION:-unknown}"
echo "========================================="

# Create necessary directories first (as root)
echo "[1/6] Creating directories..."
mkdir -p /app/data/logs /app/data/icons /app/data/screenshots /app/data/library /app/data/config /app/static/icons

# Fix permissions for mounted /app/data directory (run as root)
echo "[2/6] Fixing permissions for /app/data..."
if [ -d "/app/data" ]; then
  chown -R appuser:appuser /app/data 2>/dev/null || echo "Warning: Could not change ownership"
  chmod -R u+rwX /app/data 2>/dev/null || echo "Warning: Could not change permissions"
fi
echo "✓ Permissions fixed"

# Wait for PostgreSQL to be ready
echo "[3/6] Waiting for PostgreSQL..."
MAX_RETRIES=30
RETRY_COUNT=0

if [ -n "$DB_HOST" ] && [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_DB" ]; then
  while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; then
      echo "✓ PostgreSQL is ready!"
      break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "PostgreSQL is unavailable - attempt $RETRY_COUNT/$MAX_RETRIES - sleeping 2s"
    sleep 2
  done

  if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Could not connect to PostgreSQL after $MAX_RETRIES attempts"
    exit 1
  fi
else
  echo "WARNING: Database environment variables not set properly"
  echo "DB_HOST=$DB_HOST, POSTGRES_USER=$POSTGRES_USER, POSTGRES_DB=$POSTGRES_DB"
fi

# Check database schema version
echo "[4/6] Checking database schema..."
if [ -n "$DB_HOST" ] && [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_DB" ]; then
  # Check if alembic_version table exists
  TABLE_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version');" 2>/dev/null | tr -d '[:space:]')

  if [ "$TABLE_EXISTS" = "t" ]; then
    CURRENT_VERSION=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT version_num FROM alembic_version LIMIT 1;" 2>/dev/null | tr -d '[:space:]')
    echo "Current DB version: ${CURRENT_VERSION:-none}"
  else
    echo "Database is new or not initialized"
  fi

  # Check tables count
  TABLES_COUNT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d '[:space:]')
  echo "Existing tables in database: $TABLES_COUNT"
fi

# Run database migrations (as appuser)
echo "[5/6] Running database migrations..."
cd /app

# Show pending migrations
echo "Checking for pending migrations..."
MIGRATION_STATUS=$(gosu appuser alembic current 2>&1) || true
echo "Migration status: $MIGRATION_STATUS"

# Run migrations
if gosu appuser alembic upgrade head; then
  echo "✓ Database migrations complete"

  # Show final version
  FINAL_VERSION=$(gosu appuser alembic current 2>&1 | grep -oP '[a-f0-9]+(?= \(head\))' || echo "unknown")
  echo "Final DB version: $FINAL_VERSION"
else
  echo "WARNING: Migration failed - checking if this is expected..."
  # Check if tables exist anyway (might be first run with existing data)
  if [ "$TABLES_COUNT" -gt "0" ]; then
    echo "Database has existing tables - continuing..."
  else
    echo "ERROR: Migration failed and no existing tables found"
    exit 1
  fi
fi

# Verify critical tables exist
echo "[6/6] Verifying database schema..."
if [ -n "$DB_HOST" ] && [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_DB" ]; then
  CRITICAL_TABLES=("users" "products" "versions" "settings")
  ALL_TABLES_OK=true

  for table in "${CRITICAL_TABLES[@]}"; do
    EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '$table');" 2>/dev/null | tr -d '[:space:]')
    if [ "$EXISTS" = "t" ]; then
      echo "  ✓ Table '$table' exists"
    else
      echo "  ✗ Table '$table' missing!"
      ALL_TABLES_OK=false
    fi
  done

  if [ "$ALL_TABLES_OK" = false ]; then
    echo "WARNING: Some critical tables are missing"
  fi
fi

echo ""
echo "========================================="
echo "Starting FastAPI application..."
echo "Environment: ${ENVIRONMENT:-production}"
echo "Log Level: ${LOG_LEVEL:-INFO}"
echo "========================================="

# Execute the main command as appuser
exec gosu appuser "$@"
