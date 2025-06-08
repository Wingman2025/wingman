"""add index on chat_message.session_id

Revision ID: a9f6525ebfb1
Revises: dfbeffe02eb5
Create Date: 2025-06-09 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a9f6525ebfb1'
down_revision = 'dfbeffe02eb5'
branch_labels = None
depends_on = None

def upgrade():
    op.create_index('ix_chat_message_session_id', 'chat_message', ['session_id'])


def downgrade():
    op.drop_index('ix_chat_message_session_id', table_name='chat_message')
