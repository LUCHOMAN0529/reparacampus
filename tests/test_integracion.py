"""Pruebas de integración: recorrido completo por HTTP contra un archivo SQLite real.

Cada paso lo ejecuta el actor que corresponde, con su propia sesión. Después se
comprueban los efectos persistidos con una conexión independiente a la base.
"""
from datetime import datetime, timedelta, timezone

import pytest

from conftest import MOTIVO_REAPERTURA, MOTIVO_RECHAZO, SOLUCION, acciones, contar, id_usuario, incidencia, registro_valido

pytestmark = pytest.mark.integracion

SEGUNDA_SOLUCION = "Se cambió el cableado del circuito y se midió el voltaje"


def _hasta_pendiente(entrar, db, codigo="INC-000001"):
    entrar("solicitante1").post("/incidencias/nueva", data=registro_valido())
    entrar("coordinador1").post(f"/incidencias/{codigo}/asignar", data={"tecnico_id": id_usuario(db, "tecnico1")})
    tecnico = entrar("tecnico1")
    tecnico.post(f"/incidencias/{codigo}/iniciar")
    tecnico.post(f"/incidencias/{codigo}/solucion", data={"solucion": SOLUCION})
    return codigo


def test_p_s04_01_flujo_de_cierre(entrar, db):
    """P-S04-01 · registrar → asignar → iniciar → proponer → confirmar"""
    solicitante, coordinador, tecnico = entrar("solicitante1"), entrar("coordinador1"), entrar("tecnico1")

    assert solicitante.post("/incidencias/nueva", data=registro_valido()).status_code == 302
    assert incidencia(db, "INC-000001")["estado"] == "REGISTRADA"
    assert coordinador.post("/incidencias/INC-000001/asignar", data={"tecnico_id": id_usuario(db, "tecnico1")}).status_code == 302
    assert incidencia(db, "INC-000001")["estado"] == "ASIGNADA"
    assert tecnico.post("/incidencias/INC-000001/iniciar").status_code == 302
    assert incidencia(db, "INC-000001")["estado"] == "EN_ATENCION"
    assert tecnico.post("/incidencias/INC-000001/solucion", data={"solucion": SOLUCION}).status_code == 302
    assert incidencia(db, "INC-000001")["estado"] == "PENDIENTE_VALIDACION"
    assert solicitante.post("/incidencias/INC-000001/confirmar").status_code == 302

    fila = incidencia(db, "INC-000001")
    assert fila["estado"] == "CERRADA"
    assert fila["tecnico"] == "tecnico1"
    assert contar(db, "soluciones") == 1
    assert contar(db, "cierres") == 1
    assert acciones(db, "INC-000001") == [
        "CREAR", "ASIGNAR", "INICIAR_ATENCION", "REGISTRAR_SOLUCION", "CONFIRMAR_SOLUCION",
    ]
    actores = [
        f["usuario"]
        for f in db.execute("SELECT u.usuario FROM eventos e JOIN usuarios u ON u.id = e.actor_id ORDER BY e.id")
    ]
    assert actores == ["solicitante1", "coordinador1", "tecnico1", "tecnico1", "solicitante1"]


