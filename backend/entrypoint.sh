#!/bin/bash
set -e

echo "Starting MyApp Store Backend..."

# Wait for database to be ready (using Python)
echo "Waiting for database..."
python << END
import time
import psycopg2
import os
import sys

max_retries = 30
for i in range(max_retries):
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'db'),
            port=os.getenv('DATABASE_PORT', '5432'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'password'),
            database=os.getenv('POSTGRES_DB', 'myappstore')
        )
        conn.close()
        print("Database is ready!")
        sys.exit(0)
    except psycopg2.OperationalError:
        if i < max_retries - 1:
            time.sleep(1)
        else:
            print("Failed to connect to database")
            sys.exit(1)
END

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || echo "Warning: Migration failed or no migrations to run"

# Execute the main command (passed as arguments)
echo "Starting application..."
exec "$@"
