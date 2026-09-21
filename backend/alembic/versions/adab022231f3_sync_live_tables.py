"""sync live tables: activity_logs, product_videos, share_links

Revision ID: adab022231f3
Revises: b2c3d4e5f6a8
Create Date: 2026-09-21

이 세 테이블은 그동안 Alembic 밖에서 만들어지고 있었다
(main.py 의 Base.metadata.create_all() 과 entrypoint.sh 의 CREATE TABLE IF NOT EXISTS).
Alembic 을 스키마의 정본으로 삼기 위해 여기로 가져온다.

의도적으로 **추가만 한다**. 자동 생성에는 아래 파괴적 연산이 포함되어 있었으나 전부 제거했다:
  - drop_table('scan_history'), drop_table('unmatched_items')
      -> 죽은 테이블이지만 운영 데이터 확인 전까지 보류하기로 결정됨 (별도 이슈)
  - drop_index('ix_products_*_trgm'), drop_index('ix_versions_product_id')
      -> 모델에 선언할 수 없는 손수 만든 인덱스다. 실제로 필요하며 지우면 검색이 느려진다
  - drop_column('products','crawled_from')
      -> 죽은 컬럼이지만 운영 데이터 확인 전까지 보류

또한 entrypoint.sh 만 만들고 있던 trgm 인덱스 2개를 여기에 추가한다.
이름은 entrypoint.sh 와 동일하게 두어 기존 운영 DB 에서는 no-op 이 되도록 했다.

기존 운영 DB 는 이 테이블들을 이미 갖고 있으므로 inspector 가드로 건너뛴다
(e1f2g3h4i5j6 과 동일한 관례).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'adab022231f3'
down_revision = 'b2c3d4e5f6a8'
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    if not _has_table('activity_logs'):
        op.create_table('activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('resource_name', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_activity_logs_action'), 'activity_logs', ['action'], unique=False)
        op.create_index(op.f('ix_activity_logs_created_at'), 'activity_logs', ['created_at'], unique=False)
        op.create_index(op.f('ix_activity_logs_id'), 'activity_logs', ['id'], unique=False)

    if not _has_table('product_videos'):
        op.create_table('product_videos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_product_videos_id'), 'product_videos', ['id'], unique=False)
        op.create_index(op.f('ix_product_videos_product_id'), 'product_videos', ['product_id'], unique=False)

    if not _has_table('share_links'):
        op.create_table('share_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('password', sa.String(length=20), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('used_by_ip', sa.String(length=45), nullable=True),
        sa.Column('password_fail_count', sa.Integer(), nullable=True),
        sa.Column('note', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_share_links_created_by'), 'share_links', ['created_by'], unique=False)
        op.create_index(op.f('ix_share_links_id'), 'share_links', ['id'], unique=False)
        op.create_index(op.f('ix_share_links_product_id'), 'share_links', ['product_id'], unique=False)
        op.create_index(op.f('ix_share_links_token'), 'share_links', ['token'], unique=True)

    # entrypoint.sh 에만 있던 trgm 인덱스. 기존 DB 에는 이미 있으므로 IF NOT EXISTS.
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    op.execute(
        'CREATE INDEX IF NOT EXISTS idx_posts_title_trgm '
        'ON posts USING GIN (title gin_trgm_ops)'
    )
    op.execute(
        'CREATE INDEX IF NOT EXISTS idx_filename_violations_file_name_trgm '
        'ON filename_violations USING GIN (file_name gin_trgm_ops)'
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS idx_filename_violations_file_name_trgm')
    op.execute('DROP INDEX IF EXISTS idx_posts_title_trgm')
    if _has_table('share_links'):
        op.drop_table('share_links')
    if _has_table('product_videos'):
        op.drop_table('product_videos')
    if _has_table('activity_logs'):
        op.drop_table('activity_logs')
