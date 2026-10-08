"""Única fuente de la hora del servidor, siempre en UTC.

La aplicación la obtiene de ``app.config["RELOJ"]`` para que las pruebas
puedan inyectar un reloj controlado sin tocar el reloj del sistema.
"""
from datetime import datetime, timezone

FORMATO = "%Y-%m-%dT%H:%M:%S.%fZ"


def ahora_utc():
    return datetime.now(timezone.utc)


def a_texto(fecha):
    return fecha.astimezone(timezone.utc).strftime(FORMATO)


def de_texto(texto):
    return datetime.strptime(texto, FORMATO).replace(tzinfo=timezone.utc)
