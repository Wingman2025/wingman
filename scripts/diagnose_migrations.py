#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el estado de migraciones en Railway
"""
import os
import sys
from app import app
from backend.models.legacy import db
from sqlalchemy.engine.reflection import Inspector
from flask_migrate import current
# Ensure project root in sys.path
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def diagnose_migrations():
    """Diagnostica el estado actual de migraciones y tablas"""
    
    with app.app_context():
        print("🔍 DIAGNÓSTICO DE MIGRACIONES", flush=True)
        print("=" * 50, flush=True)
        
        # Detectar entorno
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_STATIC_URL')
        print(f"🌍 Entorno: {'Railway' if is_railway else 'Local'}", flush=True)
        print(f"📊 Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'No configurada')[:50]}...", flush=True)
        
        try:
            # Verificar conexión a la base de datos
            print("\n🔗 Verificando conexión a la base de datos...", flush=True)
            db.session.execute(db.text('SELECT 1'))
            print("✅ Conexión exitosa", flush=True)
            
            # Obtener migración actual
            print("\n📋 Migración actual:", flush=True)
            try:
                current_migration = current()
                if current_migration:
                    print(f"✅ Migración actual: {current_migration}", flush=True)
                else:
                    print("❌ No hay migración actual aplicada", flush=True)
            except Exception as e:
                print(f"❌ Error obteniendo migración actual: {e}", flush=True)
            
            # Verificar tablas existentes
            print("\n🗃️  Tablas existentes:", flush=True)
            inspector = Inspector.from_engine(db.engine)
            tables = inspector.get_table_names()
            
            companion_tables = ['goal_template', 'user_goal', 'badge', 'user_badge']
            for table in companion_tables:
                status = "✅" if table in tables else "❌"
                print(f"{status} {table}", flush=True)
            
            # Verificar columnas de session si existe
            if 'session' in tables:
                print(f"\n📊 Columnas de tabla 'session':", flush=True)
                columns = inspector.get_columns('session')
                session_new_columns = ['flight_duration', 'upwind_distance', 'falls_count', 'max_speed']
                for col_name in session_new_columns:
                    has_column = any(col['name'] == col_name for col in columns)
                    status = "✅" if has_column else "❌"
                    print(f"{status} {col_name}", flush=True)
            
            # Verificar datos en tablas companion
            print(f"\n📈 Datos en tablas companion:", flush=True)
            if 'goal_template' in tables:
                from backend.models.legacy import GoalTemplate, Badge
                template_count = GoalTemplate.query.count()
                badge_count = Badge.query.count()
                print(f"📋 GoalTemplate: {template_count} registros", flush=True)
                print(f"🏆 Badge: {badge_count} registros", flush=True)
            else:
                print("❌ Tablas companion no existen", flush=True)
                
        except Exception as e:
            print(f"❌ Error en diagnóstico: {e}", flush=True)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    diagnose_migrations()
