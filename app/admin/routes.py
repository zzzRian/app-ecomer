import os
from datetime import datetime, timedelta
from decimal import Decimal
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, current_app, abort, send_file)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc
from app import db
from app.models import (Producto, Categoria, Marca, Pedido, PedidoDetalle,
                         User, Rol, Notificacion, ActividadLog,
                         InventarioMovimiento)
from app.decorators import role_required

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")

def allowed_file(filename):
    return ("." in filename and
            filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"])

# ------------------------- DASHBOARD --------------------------------
@admin_bp.route("/")
@login_required
@role_required("admin")
def dashboard():
    hoy = datetime.utcnow().date()
    inicio_mes = hoy.replace(day=1)

    ventas_total = db.session.query(func.coalesce(func.sum(Pedido.total), 0))\
                              .filter(Pedido.estado != "cancelado").scalar()
    ventas_mes = db.session.query(func.coalesce(func.sum(Pedido.total), 0))\
                            .filter(Pedido.creado_en >= inicio_mes,
                                    Pedido.estado != "cancelado").scalar()
    pedidos_total = Pedido.query.count()
    clientes_total = User.query.filter(User.rol.has(nombre="cliente")).count()

    pedidos_recientes = Pedido.query.order_by(Pedido.creado_en.desc()).limit(8).all()
    top_productos = db.session.query(
        Producto, func.sum(PedidoDetalle.cantidad).label("vendidos")
    ).join(PedidoDetalle).group_by(Producto.id)\
     .order_by(desc("vendidos")).limit(5).all()
    stock_bajo = Producto.query.filter(Producto.stock <= Producto.stock_minimo,
                                        Producto.activo.is_(True)).all()

    # Serie de ventas últimos 7 días para gráfico
    serie = []
    for i in range(6, -1, -1):
        d = hoy - timedelta(days=i)
        next_d = d + timedelta(days=1)
        v = db.session.query(func.coalesce(func.sum(Pedido.total), 0))\
                       .filter(Pedido.creado_en >= d, Pedido.creado_en < next_d,
                               Pedido.estado != "cancelado").scalar()
        serie.append({"fecha": d.strftime("%d/%m"), "total": float(v)})

    return render_template("admin/dashboard.html",
        ventas_total=ventas_total, ventas_mes=ventas_mes,
        pedidos_total=pedidos_total, clientes_total=clientes_total,
        pedidos_recientes=pedidos_recientes, top_productos=top_productos,
        stock_bajo=stock_bajo, serie=serie)

# ------------------------- PRODUCTOS --------------------------------
@admin_bp.route("/productos")
@login_required
@role_required("admin")
def products_list():
    productos = Producto.query.order_by(Producto.creado_en.desc()).all()
    return render_template("admin/products.html", productos=productos)

@admin_bp.route("/productos/nuevo", methods=["GET","POST"])
@login_required
@role_required("admin")
def product_new():
    if request.method == "POST":
        return _save_product(None)
    return render_template("admin/product_form.html",
        producto=None, categorias=Categoria.query.all(), marcas=Marca.query.all())

@admin_bp.route("/productos/<int:pid>/editar", methods=["GET","POST"])
@login_required
@role_required("admin")
def product_edit(pid):
    p = Producto.query.get_or_404(pid)
    if request.method == "POST":
        return _save_product(p)
    return render_template("admin/product_form.html",
        producto=p, categorias=Categoria.query.all(), marcas=Marca.query.all())

def _save_product(p):
    es_nuevo = p is None
    if es_nuevo:
        p = Producto()
    p.nombre = request.form.get("nombre", "").strip()
    p.sku = request.form.get("sku", "").strip()
    p.descripcion = request.form.get("descripcion", "")
    p.especificaciones = request.form.get("especificaciones", "")
    p.precio = Decimal(request.form.get("precio") or "0")
    oferta = request.form.get("precio_oferta", "").strip()
    p.precio_oferta = Decimal(oferta) if oferta else None
    p.stock = int(request.form.get("stock") or 0)
    p.stock_minimo = int(request.form.get("stock_minimo") or 5)
    p.categoria_id = request.form.get("categoria_id", type=int)
    p.marca_id = request.form.get("marca_id", type=int)
    p.destacado = request.form.get("destacado") == "on"
    p.activo = request.form.get("activo", "on") == "on"

    file = request.files.get("imagen")
    if file and file.filename and allowed_file(file.filename):
        fn = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fn))
        p.imagen = fn

    if es_nuevo: db.session.add(p)
    db.session.commit()
    db.session.add(ActividadLog(usuario_id=current_user.id,
        accion="producto.guardar", detalle=f"id={p.id} nombre={p.nombre}"))
    db.session.commit()
    flash("Producto guardado.", "success")
    return redirect(url_for("admin.products_list"))

