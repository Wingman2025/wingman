"""add companion app tables

Revision ID: 20250615_companion
Revises: 20250615_seed_levels
Create Date: 2025-06-15 13:32:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '20250615_companion'
down_revision = '20250615_seed_levels'
branch_labels = None
depends_on = None

def upgrade():
    # Get connection and inspector to check existing tables
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()
    
    # Create goal_template table if it doesn't exist
    if 'goal_template' not in existing_tables:
        op.create_table('goal_template',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('category', sa.String(length=50), nullable=False),
            sa.Column('difficulty_level', sa.String(length=20), nullable=False),
            sa.Column('estimated_duration_days', sa.Integer(), nullable=True),
            sa.Column('icon', sa.String(length=50), nullable=True),
            sa.Column('target_type', sa.String(length=20), nullable=False),
            sa.Column('default_target_value', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create user_goal table if it doesn't exist
    if 'user_goal' not in existing_tables:
        op.create_table('user_goal',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('goal_template_id', sa.Integer(), nullable=True),
            sa.Column('custom_title', sa.String(length=200), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('target_value', sa.Integer(), nullable=False),
            sa.Column('current_progress', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('start_date', sa.DateTime(), nullable=True),
            sa.Column('target_date', sa.DateTime(), nullable=True),
            sa.Column('completed_date', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['goal_template_id'], ['goal_template.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create badge table if it doesn't exist
    if 'badge' not in existing_tables:
        op.create_table('badge',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('icon', sa.String(length=50), nullable=True),
            sa.Column('category', sa.String(length=50), nullable=False),
            sa.Column('criteria', sa.Text(), nullable=True),
            sa.Column('points_value', sa.Integer(), nullable=True),
            sa.Column('rarity', sa.String(length=20), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create user_badge table if it doesn't exist
    if 'user_badge' not in existing_tables:
        op.create_table('user_badge',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('badge_id', sa.Integer(), nullable=False),
            sa.Column('unlocked_at', sa.DateTime(), nullable=True),
            sa.Column('progress_context', sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(['badge_id'], ['badge.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge')
        )
    
    # Add new columns to session table if they don't exist
    try:
        session_columns = [col['name'] for col in inspector.get_columns('session')]
        
        if 'flight_duration' not in session_columns:
            op.add_column('session', sa.Column('flight_duration', sa.Integer(), nullable=True))
        if 'upwind_distance' not in session_columns:
            op.add_column('session', sa.Column('upwind_distance', sa.Integer(), nullable=True))
        if 'falls_count' not in session_columns:
            op.add_column('session', sa.Column('falls_count', sa.Integer(), nullable=True))
        if 'max_speed' not in session_columns:
            op.add_column('session', sa.Column('max_speed', sa.Float(), nullable=True))
        if 'avg_speed' not in session_columns:
            op.add_column('session', sa.Column('avg_speed', sa.Float(), nullable=True))
        if 'tricks_attempted' not in session_columns:
            op.add_column('session', sa.Column('tricks_attempted', sa.Integer(), nullable=True))
        if 'tricks_landed' not in session_columns:
            op.add_column('session', sa.Column('tricks_landed', sa.Integer(), nullable=True))
        if 'water_time' not in session_columns:
            op.add_column('session', sa.Column('water_time', sa.Integer(), nullable=True))
        if 'preparation_time' not in session_columns:
            op.add_column('session', sa.Column('preparation_time', sa.Integer(), nullable=True))
        if 'session_type' not in session_columns:
            op.add_column('session', sa.Column('session_type', sa.String(length=50), nullable=True))
        if 'motivation_level' not in session_columns:
            op.add_column('session', sa.Column('motivation_level', sa.Integer(), nullable=True))
        if 'energy_level' not in session_columns:
            op.add_column('session', sa.Column('energy_level', sa.Integer(), nullable=True))
        if 'goals_worked' not in session_columns:
            op.add_column('session', sa.Column('goals_worked', sa.JSON(), nullable=True))
        if 'personal_records' not in session_columns:
            op.add_column('session', sa.Column('personal_records', sa.JSON(), nullable=True))
    except Exception as e:
        print(f"Warning: Could not add session columns: {e}")

def downgrade():
    # Remove added columns from session
    try:
        op.drop_column('session', 'personal_records')
        op.drop_column('session', 'goals_worked')
        op.drop_column('session', 'energy_level')
        op.drop_column('session', 'motivation_level')
        op.drop_column('session', 'session_type')
        op.drop_column('session', 'preparation_time')
        op.drop_column('session', 'water_time')
        op.drop_column('session', 'tricks_landed')
        op.drop_column('session', 'tricks_attempted')
        op.drop_column('session', 'avg_speed')
        op.drop_column('session', 'max_speed')
        op.drop_column('session', 'falls_count')
        op.drop_column('session', 'upwind_distance')
        op.drop_column('session', 'flight_duration')
    except:
        pass
    
    # Drop tables
    op.drop_table('user_badge')
    op.drop_table('badge')
    op.drop_table('user_goal')
    op.drop_table('goal_template')
