"""Feat: Add reset password

Revision ID: aaaf4ed0b3f5
Revises: 
Create Date: 2024-02-10 15:41:54.664516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaaf4ed0b3f5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(table_name='user_table', column_name='user_name')
    op.add_column(table_name='user_table', column=sa.Column('password_reset_hash', sa.String))


def downgrade() -> None:
    pass
