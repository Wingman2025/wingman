"""Add UserSkillStatus table

Revision ID: ad3be3ec7e1c
Revises: 20250607_seed_skills
Create Date: 2025-06-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ad3be3ec7e1c'
down_revision = '20250607_seed_skills'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_skill_status',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('skill_id', sa.Integer(), sa.ForeignKey('skill.id'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False)
    )


def downgrade():
    op.drop_table('user_skill_status')
