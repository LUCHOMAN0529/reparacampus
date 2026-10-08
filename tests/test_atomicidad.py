"""Sin efectos parciales: si falla el guardado del evento, la operación completa se revierte.

Cubre AC-S02-10, AC-S03-09 y AC-S04-11 (SPECS v0.3). El registro (AC-S01-09) se prueba
en tests/test_s01_registro.py. En cada caso se compara, fila a fila, el contenido de
todas las tablas antes y después de la operación fallida.
"""
import pytest

from app import servicios
from conftest import MOTIVO_REAPERTURA, MOTIVO_RECHAZO, id_usuario

TABLAS = ("incidencias", "asignaciones", "soluciones", "cierres", "eventos")

# operación, estado de partida, quién la ejecuta, ruta, datos del formulario, estado si no falla
OPERACIONES = [
    pytest.param("REGISTRADA", "coordinador1", "asignar", "tecnico", "ASIGNADA", id="P-S02-10-asignar"),
    pytest.param("ASIGNADA", "tecnico1", "iniciar", None, "EN_ATENCION", id="P-S03-12-iniciar"),
    pytest.param("EN_ATENCION", "tecnico1", "solucion", "solucion", "PENDIENTE_VALIDACION", id="P-S03-12-solucion"),
    pytest.param("PENDIENTE_VALIDACION", "solicitante1", "confirmar", None, "CERRADA", id="P-S04-16-confirmar"),
    pytest.param("PENDIENTE_VALIDACION", "solicitante1", "rechazar", "rechazo", "EN_ATENCION", id="P-S04-16-rechazar"),
    pytest.param("CERRADA", "solicitante1", "reabrir", "reapertura", "EN_ATENCION", id="P-S04-16-reabrir"),
]


def fotografia(db):
    """Contenido completo de las tablas que una transición puede tocar."""
    return {tabla: [tuple(fila) for fila in db.execute(f"SELECT * FROM {tabla} ORDER BY id")] for tabla in TABLAS}


def formulario(db, cual):
    return {
        None: {},
        "tecnico": {"tecnico_id": id_usuario(db, "tecnico1")},
        "solucion": {"solucion": "Se ajustó la conexión y se verificó el funcionamiento"},
        "rechazo": {"motivo": MOTIVO_RECHAZO},
        "reapertura": {"motivo": MOTIVO_REAPERTURA},
    }[cual]


@pytest.mark.parametrize("partida, usuario, ruta, datos, destino", OPERACIONES)
def test_un_fallo_al_guardar_el_evento_revierte_toda_la_operacion(
    entrar, db, flujo, monkeypatch, partida, usuario, ruta, datos, destino
):
    """P-S02-10, P-S03-12, P-S04-16 · AC-S02-10, AC-S03-09, AC-S04-11"""
    codigo = flujo(partida)
    cliente = entrar(usuario)
    antes = fotografia(db)
    assert antes["incidencias"][0][antes_columna(db, "estado")] == partida

    def evento_que_falla(*_args, **_kwargs):
        raise RuntimeError("fallo simulado al guardar el evento")

    with monkeypatch.context() as parche:
        parche.setattr(servicios, "_registrar_evento", evento_que_falla)
        with pytest.raises(RuntimeError, match="fallo simulado"):
            cliente.post(f"/incidencias/{codigo}/{ruta}", data=formulario(db, datos))

    # Nada cambió: mismo estado, mismo técnico, mismas asignaciones, soluciones, cierres y eventos.
    assert fotografia(db) == antes

    # La base no quedó con una transacción abierta: la misma operación, ya sin el fallo, se completa.
    respuesta = cliente.post(f"/incidencias/{codigo}/{ruta}", data=formulario(db, datos))
    assert respuesta.status_code == 302
    despues = fotografia(db)
    assert despues["incidencias"][0][antes_columna(db, "estado")] == destino
    assert len(despues["eventos"]) == len(antes["eventos"]) + 1


def antes_columna(db, nombre):
    """Posición de una columna de `incidencias` dentro de la fila."""
    return [fila["name"] for fila in db.execute("PRAGMA table_info(incidencias)")].index(nombre)
