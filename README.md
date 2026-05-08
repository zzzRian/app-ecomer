# Sistema Web de Ventas de Productos Electrónicos

Sistema e-commerce completo con **Flask + MySQL + HTML/CSS/JS** y control de acceso por roles (RBAC).

## 🧰 Tecnologías

- **Backend:** Python 3.10+ / Flask
- **Base de datos:** MySQL 8.x
- **ORM:** SQLAlchemy
- **Frontend:** HTML5, CSS3, JavaScript (vanilla) + Bootstrap 5
- **Auth:** Flask-Login + Werkzeug (hashing bcrypt-style)
- **Plantillas:** Jinja2

## 👥 Roles (RBAC)

| Rol         | Acceso |
|-------------|--------|
| `admin`     | Total: usuarios, personal, productos, pedidos, reportes |
| `trabajador`| Pedidos, logística, estados de envío |
| `cliente`   | Catálogo, carrito, checkout, historial |

Tablas: `roles`, `permisos`, `rol_permiso`, `usuarios` con FK a `roles`.

## 🚀 Instalación rápida

### 1. Requisitos
- Python 3.10+
- MySQL 8.x (XAMPP, WAMP, MySQL Server, etc.)
- pip

### 2. Crear la base de datos
Abre MySQL Workbench (o phpMyAdmin) y ejecuta:

```sql
SOURCE database/schema.sql;
SOURCE database/seed.sql;
```

O desde terminal:
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

### 3. Configurar conexión
Edita `.env` (o `config.py`):

```
SECRET_KEY=cambia-esto
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ecommerce_electronicos
```

### 4. Instalar dependencias
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 5. Ejecutar
```bash
python run.py
```

Abre http://localhost:5000

## 🔑 Usuarios de prueba (seed)

| Email                  | Password    | Rol         |
|------------------------|-------------|-------------|
| admin@tienda.com       | admin123    | admin       |
| trabajador@tienda.com  | trabajo123  | trabajador  |
| cliente@tienda.com     | cliente123  | cliente     |

## 📁 Estructura

```
ecommerce/
├── run.py                  # Punto de entrada
├── config.py               # Configuración Flask + DB
├── requirements.txt
├── .env.example
├── database/
│   ├── schema.sql          # DDL: tablas, FKs, índices
│   ├── seed.sql            # Datos iniciales (roles, admin, productos)
│   └── ER_diagram.md       # Diagrama ER (Mermaid)
└── app/
    ├── __init__.py         # Factory de la app + registro de blueprints
    ├── models.py           # SQLAlchemy: User, Role, Product, Order...
    ├── auth/               # Login, logout, registro
    ├── client/             # Catálogo, carrito, checkout, perfil
    ├── admin/              # Dashboard, CRUD productos, usuarios, reportes
    ├── worker/             # Logística, estados de pedido
    ├── api/                # Endpoints JSON (carrito, chatbot)
    ├── decorators.py       # @role_required('admin')
    ├── templates/          # Jinja2
    └── static/
        ├── css/style.css
        ├── js/app.js
        └── img/
```

## 🤖 Chatbot IA

Implementado como widget flotante. Por defecto usa respuestas locales por reglas
(no requiere API key). Para conectar con OpenAI/Gemini, define `OPENAI_API_KEY`
en `.env` y descomenta la sección en `app/api/routes.py`.

## 📊 Reportes

- Ventas por fecha (filtros)
- Ventas por producto / empleado
- Stock bajo
- Exportación CSV

## 🔒 Seguridad

- Hashing de contraseñas con `werkzeug.security`
- CSRF protection vía Flask-WTF
- Decoradores `@login_required` y `@role_required`
- Validación server-side y client-side
- Sesiones firmadas

## 📝 Licencia
MIT — usa, modifica y aprende.


## Pasos de uso
1.Conectarse a la bd, ejecutando los codigos de la carpeta database en MYSQL
2. Configurar config.py y .env
3. cp .env.example .env
# 3. Instalar y correr
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m app.bootstrap   # genera hashes correctos para los usuarios seed
python run.py