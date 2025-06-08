"""Seed initial skills
Revision ID: 20250607_seed_skills
Revises: 20250529_add_product_images
Create Date: 2025-06-07 09:24:28.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '20250607_seed_skills'
down_revision = '20250529_add_product_images'
branch_labels = None
depends_on = None

def upgrade():
    skill_table = table(
        'skill',
        column('name', sa.String(length=80)),
        column('category', sa.String(length=80)),
        column('description', sa.Text)
    )
    op.bulk_insert(skill_table, [
        {'name': 'Manejo de la Cometa en Tierra', 'category': 'Basic', 'description': 'Dominar la cometa antes de entrar al agua'},
        {'name': 'Relanzar la Cometa en el Agua', 'category': 'Basic', 'description': 'Autonomía completa en el agua'},
        {'name': 'Equilibrio y Traslación en Board (Knee & Stand)', 'category': 'Basic', 'description': 'Confianza total en la tabla'},
        {'name': 'Primeros Deslizamientos de Pie (Wing Surfing)', 'category': 'Basic', 'description': 'Dominio del wing surfing'},
        {'name': 'Simulación de Foil (Preparación Mental/Física)', 'category': 'Basic', 'description': 'Preparación para el foil'},
        {'name': 'Primeros Vuelos en Foil (First Flights)', 'category': 'Intermediate', 'description': 'Vuelos controlados y repetibles'},
        {'name': 'Foiling Sostenido y Bordeo Upwind', 'category': 'Intermediate', 'description': 'Vuelos de más de 30 segundos'},
        {'name': 'Giros Downwind (Jibes)', 'category': 'Intermediate', 'description': 'Cambios de dirección fluidos'},
        {'name': 'Viradas Upwind (Tacks) & Switch Stance', 'category': 'Intermediate', 'description': 'Navegación en ambas direcciones'},
        {'name': 'Control Avanzado de Altura y Velocidad', 'category': 'Intermediate', 'description': 'Eficiencia y control fino'},
        {'name': 'Surfear Swell & Olas', 'category': 'Advanced', 'description': 'Aprovechar energía natural del agua'},
        {'name': 'Big Air & Freestyle', 'category': 'Advanced', 'description': 'Maniobras aéreas controladas'},
        {'name': 'Downwind Extremo & Aventura', 'category': 'Advanced', 'description': 'Navegación de larga distancia'},
        {'name': 'Racing & Performance Pro', 'category': 'Advanced', 'description': 'Máximo rendimiento competitivo'},
        {'name': 'Trucos y Técnicas Especiales', 'category': 'Advanced', 'description': 'Maestría técnica completa'},
    ])

def downgrade():
    op.execute(
        "DELETE FROM skill WHERE name IN ("
        "'Manejo de la Cometa en Tierra', 'Relanzar la Cometa en el Agua', "
        "'Equilibrio y Traslación en Board (Knee & Stand)', 'Primeros Deslizamientos de Pie (Wing Surfing)', "
        "'Simulación de Foil (Preparación Mental/Física)', 'Primeros Vuelos en Foil (First Flights)', "
        "'Foiling Sostenido y Bordeo Upwind', 'Giros Downwind (Jibes)', "
        "'Viradas Upwind (Tacks) & Switch Stance', 'Control Avanzado de Altura y Velocidad', "
        "'Surfear Swell & Olas', 'Big Air & Freestyle', 'Downwind Extremo & Aventura', "
        "'Racing & Performance Pro', 'Trucos y Técnicas Especiales'"
        ")"
    )
