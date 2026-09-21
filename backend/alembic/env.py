from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database import Base # Import Base from your app's database module
import app.models # Import all models to ensure Base.metadata is populated

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata # Set target_metadata to your Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# ── autogenerate / check 에서 제외할 대상 ──────────────────────────────
#
# alembic check 를 CI 가드로 쓰려면, 모델과 DB 가 "의도적으로" 다른 부분을
# 차이로 보고하지 않아야 한다. 아래 두 부류가 그렇다.

# 1) 모델에 선언할 수 없는 손수 만든 인덱스.
#    GIN + gin_trgm_ops 는 SQLAlchemy 모델로 표현하지 않고 마이그레이션에서
#    raw SQL 로 만든다. autogenerate 는 이것을 "모델에 없는 인덱스"로 보고
#    drop_index 를 제안하는데, 지우면 검색이 시퀀셜 스캔으로 돌아간다.
IGNORED_INDEXES = {
    "ix_products_title_trgm",
    "ix_products_subtitle_trgm",
    "ix_products_vendor_trgm",
    "idx_products_title_trgm",
    "idx_products_subtitle_trgm",
    "idx_products_vendor_trgm",
    "idx_posts_title_trgm",
    "idx_filename_violations_file_name_trgm",
    "ix_versions_product_id",
}

# 2) 제외할 테이블.
#    unmatched_items / scan_history / metadata_cache 는 운영 DB 에서 행 수가
#    0 인 것을 확인하고 마이그레이션으로 제거했으므로 더 이상 예외가 필요 없다.
#    비워 두되 구조는 남긴다 - 같은 상황이 또 생기면 여기에 이유와 함께 추가한다.
IGNORED_TABLES = set()

# 3) 모델에서는 뺐지만 DB 컬럼은 남겨두기로 한 것. (테이블, 컬럼) 쌍.
#    products.crawled_from 은 값을 쓰는 코드가 없었지만(v1.4.74 에서 모델/스키마
#    필드만 제거), 운영 데이터 확인 전까지 DROP COLUMN 하지 않는다.
IGNORED_COLUMNS = {
    ("products", "crawled_from"),
}


def include_object(object, name, type_, reflected, compare_to):
    """autogenerate / check 대상에서 의도적 예외를 걸러낸다.

    여기에 무언가를 추가할 때는 반드시 이유를 남길 것. 이 필터가 넓어질수록
    alembic check 의 가드 효과가 약해진다.
    """
    if type_ == "table" and name in IGNORED_TABLES:
        return False
    if type_ == "index" and name in IGNORED_INDEXES:
        return False
    if type_ == "column":
        table = getattr(object, "table", None)
        if table is not None and (table.name, name) in IGNORED_COLUMNS:
            return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = os.environ.get("DATABASE_URL") # Get DATABASE_URL from environment
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get DATABASE_URL from environment for online mode
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=os.environ.get("DATABASE_URL") # Pass DATABASE_URL directly
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
