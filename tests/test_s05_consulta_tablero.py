"""S05 · Consultar, historizar y tablero (RF05). Los esperados salen de specs/S05-consultar-historizar/spec.md."""
import re
import sqlite3
from datetime import datetime, timezone

import pytest

from app import dominio
from conftest import (
    CLAVES,
    MOTIVO_REAPERTURA,
    MOTIVO_RECHAZO,
    SOLUCION,
    acciones,
    contar,
    crear_app,
    id_usuario,
    incidencia,
    registro_valido,
)

ORDEN = ["REGISTRADA", "ASIGNADA", "EN_ATENCION", "PENDIENTE_VALIDACION", "CERRADA"]


def crear(entrar, db, hasta="REGISTRADA", solicitante="solicitante1", tecnico="tecnico1", **registro):
    """Registra una incidencia nueva y la lleva por HTTP hasta el estado pedido. Devuelve su código."""
    entrar(solicitante).post("/incidencias/nueva", data=registro_valido(**registro))
    codigo = f"INC-{contar(db, 'incidencias'):06d}"
    pasos = [
        lambda: entrar("coordinador1").post(f"/incidencias/{codigo}/asignar", data={"tecnico_id": id_usuario(db, tecnico)}),
        lambda: entrar(tecnico).post(f"/incidencias/{codigo}/iniciar"),
        lambda: entrar(tecnico).post(f"/incidencias/{codigo}/solucion", data={"solucion": SOLUCION}),
        lambda: entrar(solicitante).post(f"/incidencias/{codigo}/confirmar"),
    ]
    for paso in pasos[: ORDEN.index(hasta)]:
        assert paso().status_code == 302
    assert incidencia(db, codigo)["estado"] == hasta
    return codigo


def codigos(respuesta):
    """Códigos que aparecen en la tabla del listado, en orden."""
    return re.findall(r">(INC-\d{6})</a>", respuesta.get_data(as_text=True))


def cifra(pagina, atributo, valor):
    return int(re.search(rf'data-{atributo}="{valor}">(\d+)<', pagina).group(1))


def porcentaje(pagina):
    return re.search(r'id="porcentaje-cierre">([^<]+)<', pagina).group(1)


@pytest.fixture
def tres(entrar, db):
    """INC-000001 (solicitante1, ASIGNADA a tecnico1), INC-000002 (solicitante1), INC-000003 (solicitante2)."""
    crear(entrar, db, "ASIGNADA")
    crear(entrar, db)
    crear(entrar, db, solicitante="solicitante2")


@pytest.mark.parametrize(
    "usuario, esperados",
    [
        ("solicitante1", ["INC-000002", "INC-000001"]),
        ("solicitante2", ["INC-000003"]),
        ("tecnico1", ["INC-000001"]),
        ("tecnico2", []),
        ("coordinador1", ["INC-000003", "INC-000002", "INC-000001"]),
    ],
)
def test_p_s05_01_listado_segun_permisos(entrar, tres, usuario, esperados):
    """P-S05-01 · AC-S05-01"""
    respuesta = entrar(usuario).get("/incidencias/")

    assert respuesta.status_code == 200
    assert codigos(respuesta) == esperados


@pytest.mark.parametrize(
    "usuario, codigo, esperado",
    [
        ("solicitante1", "INC-000001", 200),
        ("solicitante2", "INC-000001", 404),
        ("solicitante1", "INC-000003", 404),
        ("tecnico1", "INC-000001", 200),
        ("tecnico2", "INC-000001", 404),
        ("tecnico1", "INC-000002", 404),
        ("coordinador1", "INC-000003", 200),
        ("coordinador1", "INC-999999", 404),
    ],
)
def test_p_s05_01_detalle_segun_permisos(entrar, tres, usuario, codigo, esperado):
    """P-S05-01 · AC-S05-11"""
    assert entrar(usuario).get(f"/incidencias/{codigo}").status_code == esperado


@pytest.fixture
def variadas(entrar, db):
    """001 CRITICA ASIGNADA · 002 CRITICA REGISTRADA · 003 ALTA ASIGNADA · 004 NORMAL REGISTRADA (de solicitante2)."""
    crear(entrar, db, "ASIGNADA", riesgo_personas="true")
    crear(entrar, db, riesgo_personas="true", impacto="ALTO")
    crear(entrar, db, "ASIGNADA", impacto="ALTO")
    crear(entrar, db, solicitante="solicitante2")


