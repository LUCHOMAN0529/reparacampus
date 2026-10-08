"""Fábrica de la aplicación ReparaCampus."""
import os
import secrets

from flask import Flask, render_template

from . import auth, db, dominio, reloj, rutas


def _clave_secreta(app):
    """La clave de sesión no se versiona: sale del entorno o de un archivo local."""
    clave = os.environ.get("REPARACAMPUS_SECRET_KEY")
    if clave:
        return clave
    ruta = os.path.join(app.instance_path, "secret_key")
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(secrets.token_hex(32))
    with open(ruta, encoding="utf-8") as archivo:
        return archivo.read().strip()


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "reparacampus.sqlite"),
        RELOJ=reloj.ahora_utc,
        PASSWORD_HASH_METHOD="scrypt",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if config:
        app.config.update(config)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = _clave_secreta(app)

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(rutas.bp)

    @app.template_filter("fecha")
    def fecha(texto):
        return reloj.de_texto(texto).strftime("%Y-%m-%d %H:%M:%S UTC")

    @app.errorhandler(dominio.ErrorDominio)
    def error_de_dominio(error):
        return render_template("error.html", error=error), error.codigo_http

    @app.route("/")
    @auth.requiere_sesion
    def inicio():
        return render_template("inicio.html")

    return app
