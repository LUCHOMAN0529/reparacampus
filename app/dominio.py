"""Reglas de negocio de ReparaCampus como funciones puras.

Este módulo no conoce Flask ni la base de datos. Cada regla remite a su SPEC.
"""
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

UBICACIONES = ("LAB-01", "AULA-201", "BIB-01")
CATEGORIAS = ("ELECTRICIDAD", "HIDRAULICA", "MOBILIARIO", "TIC")
IMPACTOS = ("BAJO", "ALTO")
PRIORIDADES = ("CRITICA", "ALTA", "NORMAL")
ESTADOS = ("REGISTRADA", "ASIGNADA", "EN_ATENCION", "PENDIENTE_VALIDACION", "CERRADA")

SOLICITANTE = "SOLICITANTE"
COORDINADOR = "COORDINADOR"
TECNICO = "TECNICO"

# Única definición de las transiciones permitidas (arquitectura.md, sección 3).
# accion -> (estado de origen, estado de destino, rol que la ejecuta)
TRANSICIONES = {
    "CREAR": (None, "REGISTRADA", SOLICITANTE),
    "ASIGNAR": ("REGISTRADA", "ASIGNADA", COORDINADOR),
    "INICIAR_ATENCION": ("ASIGNADA", "EN_ATENCION", TECNICO),
    "REGISTRAR_SOLUCION": ("EN_ATENCION", "PENDIENTE_VALIDACION", TECNICO),
    "CONFIRMAR_SOLUCION": ("PENDIENTE_VALIDACION", "CERRADA", SOLICITANTE),
    "RECHAZAR_SOLUCION": ("PENDIENTE_VALIDACION", "EN_ATENCION", SOLICITANTE),
    "REABRIR": ("CERRADA", "EN_ATENCION", SOLICITANTE),
}

DESCRIPCION_MIN, DESCRIPCION_MAX = 20, 500
SOLUCION_MIN, SOLUCION_MAX = 20, 800
MOTIVO_MIN, MOTIVO_MAX = 10, 300
PLAZO_REAPERTURA = timedelta(hours=48)


class ErrorDominio(Exception):
    codigo_http = 400

    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.mensaje = mensaje


class ErrorValidacion(ErrorDominio):
    """Dato ausente, fuera de catálogo o fuera de límites."""

    codigo_http = 400

    def __init__(self, errores):
        super().__init__("; ".join(errores.values()))
        self.errores = errores


class ErrorPermiso(ErrorDominio):
    """El rol de la sesión no puede ejecutar la operación."""

    codigo_http = 403


class NoEncontrada(ErrorDominio):
    """La incidencia no existe o el usuario no puede verla."""

    codigo_http = 404


class ErrorEstado(ErrorDominio):
    """El estado actual o el plazo no permiten la operación."""

    codigo_http = 409


def exigir_rol(rol, accion):
    """Paso 2 del orden de comprobación: ¿el rol puede ejecutar la acción?"""
    if rol != TRANSICIONES[accion][2]:
        raise ErrorPermiso("Su rol no puede ejecutar esta operación.")


def exigir_estado(estado_actual, accion):
    """Paso 4: ¿el estado actual es el origen de la transición?"""
    origen = TRANSICIONES[accion][0]
    if estado_actual != origen:
        raise ErrorEstado(
            f"La operación requiere el estado {origen} y la incidencia está en {estado_actual}."
        )


def validar_texto(valor, minimo, maximo, campo):
    """Retira espacios externos y aplica los límites (SUP-04)."""
    texto = (valor or "").strip()
    if not minimo <= len(texto) <= maximo:
        raise ErrorValidacion(
            {campo: f"Debe tener entre {minimo} y {maximo} caracteres; tiene {len(texto)}."}
        )
    return texto


def validar_registro(datos):
    """S01: valida los cinco campos del registro y devuelve los datos limpios."""
    errores = {}

    ubicacion = datos.get("ubicacion")
    if ubicacion not in UBICACIONES:
        errores["ubicacion"] = "Seleccione una ubicación del catálogo."

    categoria = datos.get("categoria")
    if categoria not in CATEGORIAS:
        errores["categoria"] = "Seleccione una categoría del catálogo."

    try:
        descripcion = validar_texto(
            datos.get("descripcion"), DESCRIPCION_MIN, DESCRIPCION_MAX, "descripcion"
        )
    except ErrorValidacion as error:
        errores.update(error.errores)

    impacto = datos.get("impacto")
    if impacto not in IMPACTOS:
        errores["impacto"] = "El impacto debe ser BAJO o ALTO."

    # SUP-02: el riesgo es explícito; ausente o distinto de true/false se rechaza.
    riesgo = {"true": True, "false": False}.get(datos.get("riesgo_personas"))
    if riesgo is None:
        errores["riesgo_personas"] = "Indique si hay riesgo para personas."

    if errores:
        raise ErrorValidacion(errores)
    return {
        "ubicacion": ubicacion,
        "categoria": categoria,
        "descripcion": descripcion,
        "impacto": impacto,
        "riesgo_personas": riesgo,
    }


def calcular_prioridad(impacto, riesgo_personas):
    """S02: con riesgo, CRITICA; sin riesgo, ALTA si el impacto es ALTO y NORMAL si es BAJO."""
    if riesgo_personas:
        return "CRITICA"
    return "ALTA" if impacto == "ALTO" else "NORMAL"


def dentro_de_plazo_reapertura(cerrada_en, ahora):
    """S04: el límite de 48 horas es inclusivo (Q3)."""
    return ahora - cerrada_en <= PLAZO_REAPERTURA


def validar_filtros(estado, prioridad):
    """S05: un filtro vacío no restringe; un valor fuera del catálogo se rechaza (SUP-09)."""
    estado = estado or None
    prioridad = prioridad or None
    errores = {}
    if estado is not None and estado not in ESTADOS:
        errores["estado"] = "El estado del filtro no existe."
    if prioridad is not None and prioridad not in PRIORIDADES:
        errores["prioridad"] = "La prioridad del filtro no existe."
    if errores:
        raise ErrorValidacion(errores)
    return estado, prioridad


def porcentaje_cierre(cerradas, total):
    """S05: CERRADAS / total x 100 con un decimal y coma; sin registros, 0,0 %."""
    if total == 0:
        valor = Decimal("0.0")
    else:
        valor = (Decimal(cerradas) * 100 / Decimal(total)).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )
    return f"{valor}".replace(".", ",") + " %"
