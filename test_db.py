from config import Config
from sqlalchemy import create_engine, text

def test_connection():
    try:
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE();"))
            db_name = result.fetchone()[0]

        print("✅ CONEXIÓN EXITOSA")
        print(f"📦 Base de datos activa: {db_name}")

    except Exception as e:
        print("❌ ERROR DE CONEXIÓN")
        print(str(e))

if __name__ == "__main__":
    test_connection()