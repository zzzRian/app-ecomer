from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Rol

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("client.home"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Credenciales inválidas.", "danger")
            return render_template("auth/login.html")
        if not user.activo:
            flash("Tu cuenta está desactivada. Contacta al administrador.", "danger")
            return render_template("auth/login.html")
        login_user(user, remember=request.form.get("remember") == "on")
        user.ultimo_login = datetime.utcnow()
        db.session.commit()
        flash(f"Bienvenido, {user.nombre}!", "success")

        # Redirección por rol
        if user.has_role("admin"):
            return redirect(url_for("admin.dashboard"))
        if user.has_role("trabajador"):
            return redirect(url_for("worker.panel"))
        return redirect(url_for("client.home"))
    return render_template("auth/login.html")

@auth_bp.route("/registro", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("client.home"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese email.", "warning")
            return render_template("auth/register.html")
        cliente_role = Rol.query.filter_by(nombre="cliente").first()
        u = User(
            nombre=request.form.get("nombre", "").strip(),
            apellido=request.form.get("apellido", "").strip(),
            email=email,
            telefono=request.form.get("telefono", "").strip(),
            rol_id=cliente_role.id if cliente_role else 3,
        )
        u.set_password(request.form.get("password", ""))
        db.session.add(u)
        db.session.commit()
        login_user(u)
        flash("Cuenta creada con éxito.", "success")
        return redirect(url_for("client.home"))
    return render_template("auth/register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("client.home"))
