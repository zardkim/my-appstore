#!/bin/bash
set -e

echo "Starting MyApp Store Backend..."

# Wait for database to be ready (using Python)
echo "Waiting for database..."
python3 << 'END'
import time
import psycopg2
import os
import sys

# Parse DATABASE_URL or use individual env vars
database_url = os.getenv('DATABASE_URL', '')
if database_url:
    print(f"Using DATABASE_URL: {database_url[:30]}...")
else:
    print("Using individual database env vars")
    database_url = f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'password')}@db:5432/{os.getenv('POSTGRES_DB', 'myappstore')}"

max_retries = 30
for i in range(max_retries):
    try:
        print(f"Attempt {i+1}/{max_retries} to connect to database...")
        conn = psycopg2.connect(database_url)
        conn.close()
        print("Database is ready!")
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
        if i < max_retries - 1:
            time.sleep(1)
        else:
            print("Failed to connect to database after 30 attempts")
            sys.exit(1)
END

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || echo "Warning: Migration failed or no migrations to run"

# Execute the main command (passed as arguments)
echo "Starting application..."
exec "$@"
