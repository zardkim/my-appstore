"""add_subtitle_to_products

Revision ID: 9bd8279ddfa2
Revises: b6b8b55b4309
Create Date: 2025-12-23 11:18:20.982517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bd8279ddfa2'
down_revision: Union[str, None] = 'b6b8b55b4309'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('products', sa.Column('subtitle', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'subtitle')
