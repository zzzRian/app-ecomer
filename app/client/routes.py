import uuid
from datetime import datetime
from decimal import Decimal
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, session, abort)
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models import (Producto, Categoria, Marca, Pedido, PedidoDetalle,
                         Direccion, Pago, Envio, Notificacion, Opinion)

client_bp = Blueprint("client", __name__, template_folder="../templates/client")

# --------------------------- HOME / CATALOG -------------------------
@client_bp.route("/")
def home():
    destacados = Producto.query.filter_by(destacado=True, activo=True).limit(8).all()
    ofertas = Producto.query.filter(Producto.precio_oferta.isnot(None),
                                    Producto.activo.is_(True)).limit(4).all()
    categorias = Categoria.query.all()
    return render_template("client/home.html",
                           destacados=destacados, ofertas=ofertas, categorias=categorias)

@client_bp.route("/productos")
def catalog():
    q = request.args.get("q", "").strip()
    cat = request.args.get("categoria", type=int)
    marca = request.args.get("marca", type=int)
    pmin = request.args.get("pmin", type=float)
    pmax = request.args.get("pmax", type=float)
    orden = request.args.get("orden", "nuevos")
    page = request.args.get("page", 1, type=int)

    query = Producto.query.filter_by(activo=True)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Producto.nombre.ilike(like),
                                  Producto.descripcion.ilike(like)))
    if cat:   query = query.filter_by(categoria_id=cat)
    if marca: query = query.filter_by(marca_id=marca)
    if pmin is not None: query = query.filter(Producto.precio >= pmin)
    if pmax is not None: query = query.filter(Producto.precio <= pmax)

    if orden == "precio_asc":   query = query.order_by(Producto.precio.asc())
    elif orden == "precio_desc": query = query.order_by(Producto.precio.desc())
    elif orden == "nombre":     query = query.order_by(Producto.nombre.asc())
    else:                       query = query.order_by(Producto.creado_en.desc())

    productos = query.paginate(page=page, per_page=12, error_out=False)
    categorias = Categoria.query.all()
    marcas = Marca.query.all()
    return render_template("client/catalog.html", productos=productos,
                           categorias=categorias, marcas=marcas, q=q,
                           sel_cat=cat, sel_marca=marca, orden=orden)

@client_bp.route("/producto/<int:pid>")
def product_detail(pid):
    producto = Producto.query.get_or_404(pid)
    relacionados = Producto.query.filter(
        Producto.categoria_id == producto.categoria_id,
        Producto.id != pid, Producto.activo.is_(True)
    ).limit(4).all()
    return render_template("client/product.html", producto=producto, relacionados=relacionados)

# --------------------------- CART -----------------------------------
def _get_cart():
    return session.setdefault("cart", {})

@client_bp.route("/carrito")
def cart():
    cart = _get_cart()
    items, total = [], Decimal("0")
    for pid, qty in cart.items():
        p = Producto.query.get(int(pid))
        if not p: continue
        sub = Decimal(str(p.precio_final)) * qty
        total += sub
        items.append({"producto": p, "cantidad": qty, "subtotal": sub})
    return render_template("client/cart.html", items=items, total=total)

@client_bp.route("/carrito/agregar/<int:pid>", methods=["POST"])
def cart_add(pid):
    p = Producto.query.get_or_404(pid)
    qty = int(request.form.get("cantidad", 1))
    cart = _get_cart()
    cart[str(pid)] = cart.get(str(pid), 0) + qty
    if cart[str(pid)] > p.stock:
        cart[str(pid)] = p.stock
        flash(f"Stock máximo: {p.stock}", "warning")
    session.modified = True
    flash(f"{p.nombre} agregado al carrito.", "success")
    return redirect(request.referrer or url_for("client.catalog"))

@client_bp.route("/carrito/actualizar/<int:pid>", methods=["POST"])
def cart_update(pid):
    qty = int(request.form.get("cantidad", 1))
    cart = _get_cart()
    if qty <= 0: cart.pop(str(pid), None)
    else: cart[str(pid)] = qty
    session.modified = True
    return redirect(url_for("client.cart"))

