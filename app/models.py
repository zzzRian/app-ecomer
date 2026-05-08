from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# ----------------------------- RBAC ---------------------------------
rol_permiso = db.Table(
    "rol_permiso",
    db.Column("rol_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permiso_id", db.Integer, db.ForeignKey("permisos.id"), primary_key=True),
)

class Rol(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    permisos = db.relationship("Permiso", secondary=rol_permiso, backref="roles")

class Permiso(db.Model):
    __tablename__ = "permisos"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(80), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))

# ----------------------------- USERS --------------------------------
class User(db.Model, UserMixin):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(30))
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    area = db.Column(db.String(80))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)

    rol = db.relationship("Rol", backref="usuarios")
    direcciones = db.relationship("Direccion", backref="usuario", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def has_role(self, *roles):
        return self.rol and self.rol.nombre in roles
    def has_permission(self, codigo):
        if not self.rol: return False
        return any(p.codigo == codigo for p in self.rol.permisos)

class Direccion(db.Model):
    __tablename__ = "direcciones"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    etiqueta = db.Column(db.String(50))
    destinatario = db.Column(db.String(120))
    calle = db.Column(db.String(200), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    pais = db.Column(db.String(80), default="Perú")
    predeterminada = db.Column(db.Boolean, default=False)

# ----------------------------- CATALOG ------------------------------
class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    productos = db.relationship("Producto", backref="categoria")

class Marca(db.Model):
    __tablename__ = "marcas"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    productos = db.relationship("Producto", backref="marca")

class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    especificaciones = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    precio_oferta = db.Column(db.Numeric(10, 2))
    stock = db.Column(db.Integer, default=0, nullable=False)
    stock_minimo = db.Column(db.Integer, default=5, nullable=False)
    imagen = db.Column(db.String(255))
    destacado = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"))
    marca_id = db.Column(db.Integer, db.ForeignKey("marcas.id"))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def precio_final(self):
        return float(self.precio_oferta) if self.precio_oferta else float(self.precio)

    @property
    def en_oferta(self):
        return self.precio_oferta is not None and self.precio_oferta < self.precio

    @property
    def stock_bajo(self):
        return self.stock <= self.stock_minimo

class Opinion(db.Model):
    __tablename__ = "opiniones"
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    puntuacion = db.Column(db.SmallInteger, nullable=False)
    comentario = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    producto = db.relationship("Producto", backref="opiniones")
    usuario = db.relationship("User")

# ----------------------------- ORDERS -------------------------------
class Pedido(db.Model):
    __tablename__ = "pedidos"
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    direccion_id = db.Column(db.Integer, db.ForeignKey("direcciones.id"))
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    envio = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), default=0)
    estado = db.Column(db.Enum("pendiente","pagado","en_preparacion","enviado","entregado","cancelado"),
                        default="pendiente", nullable=False)
    metodo_pago = db.Column(db.String(40))
    notas = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = db.relationship("User", foreign_keys=[usuario_id], backref="pedidos")
    trabajador = db.relationship("User", foreign_keys=[trabajador_id])
    direccion = db.relationship("Direccion")
    detalles = db.relationship("PedidoDetalle", backref="pedido", cascade="all, delete-orphan")
    pagos = db.relationship("Pago", backref="pedido", cascade="all, delete-orphan")
    envios = db.relationship("Envio", backref="pedido", cascade="all, delete-orphan")

class PedidoDetalle(db.Model):
    __tablename__ = "pedido_detalles"
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    producto = db.relationship("Producto")

class Pago(db.Model):
    __tablename__ = "pagos"
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    metodo = db.Column(db.String(40), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.Enum("aprobado","rechazado","pendiente"), default="pendiente")
    referencia = db.Column(db.String(80))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class Envio(db.Model):
    __tablename__ = "envios"
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    estado = db.Column(db.Enum("pendiente","en_preparacion","en_camino","entregado"), default="pendiente")
    tracking = db.Column(db.String(80))
    fecha_envio = db.Column(db.DateTime)
    fecha_entrega = db.Column(db.DateTime)
    notas = db.Column(db.Text)
    trabajador = db.relationship("User")

# --------------------------- INVENTORY ------------------------------
class InventarioMovimiento(db.Model):
    __tablename__ = "inventario_movimientos"
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    tipo = db.Column(db.Enum("entrada","salida","ajuste"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(200))
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    producto = db.relationship("Producto")

# --------------------------- NOTIFICATIONS --------------------------
class Notificacion(db.Model):
    __tablename__ = "notificaciones"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    mensaje = db.Column(db.Text)
    tipo = db.Column(db.String(40), default="info")
    leida = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class ActividadLog(db.Model):
    __tablename__ = "actividad_log"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    accion = db.Column(db.String(120), nullable=False)
    detalle = db.Column(db.Text)
    ip = db.Column(db.String(45))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.relationship("User")
