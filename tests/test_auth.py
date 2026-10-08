"""Autenticación con las cinco cuentas ficticias (AC-S05-13 y límites del prototipo)."""
from conftest import CLAVES


def test_seed_tiene_cinco_cuentas_con_hash(db):
    filas = db.execute("SELECT usuario, rol, password_hash, activo FROM usuarios ORDER BY usuario").fetchall()

    assert [(f["usuario"], f["rol"]) for f in filas] == [
        ("coordinador1", "COORDINADOR"),
        ("solicitante1", "SOLICITANTE"),
        ("solicitante2", "SOLICITANTE"),
        ("tecnico1", "TECNICO"),
        ("tecnico2", "TECNICO"),
    ]
    for fila in filas:
        assert fila["activo"] == 1
        assert CLAVES[fila["usuario"]] not in fila["password_hash"]
        assert fila["password_hash"].startswith("pbkdf2:sha256:")


def test_login_correcto_inicia_sesion(app):
    cliente = app.test_client()

    respuesta = cliente.post("/login", data={"usuario": "solicitante1", "clave": "Repara-sol1"})

    assert respuesta.status_code == 302
    pagina = cliente.get("/", follow_redirects=True)
    assert "Solicitante Uno" in pagina.get_data(as_text=True)


def test_login_con_clave_incorrecta_no_inicia_sesion(app):
    cliente = app.test_client()

    respuesta = cliente.post("/login", data={"usuario": "solicitante1", "clave": "otra-clave"})

    assert respuesta.status_code == 401
    assert cliente.get("/").headers["Location"].endswith("/login")


def test_el_rol_no_se_elige_en_el_formulario(app, db):
    """Enviar un rol en el inicio de sesión no cambia el rol de la cuenta."""
    cliente = app.test_client()

    cliente.post("/login", data={"usuario": "solicitante1", "clave": "Repara-sol1", "rol": "COORDINADOR"})

    pagina = cliente.get("/", follow_redirects=True).get_data(as_text=True)
    assert "SOLICITANTE" in pagina
    assert "COORDINADOR" not in pagina


def test_sin_sesion_redirige_al_login(app):
    respuesta = app.test_client().get("/")

    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/login")


def test_logout_cierra_la_sesion(entrar):
    cliente = entrar("tecnico1")

    assert cliente.post("/logout").status_code == 302

    assert cliente.get("/").headers["Location"].endswith("/login")


def test_cuenta_inactiva_no_puede_entrar(app, db):
    db.execute("UPDATE usuarios SET activo = 0 WHERE usuario = 'tecnico2'")

    respuesta = app.test_client().post("/login", data={"usuario": "tecnico2", "clave": "Repara-tec2"})

    assert respuesta.status_code == 401
