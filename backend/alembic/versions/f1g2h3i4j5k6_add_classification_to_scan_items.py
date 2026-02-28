"""add classification to scan items (filename_violations)

Revision ID: f1g2h3i4j5k6
Revises: e1f2g3h4i5j6
Create Date: 2026-02-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1g2h3i4j5k6'
down_revision: Union[str, None] = 'e1f2g3h4i5j6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('filename_violations')]

    if 'classification' not in columns:
        op.add_column(
            'filename_violations',
            sa.Column('classification', sa.String(20), nullable=False, server_default='product')
        )

    if 'classification_auto' not in columns:
        op.add_column(
            'filename_violations',
            sa.Column('classification_auto', sa.Boolean(), nullable=False, server_default='true')
        )

    # 기존 Attachment type 정규화: crack → patch
    op.execute("UPDATE attachments SET type = 'patch' WHERE type = 'crack'")
    # 미분류 → patch
    op.execute(
        "UPDATE attachments SET type = 'patch' "
        "WHERE type NOT IN ('patch', 'manual', 'language_pack', 'update')"
    )


def downgrade() -> None:
    op.drop_column('filename_violations', 'classification_auto')
    op.drop_column('filename_violations', 'classification')
