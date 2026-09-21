"""drop dead tables: unmatched_items, scan_history, metadata_cache

Revision ID: e4a861c32785
Revises: adab022231f3
Create Date: 2026-09-21

세 테이블 모두 살아있는 코드에서 참조되지 않는다. 운영 DB 에서 행 수가
전부 0 임을 확인하고 제거한다.

  unmatched_items  v1.4.64(a21e9da)에서 모델·API 가 제거됐고 "데이터 삭제는
                   별도 판단 필요"로 테이블만 남아 있었다.
  scan_history     초기 커밋 이후 사용된 적이 없다. 실제 스캔 이력은
                   scheduler 가 scan_history.json 파일에 저장한다.
  metadata_cache   v1.4.64 에서 사용처가 제거됐다. "계획 5번에서 신뢰도
                   신호로 쓸 여지가 있어 유지"였으나, 계획 5번은
                   4727904 에서 규칙 기반 core/confidence.py 로 구현됐고
                   이 테이블을 쓰지 않았다. 보존 사유가 만료됐다.

운영 DB 실측 (2026-09-21):
  unmatched_items 0 / metadata_cache 0 / scan_history 0

downgrade 는 테이블을 되살리지 않는다. 죽은 테이블을 복원할 이유가 없고,
필요하면 이 리비전 이전 상태에서 다시 만들면 된다.
"""
from alembic import op
import sqlalchemy as sa

revision = 'e4a861c32785'
down_revision = 'adab022231f3'
branch_labels = None
depends_on = None

DEAD_TABLES = ('unmatched_items', 'scan_history', 'metadata_cache')


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    for table in DEAD_TABLES:
        if _has_table(table):
            op.drop_table(table)


def downgrade() -> None:
    # 죽은 테이블은 되살리지 않는다.
    pass
