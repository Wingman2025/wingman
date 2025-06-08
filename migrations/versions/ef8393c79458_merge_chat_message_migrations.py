"""merge chat message migrations

Revision ID: ef8393c79458
Revises: 20250607_create_chat_message, 20250608_add_chat_message
Create Date: 2025-06-07 23:51:35.141228

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef8393c79458'
down_revision = ('20250607_create_chat_message', '20250608_add_chat_message')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
