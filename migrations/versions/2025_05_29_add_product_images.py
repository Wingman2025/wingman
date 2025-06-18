"""
Add ProductImage table for multiple images per product
Revision ID: 20250529_add_product_images
Revises: fbc2834a872d
Create Date: 2025-05-29
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250529_add_product_images'
down_revision = 'fbc2834a872d'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'product_image',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
    )

def downgrade():
    op.drop_table('product_image')
