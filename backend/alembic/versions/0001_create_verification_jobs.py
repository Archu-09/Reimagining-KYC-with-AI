"""Create verification_jobs table

Revision ID: 0001_create_verification_jobs
Revises: 
Create Date: 2025-11-16
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_verification_jobs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'verification_jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('status', sa.String(), nullable=True, server_default='pending'),
        sa.Column('callback_url', sa.String(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.Column('updated_at', sa.String(), nullable=True),
        sa.Column('manual_review', sa.String(), nullable=True),
        sa.Column('reviewer', sa.String(), nullable=True),
        sa.Column('review_comments', sa.String(), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=True),
    )


def downgrade():
    op.drop_table('verification_jobs')
