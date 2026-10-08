"""S01 · Registrar una incidencia (RF01). Los esperados salen de specs/S01-registrar/spec.md."""
import pytest

from app import servicios
from conftest import acciones, contar, id_usuario, incidencia, registro_valido


def test_p_s01_01_registro_valido(entrar, db):
    """P-S01-01 · AC-S01-01"""
    cliente = entrar("solicitante1")

    respuesta = cliente.post("/incidencias/nueva", data=registro_valido())

    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/incidencias/INC-000001")
    fila = incidencia(db, "INC-000001")
    assert fila["solicitante"] == "solicitante1"
    assert fila["estado"] == "REGISTRADA"
    assert fila["prioridad"] == "NORMAL"
    assert fila["ubicacion"] == "LAB-01"
    assert fila["categoria"] == "ELECTRICIDAD"
    assert fila["descripcion"] == "El tomacorriente del puesto 4 no tiene energía"
    assert fila["impacto"] == "BAJO"
    assert fila["riesgo_personas"] == 0
    assert fila["tecnico"] is None
    assert fila["creada_en"] == "2026-10-01T08:00:00.000000Z"
    evento = db.execute("SELECT * FROM eventos").fetchall()
    assert len(evento) == 1
    assert evento[0]["accion"] == "CREAR"
    assert evento[0]["actor_id"] == id_usuario(db, "solicitante1")
    assert evento[0]["estado_anterior"] is None
    assert evento[0]["estado_nuevo"] == "REGISTRADA"
    assert evento[0]["ocurrido_en"] == "2026-10-01T08:00:00.000000Z"


def test_p_s01_02_limites_de_la_descripcion(entrar, db):
    """P-S01-02 · AC-S01-03"""
    cliente = entrar("solicitante1")

    assert cliente.post("/incidencias/nueva", data=registro_valido(descripcion="a" * 19)).status_code == 400
    assert contar(db, "incidencias") == 0
    assert cliente.post("/incidencias/nueva", data=registro_valido(descripcion="a" * 20)).status_code == 302
    assert cliente.post("/incidencias/nueva", data=registro_valido(descripcion="a" * 500)).status_code == 302
    assert cliente.post("/incidencias/nueva", data=registro_valido(descripcion="a" * 501)).status_code == 400

    assert contar(db, "incidencias") == 2
    assert contar(db, "eventos") == 2


def test_los_espacios_externos_no_cuentan(entrar, db):
    """AC-S01-03"""
    cliente = entrar("solicitante1")

    rechazada = cliente.post("/incidencias/nueva", data=registro_valido(descripcion="   " + "a" * 19 + "   "))
    aceptada = cliente.post("/incidencias/nueva", data=registro_valido(descripcion="  " + "b" * 20 + "\n"))

    assert rechazada.status_code == 400
    assert aceptada.status_code == 302
    assert incidencia(db, "INC-000001")["descripcion"] == "b" * 20


@pytest.mark.parametrize(
    "cambio",
    [
        {"impacto": "MEDIO"},
        {"impacto": "alto"},
        {"impacto": ""},
        {"riesgo_personas": "quiza"},
        {"riesgo_personas": None},
        {"ubicacion": "LAB-99"},
        {"ubicacion": None},
        {"categoria": "JARDINERIA"},
        {"categoria": None},
        {"descripcion": None},
    ],
)
def test_p_s01_03_valores_invalidos(entrar, db, cambio):
    """P-S01-03 · AC-S01-04, AC-S01-05, AC-S01-06"""
    cliente = entrar("solicitante1")
    datos = {campo: valor for campo, valor in registro_valido(**cambio).items() if valor is not None}

    respuesta = cliente.post("/incidencias/nueva", data=datos)

    assert respuesta.status_code == 400
    assert contar(db, "incidencias") == 0
    assert contar(db, "eventos") == 0


@pytest.mark.parametrize("riesgo", ["True", "1", "on", "TRUE", "si", " true"])
def test_p_s01_12_el_riesgo_solo_acepta_true_o_false(entrar, db, riesgo):
    """P-S01-12 · AC-S01-05 · el formulario envía exactamente `true` o `false`; no hay valor por defecto."""
    cliente = entrar("solicitante1")

    respuesta = cliente.post("/incidencias/nueva", data=registro_valido(riesgo_personas=riesgo))

    assert respuesta.status_code == 400
    assert contar(db, "incidencias") == 0
    assert contar(db, "eventos") == 0


@pytest.mark.parametrize("usuario", ["coordinador1", "tecnico1"])
def test_p_s01_04_otros_roles_no_registran(entrar, db, usuario):
    """P-S01-04 · AC-S01-02"""
    respuesta = entrar(usuario).post("/incidencias/nueva", data=registro_valido())

    assert respuesta.status_code == 403
    assert contar(db, "incidencias") == 0
    assert contar(db, "eventos") == 0


def test_sin_sesion_no_registra(app, db):
    """AC-S01-02"""
    respuesta = app.test_client().post("/incidencias/nueva", data=registro_valido())

    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/login")
    assert contar(db, "incidencias") == 0


def test_p_s01_05_el_texto_no_se_ejecuta_como_html(entrar, db):
    """P-S01-05 · AC-S01-07"""
    cliente = entrar("solicitante1")
    texto = "<script>alert(1)</script> la silla está rota"

    cliente.post("/incidencias/nueva", data=registro_valido(descripcion=texto))
    pagina = cliente.get("/incidencias/INC-000001").get_data(as_text=True)

    assert incidencia(db, "INC-000001")["descripcion"] == texto
    assert "&lt;script&gt;alert(1)&lt;/script&gt; la silla está rota" in pagina
    assert "<script>alert(1)</script>" not in pagina


def test_p_s01_06_el_servidor_ignora_campos_generados(entrar, db):
    """P-S01-06 · AC-S01-08"""
    cliente = entrar("solicitante1")
    datos = registro_valido(
        codigo="INC-777777",
        estado="CERRADA",
        prioridad="CRITICA",
        solicitante_id=str(id_usuario(db, "solicitante2")),
        creada_en="2020-01-01T00:00:00.000000Z",
    )

    cliente.post("/incidencias/nueva", data=datos)

    fila = incidencia(db, "INC-000001")
    assert fila["estado"] == "REGISTRADA"
    assert fila["prioridad"] == "NORMAL"
    assert fila["solicitante"] == "solicitante1"
    assert fila["creada_en"] == "2026-10-01T08:00:00.000000Z"
    assert incidencia(db, "INC-777777") is None


def test_sin_efectos_parciales_si_falla_el_evento(entrar, db, monkeypatch):
    """AC-S01-09"""

    def evento_que_falla(*_args, **_kwargs):
        raise RuntimeError("fallo simulado al guardar el evento")

    monkeypatch.setattr(servicios, "_registrar_evento", evento_que_falla)
    cliente = entrar("solicitante1")

    with pytest.raises(RuntimeError):
        cliente.post("/incidencias/nueva", data=registro_valido())

    assert contar(db, "incidencias") == 0
    assert contar(db, "eventos") == 0


def test_los_codigos_son_consecutivos(entrar, db):
    """SUP-01"""
    entrar("solicitante1").post("/incidencias/nueva", data=registro_valido())
    entrar("solicitante2").post("/incidencias/nueva", data=registro_valido())

    assert acciones(db, "INC-000001") == ["CREAR"]
    assert incidencia(db, "INC-000002")["solicitante"] == "solicitante2"
