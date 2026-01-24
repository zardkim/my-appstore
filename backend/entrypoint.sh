#!/bin/bash
set -e

echo "Starting MyApp Store Backend..."

# Wait for database to be ready (using Python)
echo "Waiting for database..."
echo "Environment variables check:"
echo "  DATABASE_URL: ${DATABASE_URL:0:40}..."
echo "  POSTGRES_USER: ${POSTGRES_USER}"
echo "  POSTGRES_DB: ${POSTGRES_DB}"

python3 << 'END'
import time
import psycopg2
import os
import sys

# Parse DATABASE_URL or use individual env vars
database_url = os.getenv('DATABASE_URL', '')
postgres_user = os.getenv('POSTGRES_USER', 'postgres')
postgres_password = os.getenv('POSTGRES_PASSWORD', 'password')
postgres_db = os.getenv('POSTGRES_DB', 'myappstore')

if database_url:
    print(f"Using DATABASE_URL from environment")
    # Mask password in log
    safe_url = database_url.split('@')[0].split(':')[0] + ':****@' + database_url.split('@')[1] if '@' in database_url else database_url[:40]
    print(f"  Connection string: {safe_url}")
else:
    print("DATABASE_URL not set, constructing from individual vars")
    print(f"  POSTGRES_USER: {postgres_user}")
    print(f"  POSTGRES_DB: {postgres_db}")
    print(f"  POSTGRES_PASSWORD: {'*' * len(postgres_password)}")
    database_url = f"postgresql://{postgres_user}:{postgres_password}@db:5432/{postgres_db}"

max_retries = 30
for i in range(max_retries):
    try:
        print(f"Attempt {i+1}/{max_retries} to connect to database...")
        conn = psycopg2.connect(database_url)
        conn.close()
        print("✓ Database is ready!")
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f"✗ Connection failed: {str(e)[:100]}")
        if i < max_retries - 1:
            print(f"  Waiting 1 second before retry...")
            time.sleep(1)
        else:
            print("✗ Failed to connect to database after 30 attempts")
            print("\nDebug info:")
            print(f"  Target: db:5432")
            print(f"  User: {postgres_user}")
            print(f"  Database: {postgres_db}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)
END

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || echo "Warning: Migration failed or no migrations to run"

# Execute the main command (passed as arguments)
echo "Starting application..."
exec "$@"
