"""Bootstrap helper: regenera hashes de los usuarios seed con los passwords reales.
Ejecutar UNA VEZ después de aplicar seed.sql:

    python -m app.bootstrap
"""
from app import create_app, db
from app.models import User

DEFAULTS = {
    "admin@tienda.com": "admin123",
    "trabajador@tienda.com": "trabajo123",
    "cliente@tienda.com": "cliente123",
}

def main():
    app = create_app()
    with app.app_context():
        for email, pwd in DEFAULTS.items():
            u = User.query.filter_by(email=email).first()
            if u:
                u.set_password(pwd)
                print(f"[OK] password reseteado: {email} -> {pwd}")
        db.session.commit()
        print("Listo. Ya puedes iniciar sesión con los usuarios de prueba.")

if __name__ == "__main__":
    main()
