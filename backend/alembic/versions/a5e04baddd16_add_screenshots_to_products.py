"""add_screenshots_to_products

Revision ID: a5e04baddd16
Revises: 2119d6102bff
Create Date: 2025-12-19 14:47:36.313701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5e04baddd16'
down_revision: Union[str, None] = '2119d6102bff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add screenshots JSON column
    op.add_column('products', sa.Column('screenshots', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove screenshots column
    op.drop_column('products', 'screenshots')
