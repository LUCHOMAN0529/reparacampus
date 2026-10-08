"""Inicio y cierre de sesión. La identidad y el rol salen siempre de la sesión."""
from functools import wraps

from flask import Blueprint, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db
from .dominio import ErrorPermiso

bp = Blueprint("auth", __name__)


@bp.before_app_request
def cargar_usuario():
    """La sesión guarda solo el identificador; el rol se lee de la base en cada petición."""
    g.usuario = None
    usuario_id = session.get("usuario_id")
    if usuario_id is not None:
        g.usuario = get_db().execute(
            "SELECT id, usuario, nombre, rol FROM usuarios WHERE id = ? AND activo = 1",
            (usuario_id,),
        ).fetchone()


def requiere_sesion(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if g.usuario is None:
            return redirect(url_for("auth.login"))
        return vista(*args, **kwargs)

    return envoltura


def requiere_rol(*roles):
    def decorador(vista):
        @wraps(vista)
        @requiere_sesion
        def envoltura(*args, **kwargs):
            if g.usuario["rol"] not in roles:
                raise ErrorPermiso("Su rol no puede abrir esta página.")
            return vista(*args, **kwargs)

        return envoltura

    return decorador


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        fila = get_db().execute(
            "SELECT id, password_hash FROM usuarios WHERE usuario = ? AND activo = 1",
            (request.form.get("usuario", ""),),
        ).fetchone()
        if fila is None or not check_password_hash(
            fila["password_hash"], request.form.get("clave", "")
        ):
            return render_template("login.html", error="Usuario o contraseña incorrectos."), 401
        session.clear()
        session["usuario_id"] = fila["id"]
        return redirect(url_for("inicio"))
    return render_template("login.html", error=None)


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
