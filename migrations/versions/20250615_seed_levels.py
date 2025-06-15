"""Seed initial wingfoil levels

Revision ID: 20250615_seed_levels
Revises: 20250614_add_goal_fields
Create Date: 2025-06-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '20250615_seed_levels'
down_revision = '20250614_add_goal_fields'
branch_labels = None
depends_on = None


def upgrade():
    level_table = table(
        'level',
        column('code', sa.String(length=20)),
        column('name', sa.String(length=100)),
        column('description', sa.Text)
    )
    op.bulk_insert(level_table, [
        {'code': '1A', 'name': 'S.E.A, Gear, Setup, Safety', 'description': "Learn the basics of wing foiling equipment, safety protocols, and proper setup techniques. This foundational knowledge is essential before getting on the water."},
        {'code': '1B', 'name': 'Beach Wing Handling, Use of Handles', 'description': "Master the art of controlling your wing on land, understanding wind direction, and properly using the handles for maximum control and efficiency."},
        {'code': '1C', 'name': 'Beach Board Exercises, Knee Stand Up', 'description': "Practice balance and board control on land, including the crucial transition from kneeling to standing position that you'll use in your early water sessions."},
        {'code': '1D', 'name': 'Beach Self Rescue, R.O.W.', 'description': "Learn essential self-rescue techniques and the Rules of the Water (R.O.W.) to ensure your safety and the safety of others while wing foiling."},
        {'code': '1E', 'name': 'Flip Wing on Water, Enter and Exit with Full Gear', 'description': "Master the technique of flipping your wing on water and practice safely entering and exiting the water with all your equipment."},
        {'code': '2F', 'name': 'Knee on Board, Control Gear in Knees', 'description': "Learn to balance on your board while kneeling and control your wing effectively from this position, a crucial stepping stone to standing up."},
        {'code': '2G', 'name': 'Ride on Knees, Change Direction', 'description': "Master riding on your knees while controlling the wing, and practice changing direction smoothly while maintaining balance and control."},
        {'code': '2H', 'name': 'Ride Standing Up, Jibe with Wing/Feet', 'description': "Take the exciting step of standing up on your board while riding, and learn to perform basic jibes by coordinating your wing and foot movements."},
        {'code': '2I', 'name': 'Ride Cross & Upwind, Change Direction', 'description': "Develop the skills to ride across and against the wind, expanding your range and freedom on the water, while mastering direction changes."},
        {'code': '3J', 'name': 'Pumping, Getting on the Foil', 'description': "Learn the crucial technique of pumping to generate lift and get your board up on the foil, experiencing the magical feeling of flying above the water."},
        {'code': '3K', 'name': 'Control Direction & Speed Foiling', 'description': "Master the art of controlling your direction and speed while foiling, developing the fine motor skills needed for smooth, controlled flight."},
        {'code': '3L', 'name': 'Toeside, Changing Foot', 'description': "Learn to ride toeside and practice changing your foot position while maintaining balance and control on the foil."},
        {'code': '3M', 'name': 'Jibe, Tack', 'description': "Master the techniques of jibing and tacking while on the foil, allowing you to change direction smoothly without losing your foiling state."},
        {'code': '3N', 'name': 'Catching Swell, Free Pumping', 'description': "Develop the skills to catch and ride swells, and practice free pumping to maintain your foil without relying on the wing's power."},
        {'code': '4O', 'name': 'Jump Basic', 'description': "Learn the fundamentals of jumping with your wing foil, taking your first steps into the exciting world of aerial maneuvers."},
        {'code': '4P', 'name': 'Power Jibe', 'description': "Master the dynamic power jibe, a more aggressive and efficient way to change direction while maintaining speed and control."},
        {'code': '4Q', 'name': 'Jump with Rotation', 'description': "Take your jumping skills to the next level by adding rotations, adding style and flair to your aerial maneuvers."},
        {'code': '4R', 'name': 'Riding on Waves', 'description': "Develop the skills to ride ocean waves with your wing foil, combining the thrill of surfing with the freedom of wing foiling."},
        {'code': '4S', 'name': 'Ride with Harness', 'description': "Learn to use a harness while wing foiling, reducing arm fatigue and allowing for longer, more comfortable sessions."},
        {'code': '4T', 'name': 'Jump with Harness', 'description': "Master the advanced technique of jumping while using a harness, combining two complex skills for maximum performance."},
    ])


def downgrade():
    op.execute(
        "DELETE FROM level WHERE code IN ("
        "'1A', '1B', '1C', '1D', '1E',"
        "'2F', '2G', '2H', '2I',"
        "'3J', '3K', '3L', '3M', '3N',"
        "'4O', '4P', '4Q', '4R', '4S', '4T'"
        ")"
    )