@admin_bp.route("/productos/<int:pid>/eliminar", methods=["POST"])
@login_required
@role_required("admin")
def product_delete(pid):
    p = Producto.query.get_or_404(pid)
    p.activo = False
    db.session.commit()
    flash("Producto desactivado.", "info")
    return redirect(url_for("admin.products_list"))

# ------------------------- PEDIDOS ----------------------------------
@admin_bp.route("/pedidos")
@login_required
@role_required("admin","trabajador")
def orders_list():
    estado = request.args.get("estado")
    q = Pedido.query
    if estado: q = q.filter_by(estado=estado)
    pedidos = q.order_by(Pedido.creado_en.desc()).all()
    return render_template("admin/orders.html", pedidos=pedidos, estado=estado)

@admin_bp.route("/pedidos/<int:pid>", methods=["GET","POST"])
@login_required
@role_required("admin","trabajador")
def order_detail(pid):
    ped = Pedido.query.get_or_404(pid)
    if request.method == "POST":
        nuevo = request.form.get("estado")
        if nuevo:
            ped.estado = nuevo
            db.session.add(Notificacion(
                usuario_id=ped.usuario_id,
                titulo="Estado de pedido actualizado",
                mensaje=f"Tu pedido {ped.numero} ahora está {nuevo}.",
                tipo="info",
            ))
            db.session.commit()
            flash("Estado actualizado.", "success")
        return redirect(url_for("admin.order_detail", pid=pid))
    return render_template("admin/order_detail.html", pedido=ped)

# ------------------------- USUARIOS ---------------------------------
@admin_bp.route("/usuarios")
@login_required
@role_required("admin")
def users_list():
    usuarios = User.query.order_by(User.creado_en.desc()).all()
    return render_template("admin/users.html", usuarios=usuarios, roles=Rol.query.all())

@admin_bp.route("/usuarios/<int:uid>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def user_toggle(uid):
    u = User.query.get_or_404(uid)
    u.activo = not u.activo
    db.session.commit()
    flash(f"Usuario {'activado' if u.activo else 'desactivado'}.", "info")
    return redirect(url_for("admin.users_list"))

@admin_bp.route("/usuarios/<int:uid>/rol", methods=["POST"])
@login_required
@role_required("admin")
def user_role(uid):
    u = User.query.get_or_404(uid)
    rol_id = request.form.get("rol_id", type=int)
    if rol_id:
        u.rol_id = rol_id
        db.session.commit()
        flash("Rol actualizado.", "success")
    return redirect(url_for("admin.users_list"))

# ------------------------- PERSONAL ---------------------------------
@admin_bp.route("/personal", methods=["GET","POST"])
@login_required
@role_required("admin")
def staff():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Email ya registrado.", "warning")
        else:
            u = User(
                nombre=request.form.get("nombre"),
                apellido=request.form.get("apellido"),
                email=email,
                rol_id=request.form.get("rol_id", type=int),
                area=request.form.get("area"),
            )
            u.set_password(request.form.get("password", "12345678"))
            db.session.add(u); db.session.commit()
            flash("Personal creado.", "success")
        return redirect(url_for("admin.staff"))
    personal = User.query.filter(User.rol.has(Rol.nombre.in_(["admin","trabajador"])))\
                          .order_by(User.creado_en.desc()).all()
    roles = Rol.query.filter(Rol.nombre.in_(["admin","trabajador"])).all()
    return render_template("admin/staff.html", personal=personal, roles=roles)

# ------------------------- REPORTES ---------------------------------
@admin_bp.route("/reportes")
@login_required
@role_required("admin")
def reports():
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    q = Pedido.query.filter(Pedido.estado != "cancelado")
    if desde:
        q = q.filter(Pedido.creado_en >= datetime.strptime(desde, "%Y-%m-%d"))
    if hasta:
        q = q.filter(Pedido.creado_en <= datetime.strptime(hasta, "%Y-%m-%d") + timedelta(days=1))
    pedidos = q.order_by(Pedido.creado_en.desc()).all()
    total = sum(float(p.total) for p in pedidos)

    por_producto = db.session.query(
        Producto.nombre, func.sum(PedidoDetalle.cantidad).label("uds"),
        func.sum(PedidoDetalle.subtotal).label("ingreso")
    ).join(PedidoDetalle).group_by(Producto.id)\
     .order_by(desc("ingreso")).limit(20).all()

    por_empleado = db.session.query(
        User.nombre, func.count(Pedido.id).label("ventas"),
        func.coalesce(func.sum(Pedido.total), 0).label("monto")
    ).join(Pedido, Pedido.trabajador_id == User.id)\
     .group_by(User.id).all()

    return render_template("admin/reports.html",
        pedidos=pedidos, total=total, desde=desde, hasta=hasta,
        por_producto=por_producto, por_empleado=por_empleado)
