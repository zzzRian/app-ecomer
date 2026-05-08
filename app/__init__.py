import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para continuar."
    login_manager.login_message_category = "warning"

    from app.models import User
    @login_manager.user_loader
    def load_user(uid):
        return db.session.get(User, int(uid))

    # Blueprints
    from app.auth.routes import auth_bp
    from app.client.routes import client_bp
    from app.admin.routes import admin_bp
    from app.worker.routes import worker_bp
    from app.api.routes import api_bp
    from app.errors import errors_bp

    app.register_blueprint(auth_bp,   url_prefix="/auth")
    app.register_blueprint(client_bp)                       # raíz: /
    app.register_blueprint(admin_bp,  url_prefix="/admin")
    app.register_blueprint(worker_bp, url_prefix="/trabajador")
    app.register_blueprint(api_bp,    url_prefix="/api")
    app.register_blueprint(errors_bp)

    # Crear carpeta uploads si no existe
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Context processor: cantidad en carrito y notificaciones
    from flask_login import current_user
    from app.models import Notificacion
    @app.context_processor
    def inject_globals():
        from flask import session
        cart = session.get("cart", {})
        cart_count = sum(cart.values()) if cart else 0
        notif_count = 0
        if current_user.is_authenticated:
            notif_count = Notificacion.query.filter_by(
                usuario_id=current_user.id, leida=False
            ).count()
        return dict(cart_count=cart_count, notif_count=notif_count)

    return app
