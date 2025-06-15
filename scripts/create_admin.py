from app import db
from backend.models.legacy import User
from werkzeug.security import generate_password_hash
# Ensure project root in sys.path
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Cambia estos valores según tus necesidades
USERNAME = "admin"
EMAIL = "admin@tudominio.com"
PASSWORD = "TuPasswordSeguro"
NAME = "Administrador"

# Verifica si ya existe
admin = User.query.filter_by(username=USERNAME).first()
if admin:
    print(f"El usuario admin '{USERNAME}' ya existe.")
else:
    admin = User(
        username=USERNAME,
        email=EMAIL,
        password=generate_password_hash(PASSWORD),
        name=NAME,
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print(f"Usuario admin '{USERNAME}' creado correctamente.")
