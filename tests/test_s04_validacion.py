"""S04 · Confirmar, rechazar y reabrir (RF04). Los esperados salen de specs/S04-validar/spec.md."""
from datetime import datetime, timedelta, timezone

import pytest

from conftest import MOTIVO_REAPERTURA, MOTIVO_RECHAZO, acciones, contar, id_usuario, incidencia

CIERRE = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def cerrada(flujo, reloj):
    """INC-000001 CERRADA con el último cierre en 2026-10-01T10:00:00Z."""
    reloj.fijar(CIERRE)
    return flujo("CERRADA")


def test_confirmar(entrar, db, flujo, reloj):
    """AC-S04-01"""
    codigo = flujo("PENDIENTE_VALIDACION")
    reloj.fijar(CIERRE)

    respuesta = entrar("solicitante1").post(f"/incidencias/{codigo}/confirmar")

    assert respuesta.status_code == 302
    assert incidencia(db, codigo)["estado"] == "CERRADA"
    cierres = db.execute("SELECT * FROM cierres").fetchall()
    assert len(cierres) == 1
    assert cierres[0]["confirmado_por"] == id_usuario(db, "solicitante1")
    assert cierres[0]["cerrada_en"] == "2026-10-01T10:00:00.000000Z"
    assert cierres[0]["solucion_id"] == db.execute("SELECT id FROM soluciones").fetchone()["id"]
    evento = db.execute("SELECT * FROM eventos WHERE accion = 'CONFIRMAR_SOLUCION'").fetchone()
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("PENDIENTE_VALIDACION", "CERRADA")
    assert evento["cierre_id"] == cierres[0]["id"]


def test_rechazar_conserva_tecnico_y_solucion(entrar, db, flujo, reloj):
    """AC-S04-02 (ejemplo del enunciado)"""
    codigo = flujo("PENDIENTE_VALIDACION")
    reloj.fijar(CIERRE)

    respuesta = entrar("solicitante1").post(f"/incidencias/{codigo}/rechazar", data={"motivo": MOTIVO_RECHAZO})

    assert respuesta.status_code == 302
    fila = incidencia(db, codigo)
    assert fila["estado"] == "EN_ATENCION"
    assert fila["tecnico"] == "tecnico1"
    soluciones = db.execute("SELECT * FROM soluciones").fetchall()
    assert len(soluciones) == 1
    assert soluciones[0]["texto"] == "Se reemplazó el tomacorriente y se probó con carga"
    assert contar(db, "cierres") == 0
    evento = db.execute("SELECT * FROM eventos WHERE accion = 'RECHAZAR_SOLUCION'").fetchone()
    assert evento["actor_id"] == id_usuario(db, "solicitante1")
    assert evento["ocurrido_en"] == "2026-10-01T10:00:00.000000Z"
    assert evento["motivo"] == "El daño sigue presente"
    assert evento["solucion_id"] == soluciones[0]["id"]


@pytest.mark.parametrize(
    "motivo, esperado",
    [("m" * 9, 400), ("m" * 301, 400), ("", 400), ("  " + "m" * 9 + "  ", 400), ("m" * 10, 302), ("m" * 300, 302)],
)
def test_p_s04_04_limites_del_motivo_de_rechazo(entrar, db, flujo, motivo, esperado):
    """P-S04-04 · AC-S04-03"""
    codigo = flujo("PENDIENTE_VALIDACION")

    respuesta = entrar("solicitante1").post(f"/incidencias/{codigo}/rechazar", data={"motivo": motivo})

    assert respuesta.status_code == esperado
    if esperado == 400:
        assert incidencia(db, codigo)["estado"] == "PENDIENTE_VALIDACION"
        assert len(acciones(db, codigo)) == 4
    else:
        assert incidencia(db, codigo)["estado"] == "EN_ATENCION"


@pytest.mark.parametrize(
    "usuario, esperado", [("solicitante2", 404), ("coordinador1", 403), ("tecnico1", 403), ("tecnico2", 403)]
)
@pytest.mark.parametrize("operacion", ["confirmar", "rechazar"])
def test_p_s04_05_solo_el_duenio_valida(entrar, db, flujo, usuario, esperado, operacion):
    """P-S04-05 · AC-S04-04, AC-S03-07"""
    codigo = flujo("PENDIENTE_VALIDACION")

    respuesta = entrar(usuario).post(f"/incidencias/{codigo}/{operacion}", data={"motivo": MOTIVO_RECHAZO})

    assert respuesta.status_code == esperado
    assert incidencia(db, codigo)["estado"] == "PENDIENTE_VALIDACION"
    assert len(acciones(db, codigo)) == 4
    assert contar(db, "cierres") == 0


@pytest.mark.parametrize(
    "usuario, esperado", [("solicitante2", 404), ("coordinador1", 403), ("tecnico1", 403)]
)
def test_solo_el_duenio_reabre(entrar, db, cerrada, usuario, esperado):
    """AC-S04-04"""
    respuesta = entrar(usuario).post(f"/incidencias/{cerrada}/reabrir", data={"motivo": MOTIVO_REAPERTURA})

    assert respuesta.status_code == esperado
    assert incidencia(db, cerrada)["estado"] == "CERRADA"
    assert len(acciones(db, cerrada)) == 5


@pytest.mark.parametrize("estado", ["REGISTRADA", "ASIGNADA", "EN_ATENCION", "CERRADA"])
@pytest.mark.parametrize("operacion", ["confirmar", "rechazar"])
def test_validar_en_estado_incompatible(entrar, db, flujo, estado, operacion):
    """AC-S04-05"""
    codigo = flujo(estado)
    antes = acciones(db, codigo)

    respuesta = entrar("solicitante1").post(f"/incidencias/{codigo}/{operacion}", data={"motivo": MOTIVO_RECHAZO})

    assert respuesta.status_code == 409
    assert incidencia(db, codigo)["estado"] == estado
    assert acciones(db, codigo) == antes


