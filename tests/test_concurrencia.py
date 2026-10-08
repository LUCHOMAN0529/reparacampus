"""Registros simultáneos: códigos distintos y consecutivos, y datos consistentes (AC-S01-10, SUP-14)."""
import threading

import pytest

from conftest import contar, registro_valido

SIMULTANEOS = 8


@pytest.mark.parametrize("repeticion", range(5))
def test_p_s01_11_registros_simultaneos(entrar, db, repeticion):
    """P-S01-11 · AC-S01-10

    Ocho hilos envían un registro válido al mismo tiempo, cada uno con su propia
    sesión y su propia conexión a la misma base SQLite. Se repite cinco veces
    porque un problema de concurrencia puede no aparecer en una sola ejecución.
    """
    usuarios = ["solicitante1", "solicitante2"] * (SIMULTANEOS // 2)
    # Las sesiones se inician antes, para que los hilos compitan solo en el registro.
    clientes = [entrar(usuario) for usuario in usuarios]
    salida = threading.Barrier(SIMULTANEOS)
    resultados = [None] * SIMULTANEOS

    def registrar(indice):
        salida.wait()
        try:
            respuesta = clientes[indice].post(
                "/incidencias/nueva", data=registro_valido(descripcion=f"Registro simultáneo número {indice:02d}")
            )
            resultados[indice] = (respuesta.status_code, respuesta.headers.get("Location", ""))
        except Exception as error:  # el hilo no debe ocultar un fallo
            resultados[indice] = (repr(error), "")

    hilos = [threading.Thread(target=registrar, args=(i,)) for i in range(SIMULTANEOS)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join(timeout=30)
    assert not any(hilo.is_alive() for hilo in hilos)

    # Todas se crean.
    assert [estado for estado, _ in resultados] == [302] * SIMULTANEOS

    # Códigos distintos y consecutivos, sin huecos ni duplicados.
    esperados = [f"INC-{n:06d}" for n in range(1, SIMULTANEOS + 1)]
    assert sorted(destino.rsplit("/", 1)[-1] for _, destino in resultados) == esperados
    filas = db.execute(
        """SELECT i.id, i.codigo, i.descripcion, i.estado, i.prioridad, u.usuario
           FROM incidencias i JOIN usuarios u ON u.id = i.solicitante_id ORDER BY i.id"""
    ).fetchall()
    assert [fila["codigo"] for fila in filas] == esperados
    assert [fila["codigo"] for fila in filas] == [f"INC-{fila['id']:06d}" for fila in filas]

    # Cada respuesta corresponde a la incidencia de su autor y con su descripción.
    por_codigo = {fila["codigo"]: fila for fila in filas}
    for indice, (_, destino) in enumerate(resultados):
        fila = por_codigo[destino.rsplit("/", 1)[-1]]
        assert fila["descripcion"] == f"Registro simultáneo número {indice:02d}"
        assert fila["usuario"] == usuarios[indice]
        assert (fila["estado"], fila["prioridad"]) == ("REGISTRADA", "NORMAL")

    # Un evento CREAR por incidencia, del mismo autor, y nada más.
    eventos = db.execute(
        """SELECT e.incidencia_id, e.accion, e.estado_anterior, e.estado_nuevo, e.actor_id, i.solicitante_id
           FROM eventos e JOIN incidencias i ON i.id = e.incidencia_id ORDER BY e.incidencia_id"""
    ).fetchall()
    assert [evento["incidencia_id"] for evento in eventos] == [fila["id"] for fila in filas]
    for evento in eventos:
        assert (evento["accion"], evento["estado_anterior"], evento["estado_nuevo"]) == ("CREAR", None, "REGISTRADA")
        assert evento["actor_id"] == evento["solicitante_id"]
    assert contar(db, "eventos") == SIMULTANEOS
