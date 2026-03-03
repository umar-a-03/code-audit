"""Add password_hash to clients table

Revision ID: 002
Revises: 001
Create Date: 2026-03-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password_hash column to clients table
    op.add_column(
        'clients',
        sa.Column('password_hash', sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    # Remove password_hash column from clients table
    op.drop_column('clients', 'password_hash')
