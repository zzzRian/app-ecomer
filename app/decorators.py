from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user

def role_required(*roles):
    """Restringe acceso por rol. Usage: @role_required('admin', 'trabajador')"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesión.", "warning")
                return redirect(url_for("auth.login"))
            if not current_user.has_role(*roles):
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def permission_required(codigo):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if not current_user.has_permission(codigo):
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
