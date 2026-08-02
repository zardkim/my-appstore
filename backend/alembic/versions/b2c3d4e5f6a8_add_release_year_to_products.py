"""add release_year to products

Revision ID: b2c3d4e5f6a8
Revises: a1b2c3d4e5f7
Create Date: 2026-08-02 03:00:00.000000

"""
import os
import re
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a8'
down_revision: Union[str, None] = 'a1b2c3d4e5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# app.core.parser.FilenameParser._extract_year와 동일한 패턴을 그대로 복사.
# 마이그레이션은 app 모듈을 import하면 안 되므로(설정/엔진을 끌어와 배포 환경에서
# 깨질 수 있음) 정규식을 여기 인라인으로 둔다.
_YEAR_PATTERN = re.compile(r'(?<!\d)((?:19|20)\d{2})(?!\d)')


def _extract_year(text: str):
    if not text:
        return None
    match = _YEAR_PATTERN.search(text)
    return int(match.group(1)) if match else None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('products')]

    if 'release_year' not in columns:
        op.add_column('products', sa.Column('release_year', sa.Integer(), nullable=True))

    existing_indexes = {ix['name'] for ix in inspector.get_indexes('products')}
    if 'ix_products_release_year' not in existing_indexes:
        op.create_index('ix_products_release_year', 'products', ['release_year'])

    # 기존 행 backfill: title에서 우선 추출, 실패 시 folder_path의 폴더명에서 재시도
    # (auto_matcher.py의 get_product_version_signature와 동일한 폴백 순서)
    products_table = sa.table(
        'products',
        sa.column('id', sa.Integer),
        sa.column('title', sa.String),
        sa.column('folder_path', sa.String),
        sa.column('release_year', sa.Integer),
    )

    rows = conn.execute(sa.select(
        products_table.c.id, products_table.c.title, products_table.c.folder_path
    )).fetchall()

    for row in rows:
        year = _extract_year(row.title)
        if not year and row.folder_path:
            folder_name = os.path.basename(row.folder_path.rstrip('/\\'))
            year = _extract_year(folder_name)
        if year:
            conn.execute(
                products_table.update()
                .where(products_table.c.id == row.id)
                .values(release_year=year)
            )


def downgrade() -> None:
    op.drop_index('ix_products_release_year', table_name='products')
    op.drop_column('products', 'release_year')
