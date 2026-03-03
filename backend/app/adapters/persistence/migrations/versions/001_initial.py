"""Initial migration

Creates all base tables for the Code Audit Platform.

Revision ID: 001
Revises:
Create Date: 2026-02-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('oauth_provider', sa.String(length=50), nullable=True),
        sa.Column('oauth_id', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clients_email'), 'clients', ['email'], unique=True)
    op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_client_id'), 'users', ['client_id'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('key_name', sa.String(length=100), nullable=True),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('key_hash', sa.String(length=64), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_client_id'), 'api_keys', ['client_id'], unique=False)
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=True)
    op.create_index(op.f('ix_api_keys_id'), 'api_keys', ['id'], unique=False)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('repo_url', sa.String(length=500), nullable=True),
        sa.Column('repo_branch', sa.String(length=100), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_client_id'), 'projects', ['client_id'], unique=False)
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)

    # Create analysis_jobs table
    op.create_table(
        'analysis_jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('rq_job_id', sa.String(length=100), nullable=True),
        sa.Column('worker_name', sa.String(length=100), nullable=True),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_jobs_client_id'), 'analysis_jobs', ['client_id'], unique=False)
    op.create_index(op.f('ix_analysis_jobs_id'), 'analysis_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_analysis_jobs_project_id'), 'analysis_jobs', ['project_id'], unique=False)
    op.create_index(op.f('ix_analysis_jobs_rq_job_id'), 'analysis_jobs', ['rq_job_id'], unique=False)
    op.create_index(op.f('ix_analysis_jobs_status'), 'analysis_jobs', ['status'], unique=False)

    # Create analysis_results table
    op.create_table(
        'analysis_results',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=False),
        sa.Column('summary', sa.JSON(), nullable=False),
        sa.Column('code_quality', sa.JSON(), nullable=True),
        sa.Column('rule_violations', sa.JSON(), nullable=True),
        sa.Column('security_issues', sa.JSON(), nullable=True),
        sa.Column('ai_report', sa.JSON(), nullable=True),
        sa.Column('file_results', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['analysis_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id')
    )
    op.create_index(op.f('ix_analysis_results_client_id'), 'analysis_results', ['client_id'], unique=False)
    op.create_index(op.f('ix_analysis_results_id'), 'analysis_results', ['id'], unique=False)
    op.create_index(op.f('ix_analysis_results_job_id'), 'analysis_results', ['job_id'], unique=True)

    # Create batch_jobs table
    op.create_table(
        'batch_jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('total_jobs', sa.Integer(), nullable=True),
        sa.Column('completed_jobs', sa.Integer(), nullable=True),
        sa.Column('failed_jobs', sa.Integer(), nullable=True),
        sa.Column('job_ids', sa.ARRAY(sa.UUID()), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_batch_jobs_client_id'), 'batch_jobs', ['client_id'], unique=False)
    op.create_index(op.f('ix_batch_jobs_id'), 'batch_jobs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_batch_jobs_id'), table_name='batch_jobs')
    op.drop_index(op.f('ix_batch_jobs_client_id'), table_name='batch_jobs')
    op.drop_table('batch_jobs')

    op.drop_index(op.f('ix_analysis_results_job_id'), table_name='analysis_results')
    op.drop_index(op.f('ix_analysis_results_id'), table_name='analysis_results')
    op.drop_index(op.f('ix_analysis_results_client_id'), table_name='analysis_results')
    op.drop_table('analysis_results')

    op.drop_index(op.f('ix_analysis_jobs_status'), table_name='analysis_jobs')
    op.drop_index(op.f('ix_analysis_jobs_rq_job_id'), table_name='analysis_jobs')
    op.drop_index(op.f('ix_analysis_jobs_project_id'), table_name='analysis_jobs')
    op.drop_index(op.f('ix_analysis_jobs_id'), table_name='analysis_jobs')
    op.drop_index(op.f('ix_analysis_jobs_client_id'), table_name='analysis_jobs')
    op.drop_table('analysis_jobs')

    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_client_id'), table_name='projects')
    op.drop_table('projects')

    op.drop_index(op.f('ix_api_keys_id'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_key_hash'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_client_id'), table_name='api_keys')
    op.drop_table('api_keys')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_client_id'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_clients_id'), table_name='clients')
    op.drop_index(op.f('ix_clients_email'), table_name='clients')
    op.drop_table('clients')
