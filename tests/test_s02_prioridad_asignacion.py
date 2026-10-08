"""S02 · Priorizar y asignar (RF02). Los esperados salen de specs/S02-priorizar-asignar/spec.md."""
import pytest

from conftest import acciones, contar, id_usuario, incidencia, registro_valido


@pytest.fixture
def registrada(entrar):
    """INC-000001 en REGISTRADA, de solicitante1."""
    entrar("solicitante1").post("/incidencias/nueva", data=registro_valido())
    return "INC-000001"


@pytest.mark.parametrize(
    "riesgo, impacto, esperada",
    [
        ("true", "BAJO", "CRITICA"),
        ("true", "ALTO", "CRITICA"),
        ("false", "ALTO", "ALTA"),
        ("false", "BAJO", "NORMAL"),
    ],
)
def test_p_s02_01_prioridad_calculada(entrar, db, riesgo, impacto, esperada):
    """P-S02-01 · AC-S02-01, AC-S02-02, AC-S02-03"""
    entrar("solicitante1").post(
        "/incidencias/nueva", data=registro_valido(riesgo_personas=riesgo, impacto=impacto)
    )

    assert incidencia(db, "INC-000001")["prioridad"] == esperada


def test_p_s02_02_asignacion_correcta(entrar, db, registrada, reloj):
    """P-S02-02 · AC-S02-04"""
    reloj.avanzar(minutes=30)

    respuesta = entrar("coordinador1").post(
        f"/incidencias/{registrada}/asignar", data={"tecnico_id": id_usuario(db, "tecnico1")}
    )

    assert respuesta.status_code == 302
    fila = incidencia(db, registrada)
    assert fila["estado"] == "ASIGNADA"
    assert fila["tecnico"] == "tecnico1"
    asignaciones = db.execute("SELECT * FROM asignaciones").fetchall()
    assert len(asignaciones) == 1
    assert asignaciones[0]["tecnico_id"] == id_usuario(db, "tecnico1")
    assert asignaciones[0]["coordinador_id"] == id_usuario(db, "coordinador1")
    assert asignaciones[0]["asignada_en"] == "2026-10-01T08:30:00.000000Z"
    assert acciones(db, registrada) == ["CREAR", "ASIGNAR"]
    evento = db.execute("SELECT * FROM eventos WHERE accion = 'ASIGNAR'").fetchone()
    assert evento["actor_id"] == id_usuario(db, "coordinador1")
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("REGISTRADA", "ASIGNADA")


@pytest.mark.parametrize("segundo_tecnico", ["tecnico2", "tecnico1"])
def test_p_s02_03_asignacion_repetida(entrar, db, registrada, segundo_tecnico):
    """P-S02-03 · AC-S02-06"""
    coordinador = entrar("coordinador1")
    coordinador.post(f"/incidencias/{registrada}/asignar", data={"tecnico_id": id_usuario(db, "tecnico1")})

    respuesta = coordinador.post(
        f"/incidencias/{registrada}/asignar", data={"tecnico_id": id_usuario(db, segundo_tecnico)}
    )

    assert respuesta.status_code == 409
    assert incidencia(db, registrada)["tecnico"] == "tecnico1"
    assert incidencia(db, registrada)["estado"] == "ASIGNADA"
    assert contar(db, "asignaciones") == 1
    assert acciones(db, registrada) == ["CREAR", "ASIGNAR"]


@pytest.mark.parametrize("usuario", ["solicitante1", "solicitante2", "tecnico1"])
def test_p_s02_04_otros_roles_no_asignan(entrar, db, registrada, usuario):
    """P-S02-04 · AC-S02-05"""
    respuesta = entrar(usuario).post(
        f"/incidencias/{registrada}/asignar", data={"tecnico_id": id_usuario(db, "tecnico1")}
    )

    assert respuesta.status_code == 403
    fila = incidencia(db, registrada)
    assert fila["estado"] == "REGISTRADA"
    assert fila["tecnico"] is None
    assert acciones(db, registrada) == ["CREAR"]


@pytest.mark.parametrize("caso", ["inactivo", "solicitante", "inexistente", "ausente", "texto"])
def test_p_s02_05_tecnico_invalido(entrar, db, registrada, caso):
    """P-S02-05 · AC-S02-07"""
    db.execute(
        "INSERT INTO usuarios (usuario, nombre, rol, password_hash, activo) VALUES ('tecnico9', 'Técnico Inactivo', 'TECNICO', 'x', 0)"
    )
    datos = {
        "inactivo": {"tecnico_id": id_usuario(db, "tecnico9")},
        "solicitante": {"tecnico_id": id_usuario(db, "solicitante2")},
        "inexistente": {"tecnico_id": 9999},
        "ausente": {},
        "texto": {"tecnico_id": "1 OR 1=1"},
    }[caso]

    respuesta = entrar("coordinador1").post(f"/incidencias/{registrada}/asignar", data=datos)

    assert respuesta.status_code == 400
    fila = incidencia(db, registrada)
    assert fila["estado"] == "REGISTRADA"
    assert fila["tecnico"] is None
    assert contar(db, "asignaciones") == 0
    assert acciones(db, registrada) == ["CREAR"]


def test_incidencia_inexistente(entrar, db):
    """AC-S02-08"""
    respuesta = entrar("coordinador1").post(
        "/incidencias/INC-999999/asignar", data={"tecnico_id": id_usuario(db, "tecnico1")}
    )

    assert respuesta.status_code == 404
    assert contar(db, "asignaciones") == 0


def test_la_prioridad_no_se_cambia_al_asignar(entrar, db, registrada):
    """AC-S02-09"""
    entrar("coordinador1").post(
        f"/incidencias/{registrada}/asignar",
        data={"tecnico_id": id_usuario(db, "tecnico1"), "prioridad": "CRITICA"},
    )

    assert incidencia(db, registrada)["prioridad"] == "NORMAL"


def test_la_base_impide_una_segunda_asignacion(entrar, db, registrada):
    """AC-S02-06 · segunda barrera: unicidad y disparador en la base."""
    entrar("coordinador1").post(
        f"/incidencias/{registrada}/asignar", data={"tecnico_id": id_usuario(db, "tecnico1")}
    )

    with pytest.raises(Exception):
        db.execute(
            "INSERT INTO asignaciones (incidencia_id, tecnico_id, coordinador_id, asignada_en) VALUES (1, ?, ?, 'x')",
            (id_usuario(db, "tecnico2"), id_usuario(db, "coordinador1")),
        )
    with pytest.raises(Exception):
        db.execute("UPDATE asignaciones SET tecnico_id = ?", (id_usuario(db, "tecnico2"),))

    assert db.execute("SELECT tecnico_id FROM asignaciones").fetchone()[0] == id_usuario(db, "tecnico1")
