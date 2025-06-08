"""add chat message model
Revision ID: 20250608_add_chat_message
Revises: ad3be3ec7e1c
Create Date: 2025-06-08
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250608_add_chat_message'
down_revision = 'ad3be3ec7e1c'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'chat_message',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('role', sa.String(length=10), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True, server_default=sa.func.now())
    )


def downgrade():
    op.drop_table('chat_message')