def test_p_s04_02_rechazo_y_nueva_solucion(entrar, db):
    """P-S04-02 · … → proponer → rechazar → nueva solución → confirmar"""
    codigo = _hasta_pendiente(entrar, db)
    solicitante, tecnico = entrar("solicitante1"), entrar("tecnico1")

    assert solicitante.post(f"/incidencias/{codigo}/rechazar", data={"motivo": MOTIVO_RECHAZO}).status_code == 302

    fila = incidencia(db, codigo)
    assert fila["estado"] == "EN_ATENCION"
    assert fila["tecnico"] == "tecnico1"
    assert contar(db, "soluciones") == 1

    assert tecnico.post(f"/incidencias/{codigo}/solucion", data={"solucion": SEGUNDA_SOLUCION}).status_code == 302
    assert solicitante.post(f"/incidencias/{codigo}/confirmar").status_code == 302

    fila = incidencia(db, codigo)
    assert fila["estado"] == "CERRADA"
    assert fila["tecnico"] == "tecnico1"
    textos = [f["texto"] for f in db.execute("SELECT texto FROM soluciones ORDER BY id")]
    assert textos == [
        "Se reemplazó el tomacorriente y se probó con carga",
        "Se cambió el cableado del circuito y se midió el voltaje",
    ]
    cierres = db.execute("SELECT * FROM cierres").fetchall()
    assert len(cierres) == 1
    assert cierres[0]["solucion_id"] == db.execute("SELECT MAX(id) FROM soluciones").fetchone()[0]
    assert acciones(db, codigo) == [
        "CREAR", "ASIGNAR", "INICIAR_ATENCION", "REGISTRAR_SOLUCION",
        "RECHAZAR_SOLUCION", "REGISTRAR_SOLUCION", "CONFIRMAR_SOLUCION",
    ]
    rechazo = db.execute("SELECT motivo FROM eventos WHERE accion = 'RECHAZAR_SOLUCION'").fetchone()
    assert rechazo["motivo"] == "El daño sigue presente"


def test_p_s04_03_reapertura_y_nuevo_cierre(entrar, db, reloj):
    """P-S04-03 · cierre → reapertura a las 48 h → nueva solución → nuevo cierre; y fuera de plazo"""
    cierre = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    codigo = _hasta_pendiente(entrar, db)
    solicitante, tecnico = entrar("solicitante1"), entrar("tecnico1")
    reloj.fijar(cierre)
    solicitante.post(f"/incidencias/{codigo}/confirmar")

    reloj.fijar(cierre + timedelta(hours=48))
    assert solicitante.post(f"/incidencias/{codigo}/reabrir", data={"motivo": MOTIVO_REAPERTURA}).status_code == 302

    fila = incidencia(db, codigo)
    assert fila["estado"] == "EN_ATENCION"
    assert fila["tecnico"] == "tecnico1"
    assert contar(db, "cierres") == 1

    reloj.avanzar(hours=3)
    assert tecnico.post(f"/incidencias/{codigo}/solucion", data={"solucion": SEGUNDA_SOLUCION}).status_code == 302
    reloj.avanzar(hours=1)
    assert solicitante.post(f"/incidencias/{codigo}/confirmar").status_code == 302

    fila = incidencia(db, codigo)
    assert fila["estado"] == "CERRADA"
    assert fila["tecnico"] == "tecnico1"
    assert contar(db, "soluciones") == 2
    fechas = [f["cerrada_en"] for f in db.execute("SELECT cerrada_en FROM cierres ORDER BY id")]
    assert fechas == ["2026-10-01T10:00:00.000000Z", "2026-10-03T14:00:00.000000Z"]
    assert acciones(db, codigo) == [
        "CREAR", "ASIGNAR", "INICIAR_ATENCION", "REGISTRAR_SOLUCION", "CONFIRMAR_SOLUCION",
        "REABRIR", "REGISTRAR_SOLUCION", "CONFIRMAR_SOLUCION",
    ]

    # AC-S04-09: el plazo se cuenta desde el segundo cierre (2026-10-03T14:00Z).
    reloj.fijar(datetime(2026, 10, 5, 14, 0, 0, 1, tzinfo=timezone.utc))
    assert solicitante.post(f"/incidencias/{codigo}/reabrir", data={"motivo": MOTIVO_REAPERTURA}).status_code == 409
    assert incidencia(db, codigo)["estado"] == "CERRADA"
    assert len(acciones(db, codigo)) == 8
    reloj.fijar(datetime(2026, 10, 5, 14, 0, 0, tzinfo=timezone.utc))
    assert solicitante.post(f"/incidencias/{codigo}/reabrir", data={"motivo": MOTIVO_REAPERTURA}).status_code == 302
    assert contar(db, "cierres") == 2
