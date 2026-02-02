"""add_installation_info_to_products

Revision ID: 9c0d1e2f3a4b
Revises: 8a9b0c1d2e3f
Create Date: 2026-01-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9c0d1e2f3a4b'
down_revision: Union[str, None] = '8a9b0c1d2e3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add installation_info column to products table (JSON for storing installation details)
    op.add_column('products', sa.Column('installation_info', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'installation_info')
