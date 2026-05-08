from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Pedido, Envio, Notificacion
from app.decorators import role_required

worker_bp = Blueprint("worker", __name__, template_folder="../templates/worker")

@worker_bp.route("/")
@login_required
@role_required("trabajador","admin")
def panel():
    pendientes = Pedido.query.filter(Pedido.estado.in_(["pagado","en_preparacion"])).all()
    en_camino = Pedido.query.filter_by(estado="enviado").all()
    return render_template("worker/panel.html", pendientes=pendientes, en_camino=en_camino)

@worker_bp.route("/envio/<int:pid>", methods=["POST"])
@login_required
@role_required("trabajador","admin")
def update_shipment(pid):
    ped = Pedido.query.get_or_404(pid)
    nuevo = request.form.get("estado")
    if nuevo not in ("en_preparacion","enviado","entregado","cancelado"):
        flash("Estado inválido.", "danger"); return redirect(url_for("worker.panel"))
    ped.estado = nuevo
    env = ped.envios[0] if ped.envios else Envio(pedido_id=ped.id)
    env.trabajador_id = current_user.id
    if nuevo == "en_preparacion":  env.estado = "en_preparacion"
    elif nuevo == "enviado":       env.estado = "en_camino";  env.fecha_envio = datetime.utcnow()
    elif nuevo == "entregado":     env.estado = "entregado";  env.fecha_entrega = datetime.utcnow()
    if env.id is None: db.session.add(env)
    db.session.add(Notificacion(
        usuario_id=ped.usuario_id,
        titulo="Actualización de pedido",
        mensaje=f"Tu pedido {ped.numero} ahora está: {nuevo}",
    ))
    db.session.commit()
    flash("Estado actualizado.", "success")
    return redirect(url_for("worker.panel"))
