"""add email to users

Revision ID: e1f2g3h4i5j6
Revises: 9c0d1e2f3a4b
Create Date: 2026-02-04 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f2g3h4i5j6'
down_revision: Union[str, None] = '9c0d1e2f3a4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add email column if it doesn't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'email' not in columns:
        op.add_column('users', sa.Column('email', sa.String(), nullable=True))
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'email')
