"""Add skill tracking fields to User

Revision ID: add_user_skill_fields
Revises: 20250529_add_product_images
Create Date: 2025-06-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_user_skill_fields'
down_revision = '20250529_add_product_images'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('skills_in_progress', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('skills_mastered', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('skills_mastered')
        batch_op.drop_column('skills_in_progress')
