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

# Database tables will be created automatically by SQLAlchemy
echo "Database tables will be created by SQLAlchemy Base.metadata.create_all()"

# Ensure critical schema columns exist (classification columns for scan items)
echo "Checking schema columns..."
python3 << 'PYEND'
import os
import psycopg2

database_url = os.getenv('DATABASE_URL', '')
if not database_url:
    postgres_user = os.getenv('POSTGRES_USER', 'postgres')
    postgres_password = os.getenv('POSTGRES_PASSWORD', 'password')
    postgres_db = os.getenv('POSTGRES_DB', 'myappstore')
    database_url = f"postgresql://{postgres_user}:{postgres_password}@db:5432/{postgres_db}"

try:
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    # Check if filename_violations table exists
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'filename_violations')")
    table_exists = cur.fetchone()[0]
    if table_exists:
        cur.execute("ALTER TABLE filename_violations ADD COLUMN IF NOT EXISTS classification VARCHAR(20) NOT NULL DEFAULT 'product'")
        cur.execute("ALTER TABLE filename_violations ADD COLUMN IF NOT EXISTS classification_auto BOOLEAN NOT NULL DEFAULT true")
        conn.commit()
        print("✓ Schema columns verified")
    else:
        print("Note: filename_violations table not yet created (will be created by SQLAlchemy)")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Note: Schema check skipped: {e}")
PYEND

# config.json 파일이 없으면 config.sample.json에서 복사
CONFIG_DIR="${CONFIG_DATA_DIR:-/app/data}"
if [ ! -f "$CONFIG_DIR/config.json" ] && [ -f "$CONFIG_DIR/config.sample.json" ]; then
    echo "Creating config.json from config.sample.json..."
    cp "$CONFIG_DIR/config.sample.json" "$CONFIG_DIR/config.json"
    echo "✓ config.json created successfully"
elif [ ! -f "$CONFIG_DIR/config.json" ]; then
    echo "Warning: Neither config.json nor config.sample.json found in $CONFIG_DIR"
fi

# Execute the main command (passed as arguments)
echo "Starting application..."
exec "$@"
