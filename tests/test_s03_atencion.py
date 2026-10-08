"""S03 · Atender una incidencia (RF03). Los esperados salen de specs/S03-atender/spec.md."""
import pytest

from conftest import SOLUCION, acciones, contar, id_usuario, incidencia


def test_p_s03_01_iniciar_atencion(entrar, db, flujo, reloj):
    """P-S03-01 · AC-S03-01"""
    codigo = flujo("ASIGNADA")
    reloj.avanzar(hours=1)

    respuesta = entrar("tecnico1").post(f"/incidencias/{codigo}/iniciar")

    assert respuesta.status_code == 302
    assert incidencia(db, codigo)["estado"] == "EN_ATENCION"
    assert acciones(db, codigo) == ["CREAR", "ASIGNAR", "INICIAR_ATENCION"]
    evento = db.execute("SELECT * FROM eventos WHERE accion = 'INICIAR_ATENCION'").fetchone()
    assert evento["actor_id"] == id_usuario(db, "tecnico1")
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("ASIGNADA", "EN_ATENCION")
    assert evento["ocurrido_en"] == "2026-10-01T09:00:00.000000Z"


def test_p_s03_02_registrar_solucion(entrar, db, flujo):
    """P-S03-02 · AC-S03-02"""
    codigo = flujo("EN_ATENCION")

    respuesta = entrar("tecnico1").post(f"/incidencias/{codigo}/solucion", data={"solucion": SOLUCION})

    assert respuesta.status_code == 302
    assert incidencia(db, codigo)["estado"] == "PENDIENTE_VALIDACION"
    soluciones = db.execute("SELECT * FROM soluciones").fetchall()
    assert len(soluciones) == 1
    assert soluciones[0]["texto"] == "Se reemplazó el tomacorriente y se probó con carga"
    assert soluciones[0]["tecnico_id"] == id_usuario(db, "tecnico1")
    assert acciones(db, codigo) == ["CREAR", "ASIGNAR", "INICIAR_ATENCION", "REGISTRAR_SOLUCION"]
    evento = db.execute("SELECT * FROM eventos WHERE accion = 'REGISTRAR_SOLUCION'").fetchone()
    assert evento["solucion_id"] == soluciones[0]["id"]


@pytest.mark.parametrize("ruta, datos", [("iniciar", {}), ("solucion", {"solucion": SOLUCION})])
def test_p_s03_03_tecnico_no_asignado(entrar, db, flujo, ruta, datos):
    """P-S03-03 · AC-S03-03"""
    codigo = flujo("ASIGNADA" if ruta == "iniciar" else "EN_ATENCION")
    antes = (incidencia(db, codigo)["estado"], acciones(db, codigo))

    respuesta = entrar("tecnico2").post(f"/incidencias/{codigo}/{ruta}", data=datos)

    assert respuesta.status_code == 404
    assert (incidencia(db, codigo)["estado"], acciones(db, codigo)) == antes
    assert contar(db, "soluciones") == 0


@pytest.mark.parametrize("usuario", ["solicitante1", "coordinador1"])
def test_otros_roles_no_atienden(entrar, db, flujo, usuario):
    """AC-S03-03"""
    codigo = flujo("ASIGNADA")

    assert entrar(usuario).post(f"/incidencias/{codigo}/iniciar").status_code == 403
    assert entrar(usuario).post(f"/incidencias/{codigo}/solucion", data={"solucion": SOLUCION}).status_code == 403

    assert incidencia(db, codigo)["estado"] == "ASIGNADA"
    assert acciones(db, codigo) == ["CREAR", "ASIGNAR"]


def test_p_s03_04_solucion_antes_de_iniciar(entrar, db, flujo):
    """P-S03-04 · AC-S03-04"""
    codigo = flujo("ASIGNADA")

    respuesta = entrar("tecnico1").post(f"/incidencias/{codigo}/solucion", data={"solucion": SOLUCION})

    assert respuesta.status_code == 409
    assert incidencia(db, codigo)["estado"] == "ASIGNADA"
    assert contar(db, "soluciones") == 0
    assert acciones(db, codigo) == ["CREAR", "ASIGNAR"]


@pytest.mark.parametrize("estado", ["EN_ATENCION", "PENDIENTE_VALIDACION", "CERRADA"])
def test_iniciar_en_estado_incompatible(entrar, db, flujo, estado):
    """AC-S03-04"""
    codigo = flujo(estado)
    antes = acciones(db, codigo)

    respuesta = entrar("tecnico1").post(f"/incidencias/{codigo}/iniciar")

    assert respuesta.status_code == 409
    assert incidencia(db, codigo)["estado"] == estado
    assert acciones(db, codigo) == antes


@pytest.mark.parametrize("estado", ["PENDIENTE_VALIDACION", "CERRADA"])
def test_segunda_solucion_sin_rechazo_se_rechaza(entrar, db, flujo, estado):
    """AC-S03-04"""
    codigo = flujo(estado)

    respuesta = entrar("tecnico1").post(
        f"/incidencias/{codigo}/solucion", data={"solucion": "Otra solución distinta de la anterior"}
    )

    assert respuesta.status_code == 409
    assert contar(db, "soluciones") == 1


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("s" * 19, 400),
        ("s" * 20, 302),
        ("s" * 800, 302),
        ("s" * 801, 400),
        ("", 400),
        ("   " + "s" * 19 + "   ", 400),
    ],
)
def test_p_s03_05_limites_de_la_solucion(entrar, db, flujo, texto, esperado):
    """P-S03-05 · AC-S03-05"""
    codigo = flujo("EN_ATENCION")

    respuesta = entrar("tecnico1").post(f"/incidencias/{codigo}/solucion", data={"solucion": texto})

    assert respuesta.status_code == esperado
    if esperado == 400:
        assert incidencia(db, codigo)["estado"] == "EN_ATENCION"
        assert contar(db, "soluciones") == 0
        assert acciones(db, codigo) == ["CREAR", "ASIGNAR", "INICIAR_ATENCION"]
    else:
        assert incidencia(db, codigo)["estado"] == "PENDIENTE_VALIDACION"
        assert contar(db, "soluciones") == 1


def test_la_solucion_no_se_ejecuta_como_html(entrar, db, flujo):
    """AC-S03-08"""
    codigo = flujo("EN_ATENCION")
    texto = "<img src=x onerror=alert(1)> se cambió la pieza"

    entrar("tecnico1").post(f"/incidencias/{codigo}/solucion", data={"solucion": texto})
    pagina = entrar("solicitante1").get(f"/incidencias/{codigo}").get_data(as_text=True)

    assert "&lt;img src=x onerror=alert(1)&gt; se cambió la pieza" in pagina
    assert "<img src=x" not in pagina