@pytest.mark.parametrize("estado", ["REGISTRADA", "ASIGNADA", "EN_ATENCION", "PENDIENTE_VALIDACION"])
def test_reabrir_en_estado_incompatible(entrar, db, flujo, estado):
    """AC-S04-05"""
    codigo = flujo(estado)
    antes = acciones(db, codigo)

    respuesta = entrar("solicitante1").post(f"/incidencias/{codigo}/reabrir", data={"motivo": MOTIVO_REAPERTURA})

    assert respuesta.status_code == 409
    assert incidencia(db, codigo)["estado"] == estado
    assert acciones(db, codigo) == antes


def test_reabrir_exactamente_a_las_48_horas(entrar, db, cerrada, reloj):
    """AC-S04-06"""
    reloj.fijar(datetime(2026, 10, 3, 10, 0, 0, tzinfo=timezone.utc))

    respuesta = entrar("solicitante1").post(f"/incidencias/{cerrada}/reabrir", data={"motivo": MOTIVO_REAPERTURA})

    assert respuesta.status_code == 302
    fila = incidencia(db, cerrada)
    assert fila["estado"] == "EN_ATENCION"
    assert fila["tecnico"] == "tecnico1"
    assert contar(db, "cierres") == 1
    assert contar(db, "soluciones") == 1
    evento = db.execute("SELECT * FROM eventos WHERE accion = 'REABRIR'").fetchone()
    assert evento["motivo"] == "La fuga volvió a aparecer"
    assert evento["ocurrido_en"] == "2026-10-03T10:00:00.000000Z"
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("CERRADA", "EN_ATENCION")


def test_reabrir_un_instante_despues_de_48_horas(entrar, db, cerrada, reloj):
    """AC-S04-07"""
    reloj.fijar(datetime(2026, 10, 3, 10, 0, 0, 1, tzinfo=timezone.utc))

    respuesta = entrar("solicitante1").post(f"/incidencias/{cerrada}/reabrir", data={"motivo": MOTIVO_REAPERTURA})

    assert respuesta.status_code == 409
    assert incidencia(db, cerrada)["estado"] == "CERRADA"
    assert acciones(db, cerrada) == [
        "CREAR", "ASIGNAR", "INICIAR_ATENCION", "REGISTRAR_SOLUCION", "CONFIRMAR_SOLUCION",
    ]


@pytest.mark.parametrize("motivo", ["m" * 9, "m" * 301, ""])
def test_motivo_de_reapertura_invalido(entrar, db, cerrada, reloj, motivo):
    """AC-S04-08"""
    reloj.fijar(CIERRE + timedelta(hours=1))

    respuesta = entrar("solicitante1").post(f"/incidencias/{cerrada}/reabrir", data={"motivo": motivo})

    assert respuesta.status_code == 400
    assert incidencia(db, cerrada)["estado"] == "CERRADA"
    assert len(acciones(db, cerrada)) == 5


SOLO_ESPACIOS = [" " * 15, " " * 300, "\t\n   \r\n  "]


@pytest.mark.parametrize("motivo", SOLO_ESPACIOS)
def test_p_s04_15_rechazo_con_motivo_solo_de_espacios(entrar, db, flujo, motivo):
    """P-S04-15 · AC-S04-03 · una cadena de 15 o de 300 espacios cabe en el límite, pero recortada queda vacía."""
    codigo = flujo("PENDIENTE_VALIDACION")
    antes = [tuple(fila) for fila in db.execute("SELECT * FROM eventos ORDER BY id")]

    respuesta = entrar("solicitante1").post(f"/incidencias/{codigo}/rechazar", data={"motivo": motivo})

    assert respuesta.status_code == 400
    fila = incidencia(db, codigo)
    assert (fila["estado"], fila["tecnico"]) == ("PENDIENTE_VALIDACION", "tecnico1")
    assert [tuple(f) for f in db.execute("SELECT * FROM eventos ORDER BY id")] == antes
    assert len(antes) == 4
    assert (contar(db, "soluciones"), contar(db, "cierres")) == (1, 0)


@pytest.mark.parametrize("motivo", SOLO_ESPACIOS)
def test_p_s04_15_reapertura_con_motivo_solo_de_espacios(entrar, db, cerrada, reloj, motivo):
    """P-S04-15 · AC-S04-08"""
    reloj.fijar(CIERRE + timedelta(hours=1))
    antes = [tuple(fila) for fila in db.execute("SELECT * FROM eventos ORDER BY id")]

    respuesta = entrar("solicitante1").post(f"/incidencias/{cerrada}/reabrir", data={"motivo": motivo})

    assert respuesta.status_code == 400
    fila = incidencia(db, cerrada)
    assert (fila["estado"], fila["tecnico"]) == ("CERRADA", "tecnico1")
    assert [tuple(f) for f in db.execute("SELECT * FROM eventos ORDER BY id")] == antes
    assert len(antes) == 5
    assert (contar(db, "soluciones"), contar(db, "cierres")) == (1, 1)


def test_la_hora_la_decide_el_servidor(entrar, db, cerrada, reloj):
    """AC-S04-10"""
    reloj.fijar(CIERRE + timedelta(hours=72))

    respuesta = entrar("solicitante1").post(
        f"/incidencias/{cerrada}/reabrir",
        data={"motivo": MOTIVO_REAPERTURA, "fecha": "2026-10-01T11:00:00.000000Z", "ahora": "2026-10-01T11:00:00Z"},
    )

    assert respuesta.status_code == 409
    assert incidencia(db, cerrada)["estado"] == "CERRADA"
