"""add_attachments_field_to_posts_table

Revision ID: af4ad8a75237
Revises: c1d2e3f4g5h6
Create Date: 2025-12-29 08:56:49.764003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af4ad8a75237'
down_revision: Union[str, None] = 'c1d2e3f4g5h6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add attachments column to posts table
    op.add_column('posts', sa.Column('attachments', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove attachments column from posts table
    op.drop_column('posts', 'attachments')
