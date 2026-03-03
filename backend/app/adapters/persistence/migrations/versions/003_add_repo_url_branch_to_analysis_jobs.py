"""Add repo_url and branch to analysis_jobs table

Revision ID: 003
Revises: 002
Create Date: 2026-03-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add repo_url column to analysis_jobs table
    op.add_column(
        'analysis_jobs',
        sa.Column('repo_url', sa.String(length=500), nullable=True)
    )

    # Add branch column to analysis_jobs table
    op.add_column(
        'analysis_jobs',
        sa.Column('branch', sa.String(length=100), default='main', nullable=True)
    )


def downgrade() -> None:
    # Remove branch column from analysis_jobs table
    op.drop_column('analysis_jobs', 'branch')

    # Remove repo_url column from analysis_jobs table
    op.drop_column('analysis_jobs', 'repo_url')
