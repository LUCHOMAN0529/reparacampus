"""Entrada HTTP de las incidencias. Sin reglas de negocio ni SQL."""
from flask import Blueprint, current_app, g, redirect, render_template, request, url_for

from . import consultas, dominio, servicios
from .auth import requiere_rol, requiere_sesion
from .db import get_db

bp = Blueprint("incidencias", __name__, url_prefix="/incidencias")

# Únicos campos que el registro acepta del cliente (AC-S01-08).
CAMPOS_REGISTRO = ("ubicacion", "categoria", "descripcion", "impacto", "riesgo_personas")


def _ahora():
    return current_app.config["RELOJ"]()


def _pagina_detalle(codigo, error=None):
    db = get_db()
    incidencia = consultas.obtener(db, g.usuario, codigo)
    pagina = render_template(
        "incidencia_detalle.html",
        incidencia=incidencia,
        historial=consultas.historial(db, incidencia["id"]),
        tecnicos=consultas.tecnicos_activos(db),
        dominio=dominio,
        error=error,
    )
    return pagina, (error.codigo_http if error else 200)


def _operar(codigo, operacion, *argumentos):
    """Ejecuta una transición y vuelve al detalle.

    Un error de estado o de datos se muestra en el mismo detalle: en ese punto
    ya se comprobó que el usuario puede ver la incidencia. Los errores de
    permiso y de visibilidad los responde el manejador general (403 y 404).
    """
    try:
        operacion(get_db(), g.usuario, codigo, *argumentos, _ahora())
    except (dominio.ErrorValidacion, dominio.ErrorEstado) as error:
        return _pagina_detalle(codigo, error=error)
    return redirect(url_for(".detalle", codigo=codigo))


@bp.route("/nueva", methods=("GET", "POST"))
@requiere_rol(dominio.SOLICITANTE)
def nueva():
    valores, errores, estado_http = {}, {}, 200
    if request.method == "POST":
        valores = {campo: request.form.get(campo) for campo in CAMPOS_REGISTRO}
        try:
            codigo = servicios.registrar_incidencia(get_db(), g.usuario, valores, _ahora())
        except dominio.ErrorValidacion as error:
            errores, estado_http = error.errores, error.codigo_http
        else:
            return redirect(url_for(".detalle", codigo=codigo))
    return render_template("incidencia_nueva.html", valores=valores, errores=errores, dominio=dominio), estado_http


@bp.route("/<codigo>")
@requiere_sesion
def detalle(codigo):
    return _pagina_detalle(codigo)


@bp.route("/<codigo>/asignar", methods=("POST",))
@requiere_sesion
def asignar(codigo):
    return _operar(codigo, servicios.asignar, request.form.get("tecnico_id"))


@bp.route("/<codigo>/iniciar", methods=("POST",))
@requiere_sesion
def iniciar(codigo):
    return _operar(codigo, servicios.iniciar_atencion)


@bp.route("/<codigo>/solucion", methods=("POST",))
@requiere_sesion
def solucion(codigo):
    return _operar(codigo, servicios.registrar_solucion, request.form.get("solucion"))