@pytest.mark.parametrize(
    "consulta, esperados",
    [
        ("estado=ASIGNADA", ["INC-000003", "INC-000001"]),
        ("prioridad=CRITICA", ["INC-000002", "INC-000001"]),
        ("estado=ASIGNADA&prioridad=CRITICA", ["INC-000001"]),
        ("estado=REGISTRADA&prioridad=NORMAL", ["INC-000004"]),
        ("estado=&prioridad=", ["INC-000004", "INC-000003", "INC-000002", "INC-000001"]),
        ("estado=CERRADA", []),
    ],
)
def test_p_s05_02_filtros(entrar, variadas, consulta, esperados):
    """P-S05-02 · AC-S05-02, AC-S05-03 (valor válido sin coincidencias: 200 y lista vacía)"""
    respuesta = entrar("coordinador1").get(f"/incidencias/?{consulta}")

    assert respuesta.status_code == 200
    assert codigos(respuesta) == esperados


def test_un_filtro_no_amplia_la_visibilidad(entrar, variadas):
    """AC-S05-02"""
    assert codigos(entrar("solicitante2").get("/incidencias/?estado=ASIGNADA")) == []
    assert codigos(entrar("solicitante2").get("/incidencias/?prioridad=NORMAL")) == ["INC-000004"]
    assert codigos(entrar("tecnico1").get("/incidencias/?estado=REGISTRADA")) == []


@pytest.mark.parametrize("consulta", ["estado=ABIERTA", "prioridad=URGENTE", "estado=' OR 1=1 --"])
def test_p_s05_02_filtro_invalido(entrar, variadas, consulta):
    """P-S05-02 · AC-S05-03"""
    assert entrar("coordinador1").get(f"/incidencias/?{consulta}").status_code == 400


def test_historial_completo(entrar, db, reloj):
    """AC-S05-04"""
    codigo = crear(entrar, db, "PENDIENTE_VALIDACION")
    solicitante, tecnico = entrar("solicitante1"), entrar("tecnico1")
    solicitante.post(f"/incidencias/{codigo}/rechazar", data={"motivo": MOTIVO_RECHAZO})
    tecnico.post(f"/incidencias/{codigo}/solucion", data={"solucion": "Se cambió el cableado completo del circuito"})
    reloj.avanzar(hours=2)
    solicitante.post(f"/incidencias/{codigo}/confirmar")
    reloj.avanzar(hours=5)
    solicitante.post(f"/incidencias/{codigo}/reabrir", data={"motivo": MOTIVO_REAPERTURA})

    eventos = db.execute("SELECT * FROM eventos ORDER BY id").fetchall()
    assert [(e["accion"], e["estado_anterior"], e["estado_nuevo"]) for e in eventos] == [
        ("CREAR", None, "REGISTRADA"),
        ("ASIGNAR", "REGISTRADA", "ASIGNADA"),
        ("INICIAR_ATENCION", "ASIGNADA", "EN_ATENCION"),
        ("REGISTRAR_SOLUCION", "EN_ATENCION", "PENDIENTE_VALIDACION"),
        ("RECHAZAR_SOLUCION", "PENDIENTE_VALIDACION", "EN_ATENCION"),
        ("REGISTRAR_SOLUCION", "EN_ATENCION", "PENDIENTE_VALIDACION"),
        ("CONFIRMAR_SOLUCION", "PENDIENTE_VALIDACION", "CERRADA"),
        ("REABRIR", "CERRADA", "EN_ATENCION"),
    ]
    assert all(e["actor_id"] and e["ocurrido_en"] for e in eventos)
    assert eventos[6]["ocurrido_en"] == "2026-10-01T10:00:00.000000Z"
    assert eventos[7]["ocurrido_en"] == "2026-10-01T15:00:00.000000Z"

    for usuario in ("solicitante1", "coordinador1", "tecnico1"):
        pagina = entrar(usuario).get(f"/incidencias/{codigo}").get_data(as_text=True)
        posiciones = [
            pagina.index("Se reemplazó el tomacorriente y se probó con carga"),
            pagina.index("El daño sigue presente"),
            pagina.index("Se cambió el cableado completo del circuito"),
            pagina.index("La fuga volvió a aparecer"),
        ]
        assert posiciones == sorted(posiciones)
        assert pagina.count("<li>") == 8


