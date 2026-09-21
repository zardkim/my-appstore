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

# ── 스키마 마이그레이션 (Alembic 이 정본) ────────────────────────────────
#
# 예전에는 이 자리에서 ALTER TABLE / CREATE INDEX 를 직접 실행하고
# main.py 가 Base.metadata.create_all() 과 ALTER 안전망을 돌렸다.
# 스키마 정본이 세 곳으로 갈라져 실제로 장애가 났었다
# (v1.4.68: products.release_year 가 배포에 반영되지 않아 목록 조회 500).
#
# 기존 배포 DB 는 create_all() 로 만들어져 alembic_version 이 없다.
# 그 상태로 upgrade 를 돌리면 첫 리비전에서
# "relation \"products\" already exists" 로 죽으므로,
# DB 상태를 보고 stamp/upgrade 를 자동으로 고른다.
echo "Running database migrations (Alembic)..."

# alembic/env.py 는 os.environ["DATABASE_URL"] 을 직접 읽는다.
if [ -z "${DATABASE_URL:-}" ]; then
    export DATABASE_URL="postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-password}@db:5432/${POSTGRES_DB:-myappstore}"
    echo "  DATABASE_URL not set - constructed from individual vars"
fi

MIGRATION_MODE=$(python3 << 'PYEND'
import os
from sqlalchemy import create_engine, inspect

engine = create_engine(os.environ["DATABASE_URL"])
with engine.connect() as conn:
    insp = inspect(conn)
    tables = set(insp.get_table_names())

    if "alembic_version" in tables:
        print("upgrade")
    elif not tables:
        print("fresh")
    else:
        # create_all() 로 만들어진 기존 DB. head 로 stamp 하려면 스키마가
        # 실제로 head 와 같아야 한다. 최근 리비전이 추가한 것들을 표본으로
        # 확인해서, 하나라도 없으면 조용히 잘못 stamp 하지 않고 멈춘다.
        missing = []
        for t in ("activity_logs", "product_videos", "share_links"):
            if t not in tables:
                missing.append(f"table:{t}")
        def cols(t):
            return {c["name"] for c in insp.get_columns(t)} if t in tables else set()
        if "release_year" not in cols("products"):
            missing.append("column:products.release_year")
        if "email" not in cols("users"):
            missing.append("column:users.email")
        if "classification" not in cols("filename_violations"):
            missing.append("column:filename_violations.classification")
        print("stamp" if not missing else "outdated:" + ",".join(missing))
PYEND
)

case "$MIGRATION_MODE" in
    fresh)
        echo "  Empty database - creating schema from migrations"
        alembic upgrade head
        ;;
    stamp)
        echo "  Existing schema without alembic_version (legacy create_all deployment)"
        echo "  -> stamping head without running SQL, then applying any pending migrations"
        alembic stamp head
        alembic upgrade head
        ;;
    upgrade)
        echo "  Applying pending migrations"
        alembic upgrade head
        ;;
    outdated:*)
        echo "✗ ERROR: 기존 DB 가 최신 스키마보다 오래되었습니다."
        echo "  누락: ${MIGRATION_MODE#outdated:}"
        echo ""
        echo "  이 DB 는 자동으로 stamp 할 수 없습니다. 잘못 stamp 하면"
        echo "  실제로는 없는 컬럼을 있다고 기록하게 됩니다."
        echo "  v1.4.74 이미지로 한 번 기동해 스키마를 맞춘 뒤 다시 시도하세요."
        exit 1
        ;;
    *)
        echo "✗ ERROR: 마이그레이션 모드를 판정하지 못했습니다: ${MIGRATION_MODE}"
        exit 1
        ;;
esac

echo "✓ Database schema is up to date"

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