@client_bp.route("/carrito/eliminar/<int:pid>", methods=["POST"])
def cart_remove(pid):
    cart = _get_cart()
    cart.pop(str(pid), None)
    session.modified = True
    return redirect(url_for("client.cart"))

# --------------------------- CHECKOUT -------------------------------
@client_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = _get_cart()
    if not cart:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("client.catalog"))

    items, total = [], Decimal("0")
    for pid, qty in cart.items():
        p = Producto.query.get(int(pid))
        if not p: continue
        sub = Decimal(str(p.precio_final)) * qty
        total += sub
        items.append((p, qty, sub))

    if request.method == "POST":
        # Crear o usar dirección
        direccion_id = request.form.get("direccion_id", type=int)
        if not direccion_id:
            d = Direccion(
                usuario_id=current_user.id,
                etiqueta="Envío",
                destinatario=request.form.get("destinatario") or current_user.nombre,
                calle=request.form.get("calle"),
                ciudad=request.form.get("ciudad"),
                region=request.form.get("region"),
                codigo_postal=request.form.get("codigo_postal"),
            )
            db.session.add(d); db.session.flush()
            direccion_id = d.id

        metodo = request.form.get("metodo_pago", "tarjeta")
        envio = Decimal("15.00") if total < 200 else Decimal("0.00")
        ped = Pedido(
            numero="P-" + uuid.uuid4().hex[:8].upper(),
            usuario_id=current_user.id,
            direccion_id=direccion_id,
            subtotal=total,
            envio=envio,
            total=total + envio,
            estado="pagado",
            metodo_pago=metodo,
        )
        db.session.add(ped); db.session.flush()
        for p, qty, sub in items:
            db.session.add(PedidoDetalle(
                pedido_id=ped.id, producto_id=p.id,
                cantidad=qty, precio_unitario=p.precio_final, subtotal=sub
            ))
            # Descontar stock (también el trigger lo hace; dejamos por idempotencia)
            p.stock = max(0, p.stock - qty)

        db.session.add(Pago(pedido_id=ped.id, metodo=metodo, monto=ped.total,
                            estado="aprobado", referencia=uuid.uuid4().hex[:12]))
        db.session.add(Envio(pedido_id=ped.id, estado="pendiente"))
        db.session.add(Notificacion(
            usuario_id=current_user.id,
            titulo="Compra confirmada",
            mensaje=f"Tu pedido {ped.numero} fue registrado.",
            tipo="success",
        ))
        db.session.commit()
        session["cart"] = {}
        flash(f"¡Compra realizada! Pedido {ped.numero}", "success")
        return redirect(url_for("client.order_detail", pid=ped.id))

    direcciones = Direccion.query.filter_by(usuario_id=current_user.id).all()
    return render_template("client/checkout.html", items=items, total=total,
                            direcciones=direcciones)

# --------------------------- USER AREA ------------------------------
@client_bp.route("/cuenta")
@login_required
def account():
    pedidos = Pedido.query.filter_by(usuario_id=current_user.id)\
                          .order_by(Pedido.creado_en.desc()).all()
    return render_template("client/account.html", pedidos=pedidos)

@client_bp.route("/cuenta/perfil", methods=["GET","POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.nombre = request.form.get("nombre", current_user.nombre)
        current_user.apellido = request.form.get("apellido", current_user.apellido)
        current_user.telefono = request.form.get("telefono", current_user.telefono)
        new_pwd = request.form.get("password")
        if new_pwd:
            current_user.set_password(new_pwd)
        db.session.commit()
        flash("Perfil actualizado.", "success")
        return redirect(url_for("client.profile"))
    return render_template("client/profile.html")

@client_bp.route("/pedido/<int:pid>")
@login_required
def order_detail(pid):
    ped = Pedido.query.get_or_404(pid)
    if ped.usuario_id != current_user.id and not current_user.has_role("admin","trabajador"):
        abort(403)
    return render_template("client/order_detail.html", pedido=ped)

@client_bp.route("/conocenos")
def about():
    return render_template("client/about.html")

@client_bp.route("/contacto", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        flash("Gracias por escribirnos. Te responderemos pronto.", "success")
        return redirect(url_for("client.contact"))
    return render_template("client/contact.html")