@pytest.mark.parametrize("tabla", ["eventos", "soluciones", "cierres"])
def test_p_s05_04_el_historial_es_inmutable(entrar, db, tabla):
    """P-S05-04 · AC-S05-05"""
    crear(entrar, db, "CERRADA")
    antes = [tuple(fila) for fila in db.execute(f"SELECT * FROM {tabla} ORDER BY id")]
    assert antes

    with pytest.raises(sqlite3.DatabaseError):
        db.execute(f"UPDATE {tabla} SET incidencia_id = incidencia_id")
    with pytest.raises(sqlite3.DatabaseError):
        db.execute(f"DELETE FROM {tabla}")

    assert [tuple(fila) for fila in db.execute(f"SELECT * FROM {tabla} ORDER BY id")] == antes


def test_no_hay_rutas_para_editar_o_borrar(app):
    """AC-S05-05"""
    for regla in app.url_map.iter_rules():
        assert not regla.methods & {"PUT", "PATCH", "DELETE"}, regla
    rutas_post = {regla.rule for regla in app.url_map.iter_rules() if "POST" in regla.methods}
    assert rutas_post == {
        "/login",
        "/logout",
        "/incidencias/nueva",
        "/incidencias/<codigo>/asignar",
        "/incidencias/<codigo>/iniciar",
        "/incidencias/<codigo>/solucion",
        "/incidencias/<codigo>/confirmar",
        "/incidencias/<codigo>/rechazar",
        "/incidencias/<codigo>/reabrir",
    }


def test_las_operaciones_rechazadas_no_dejan_rastro(entrar, db):
    """AC-S05-06"""
    codigo = crear(entrar, db, "PENDIENTE_VALIDACION")
    tecnico_id = id_usuario(db, "tecnico2")
    antes = [tuple(fila) for fila in db.execute("SELECT * FROM eventos ORDER BY id")]

    rechazadas = [
        entrar("coordinador1").post(f"/incidencias/{codigo}/asignar", data={"tecnico_id": tecnico_id}),
        entrar("coordinador1").post(f"/incidencias/{codigo}/confirmar"),
        entrar("tecnico1").post(f"/incidencias/{codigo}/iniciar"),
        entrar("tecnico2").post(f"/incidencias/{codigo}/solucion", data={"solucion": SOLUCION}),
        entrar("solicitante2").post(f"/incidencias/{codigo}/confirmar"),
        entrar("solicitante1").post(f"/incidencias/{codigo}/rechazar", data={"motivo": "corto"}),
        entrar("solicitante1").post(f"/incidencias/{codigo}/reabrir", data={"motivo": MOTIVO_REAPERTURA}),
    ]

    assert [r.status_code for r in rechazadas] == [409, 403, 409, 404, 404, 400, 409]
    fila = incidencia(db, codigo)
    assert (fila["estado"], fila["tecnico"]) == ("PENDIENTE_VALIDACION", "tecnico1")
    assert [tuple(f) for f in db.execute("SELECT * FROM eventos ORDER BY id")] == antes
    assert (contar(db, "soluciones"), contar(db, "cierres"), contar(db, "asignaciones")) == (1, 0, 1)


def test_p_s05_03_tablero_vacio(entrar):
    """P-S05-03 · AC-S05-07"""
    pagina = entrar("coordinador1").get("/tablero").get_data(as_text=True)

    assert porcentaje(pagina) == "0,0 %"
    for estado in ORDEN:
        assert cifra(pagina, "estado", estado) == 0
    for prioridad in ("CRITICA", "ALTA", "NORMAL"):
        assert cifra(pagina, "prioridad", prioridad) == 0
    assert "No hay incidencias críticas pendientes." in pagina


