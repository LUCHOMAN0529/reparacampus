"""Infraestructura de pruebas.

Cada prueba usa un archivo SQLite propio y temporal, independiente de la base
de desarrollo, y un reloj controlado en lugar del reloj del sistema.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app import create_app
from app.db import conectar

CLAVES = {
    "solicitante1": "Repara-sol1",
    "solicitante2": "Repara-sol2",
    "coordinador1": "Repara-coo1",
    "tecnico1": "Repara-tec1",
    "tecnico2": "Repara-tec2",
}

DESCRIPCION = "El tomacorriente del puesto 4 no tiene energía"
SOLUCION = "Se reemplazó el tomacorriente y se probó con carga"
MOTIVO_RECHAZO = "El daño sigue presente"
MOTIVO_REAPERTURA = "La fuga volvió a aparecer"


class RelojControlado:
    """Reloj de pruebas: la hora solo cambia cuando la prueba lo indica."""

    def __init__(self):
        self.ahora = datetime(2026, 10, 1, 8, 0, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.ahora

    def fijar(self, fecha):
        self.ahora = fecha

    def avanzar(self, **delta):
        self.ahora += timedelta(**delta)


@pytest.fixture
def reloj():
    return RelojControlado()


@pytest.fixture
def ruta_db(tmp_path):
    return str(tmp_path / "prueba.sqlite")


def crear_app(ruta_db, reloj):
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "clave-solo-para-pruebas",
            "DATABASE": ruta_db,
            "RELOJ": reloj,
            # Hash real pero barato, para que la batería de pruebas sea rápida.
            "PASSWORD_HASH_METHOD": "pbkdf2:sha256:1000",
        }
    )


@pytest.fixture
def app(ruta_db, reloj):
    return crear_app(ruta_db, reloj)


@pytest.fixture
def db(app, ruta_db):
    """Conexión directa a la base de la prueba para comprobar los efectos persistidos."""
    conexion = conectar(ruta_db)
    yield conexion
    conexion.close()


@pytest.fixture
def entrar(app):
    """Devuelve un cliente con la sesión iniciada como el usuario indicado."""

    def _entrar(usuario):
        cliente = app.test_client()
        respuesta = cliente.post("/login", data={"usuario": usuario, "clave": CLAVES[usuario]})
        assert respuesta.status_code == 302
        return cliente

    return _entrar


def registro_valido(**cambios):
    datos = {
        "ubicacion": "LAB-01",
        "categoria": "ELECTRICIDAD",
        "descripcion": DESCRIPCION,
        "impacto": "BAJO",
        "riesgo_personas": "false",
    }
    datos.update(cambios)
    return datos


@pytest.fixture
def flujo(entrar, db):
    """Lleva INC-000001 (de solicitante1, técnico tecnico1) hasta el estado pedido por HTTP."""

    def _hasta(estado, **registro):
        codigo = "INC-000001"
        entrar("solicitante1").post("/incidencias/nueva", data=registro_valido(**registro))
        if estado == "REGISTRADA":
            return codigo
        entrar("coordinador1").post(
            f"/incidencias/{codigo}/asignar", data={"tecnico_id": id_usuario(db, "tecnico1")}
        )
        if estado == "ASIGNADA":
            return codigo
        tecnico = entrar("tecnico1")
        tecnico.post(f"/incidencias/{codigo}/iniciar")
        if estado == "EN_ATENCION":
            return codigo
        tecnico.post(f"/incidencias/{codigo}/solucion", data={"solucion": SOLUCION})
        if estado == "PENDIENTE_VALIDACION":
            return codigo
        entrar("solicitante1").post(f"/incidencias/{codigo}/confirmar")
        assert estado == "CERRADA"
        return codigo

    return _hasta


def contar(db, tabla):
    return db.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]


def incidencia(db, codigo):
    return db.execute(
        """SELECT i.*, s.usuario AS solicitante, t.usuario AS tecnico
           FROM incidencias i
           JOIN usuarios s ON s.id = i.solicitante_id
           LEFT JOIN usuarios t ON t.id = i.tecnico_id
           WHERE i.codigo = ?""",
        (codigo,),
    ).fetchone()


def acciones(db, codigo):
    """Acciones del historial de una incidencia, en orden."""
    return [
        fila["accion"]
        for fila in db.execute(
            """SELECT e.accion FROM eventos e JOIN incidencias i ON i.id = e.incidencia_id
               WHERE i.codigo = ? ORDER BY e.id""",
            (codigo,),
        )
    ]


def id_usuario(db, usuario):
    return db.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()["id"]
