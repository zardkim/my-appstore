"""add pg_trgm GIN indexes for product search and versions.product_id index

Revision ID: a1b2c3d4e5f7
Revises: f1g2h3i4j5k6
Create Date: 2026-08-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = 'f1g2h3i4j5k6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # products.title/subtitle/vendor에 대한 ILIKE '%검색어%' 검색이
    # pg_trgm GIN 인덱스 없이 시퀀셜 스캔으로 실행되고 있었음 (products.py의
    # 기존 주석과 달리 실제 인덱스는 존재하지 않았음)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    existing_indexes = {ix['name'] for ix in inspector.get_indexes('products')}

    if 'ix_products_title_trgm' not in existing_indexes:
        op.execute(
            "CREATE INDEX ix_products_title_trgm ON products "
            "USING gin (title gin_trgm_ops)"
        )
    if 'ix_products_subtitle_trgm' not in existing_indexes:
        op.execute(
            "CREATE INDEX ix_products_subtitle_trgm ON products "
            "USING gin (subtitle gin_trgm_ops)"
        )
    if 'ix_products_vendor_trgm' not in existing_indexes:
        op.execute(
            "CREATE INDEX ix_products_vendor_trgm ON products "
            "USING gin (vendor gin_trgm_ops)"
        )

    # versions.product_id는 FK이지만 Postgres는 FK 컬럼을 자동으로 인덱싱하지
    # 않음. 상품 상세조회/스캔 정리/rename 감지 등 대부분의 쿼리가 이 컬럼으로
    # 필터링하므로 versions 테이블이 커지면 풀스캔이 발생함
    existing_version_indexes = {ix['name'] for ix in inspector.get_indexes('versions')}
    if 'ix_versions_product_id' not in existing_version_indexes:
        op.create_index('ix_versions_product_id', 'versions', ['product_id'])


def downgrade() -> None:
    op.drop_index('ix_versions_product_id', table_name='versions')
    op.execute("DROP INDEX IF EXISTS ix_products_vendor_trgm")
    op.execute("DROP INDEX IF EXISTS ix_products_subtitle_trgm")
    op.execute("DROP INDEX IF EXISTS ix_products_title_trgm")
