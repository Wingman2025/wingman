"""add target_date and progress fields to goal

Revision ID: 20250614_add_goal_fields
Revises: 70ddc73ff13b
Create Date: 2025-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = '20250614_add_goal_fields'
down_revision = '70ddc73ff13b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('goal', sa.Column('target_date', sa.DateTime(), nullable=True))
    op.add_column('goal', sa.Column('progress', sa.Integer(), nullable=True, server_default='0'))
    op.execute('UPDATE goal SET target_date = due_date')


def downgrade():
    op.drop_column('goal', 'progress')
    op.drop_column('goal', 'target_date')
