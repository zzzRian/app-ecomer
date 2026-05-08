import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # MYSQL RAILWAY
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # Seguridad para caracteres especiales en password
    DB_PASSWORD_SAFE = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_SAFE}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ----------------------------
    # ARCHIVOS
    # ----------------------------
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__), "app", "static", "uploads"
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

    # ----------------------------
    # IA (OPCIONAL)
    # ----------------------------
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
