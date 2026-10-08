"""Conexión SQLite por petición, esquema y datos ficticios iniciales."""
import sqlite3
from contextlib import contextmanager

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash

# Cuentas ficticias del prototipo (SUP-11). No son datos reales.
CUENTAS_FICTICIAS = (
    ("solicitante1", "Solicitante Uno", "SOLICITANTE", "Repara-sol1"),
    ("solicitante2", "Solicitante Dos", "SOLICITANTE", "Repara-sol2"),
    ("coordinador1", "Coordinador Uno", "COORDINADOR", "Repara-coo1"),
    ("tecnico1", "Técnico Uno", "TECNICO", "Repara-tec1"),
    ("tecnico2", "Técnico Dos", "TECNICO", "Repara-tec2"),
)


def conectar(ruta):
    # isolation_level=None: las transacciones se abren y cierran de forma explícita.
    db = sqlite3.connect(ruta, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def get_db():
    if "db" not in g:
        g.db = conectar(current_app.config["DATABASE"])
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@contextmanager
def transaccion(db):
    """Todo o nada: estado, registros asociados y evento se guardan juntos."""
    db.execute("BEGIN IMMEDIATE")
    try:
        yield
    except BaseException:
        db.execute("ROLLBACK")
        raise
    db.execute("COMMIT")


def init_db():
    """Crea las tablas si faltan y carga las cuentas ficticias si no hay usuarios."""
    db = get_db()
    with current_app.open_resource("schema.sql") as esquema:
        db.executescript(esquema.read().decode("utf-8"))
    if db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        metodo = current_app.config["PASSWORD_HASH_METHOD"]
        with transaccion(db):
            db.executemany(
                "INSERT INTO usuarios (usuario, nombre, rol, password_hash) VALUES (?, ?, ?, ?)",
                [
                    (usuario, nombre, rol, generate_password_hash(clave, method=metodo))
                    for usuario, nombre, rol, clave in CUENTAS_FICTICIAS
                ],
            )


@click.command("init-db")
def init_db_command():
    """Crea el esquema y el seed ficticio sin borrar datos existentes."""
    init_db()
    click.echo(f"Base de datos lista en {current_app.config['DATABASE']}")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    with app.app_context():
        init_db()
