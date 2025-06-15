from app import db
from models import User
from werkzeug.security import generate_password_hash

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