def test_p_s05_03_porcentaje_de_cierre_y_reapertura(entrar, db):
    """P-S05-03 · AC-S05-08"""
    cerrada = crear(entrar, db, "CERRADA")
    for _ in range(3):
        crear(entrar, db)
    coordinador = entrar("coordinador1")

    assert porcentaje(coordinador.get("/tablero").get_data(as_text=True)) == "25,0 %"

    entrar("solicitante1").post(f"/incidencias/{cerrada}/reabrir", data={"motivo": MOTIVO_REAPERTURA})

    assert porcentaje(coordinador.get("/tablero").get_data(as_text=True)) == "0,0 %"
    assert contar(db, "cierres") == 1
    assert "CONFIRMAR_SOLUCION" in acciones(db, cerrada)


def test_tablero_cantidades_y_criticas(entrar, db):
    """AC-S05-09"""
    crear(entrar, db, "CERRADA", riesgo_personas="true")
    crear(entrar, db, "ASIGNADA", riesgo_personas="true", impacto="ALTO")
    crear(entrar, db, impacto="ALTO")
    crear(entrar, db)

    pagina = entrar("coordinador1").get("/tablero").get_data(as_text=True)

    assert [cifra(pagina, "estado", e) for e in ORDEN] == [2, 1, 0, 0, 1]
    assert [cifra(pagina, "prioridad", p) for p in ("CRITICA", "ALTA", "NORMAL")] == [2, 1, 1]
    criticas = pagina[pagina.index('id="criticas"'):]
    assert re.findall(r">(INC-\d{6})</a>", criticas) == ["INC-000002"]
    assert porcentaje(pagina) == "25,0 %"


@pytest.mark.parametrize(
    "cerradas, total, esperado",
    [(0, 0, "0,0 %"), (1, 4, "25,0 %"), (1, 3, "33,3 %"), (2, 3, "66,7 %"), (1, 16, "6,3 %"), (5, 5, "100,0 %")],
)
def test_formato_y_redondeo_del_porcentaje(cerradas, total, esperado):
    """AC-S05-07, AC-S05-08 y supuesto Q2 (redondeo aritmético)."""
    assert dominio.porcentaje_cierre(cerradas, total) == esperado


@pytest.mark.parametrize("usuario", ["solicitante1", "tecnico1"])
def test_p_s05_06_tablero_solo_para_el_coordinador(entrar, usuario):
    """P-S05-06 · AC-S05-10"""
    assert entrar(usuario).get("/tablero").status_code == 403


@pytest.mark.parametrize("ruta", ["/incidencias/", "/incidencias/INC-000001", "/tablero", "/incidencias/nueva"])
def test_p_s05_06_sin_sesion_redirige_al_login(app, ruta):
    """P-S05-06 · AC-S05-13"""
    respuesta = app.test_client().get(ruta)

    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/login")


def test_p_s05_05_los_datos_permanecen_al_reiniciar(entrar, db, ruta_db, reloj):
    """P-S05-05 · AC-S05-12"""
    codigo = crear(entrar, db, "CERRADA")
    historial_antes = [tuple(fila) for fila in db.execute("SELECT * FROM eventos ORDER BY id")]

    # Segunda instancia de la aplicación sobre el mismo archivo: equivale a reiniciar el servidor.
    reiniciada = crear_app(ruta_db, reloj)
    cliente = reiniciada.test_client()
    assert cliente.post("/login", data={"usuario": "solicitante1", "clave": CLAVES["solicitante1"]}).status_code == 302

    assert codigos(cliente.get("/incidencias/")) == [codigo]
    pagina = cliente.get(f"/incidencias/{codigo}").get_data(as_text=True)
    assert "CERRADA" in pagina
    assert "Se reemplazó el tomacorriente y se probó con carga" in pagina
    assert [tuple(fila) for fila in db.execute("SELECT * FROM eventos ORDER BY id")] == historial_antes
    assert contar(db, "usuarios") == 5


def test_el_listado_no_ejecuta_html(entrar, db):
    """AC-S01-07 en el listado y el detalle del coordinador."""
    crear(entrar, db, descripcion="<b onmouseover=alert(1)>texto</b> de prueba larga")

    pagina = entrar("coordinador1").get("/incidencias/INC-000001").get_data(as_text=True)

    assert "<b onmouseover" not in pagina
    assert "&lt;b onmouseover=alert(1)&gt;" in pagina
