"""
create chat_message table

Revision ID: 20250607_create_chat_message
Revises: ad3be3ec7e1c
Create Date: 2025-06-07 15:35:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250607_create_chat_message'
down_revision = 'ad3be3ec7e1c'
branch_labels = None
depends_on = None

def upgrade():
    # Check if table already exists
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    
    if 'chat_message' not in inspector.get_table_names():
        op.create_table(
            'chat_message',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
            sa.Column('role', sa.String(length=10), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index(op.f('ix_chat_message_user_id_timestamp'), 'chat_message', ['user_id', 'timestamp'])

def downgrade():
    op.drop_index(op.f('ix_chat_message_user_id_timestamp'), table_name='chat_message')
    op.drop_table('chat_message')
