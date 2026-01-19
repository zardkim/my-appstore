"""add_patch_links_to_products

Revision ID: 8a9b0c1d2e3f
Revises: 7fa5752a7f32
Create Date: 2026-01-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8a9b0c1d2e3f'
down_revision: Union[str, None] = '7fa5752a7f32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add patch_links column to products table (JSON array for storing links)
    op.add_column('products', sa.Column('patch_links', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'patch_links')
