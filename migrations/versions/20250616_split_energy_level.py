"""split energy level column

Revision ID: 20250616_split_energy_level
Revises: 20250615_companion
Create Date: 2025-06-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '20250616_split_energy_level'
down_revision = '20250615_companion'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    session_columns = [col['name'] for col in inspector.get_columns('session')]

    if 'energy_level_before' not in session_columns:
        if 'energy_level' in session_columns:
            op.alter_column('session', 'energy_level', new_column_name='energy_level_before')
        else:
            op.add_column('session', sa.Column('energy_level_before', sa.Integer(), nullable=True))

    if 'energy_level_after' not in session_columns:
        op.add_column('session', sa.Column('energy_level_after', sa.Integer(), nullable=True))

    # If energy_level still exists after operations, drop it as obsolete
    session_columns = [col['name'] for col in inspector.get_columns('session')]
    if 'energy_level' in session_columns:
        op.drop_column('session', 'energy_level')


def downgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    session_columns = [col['name'] for col in inspector.get_columns('session')]

    if 'energy_level_after' in session_columns:
        op.drop_column('session', 'energy_level_after')

    if 'energy_level_before' in session_columns:
        if 'energy_level' not in session_columns:
            op.alter_column('session', 'energy_level_before', new_column_name='energy_level')
        else:
            op.drop_column('session', 'energy_level_before')
