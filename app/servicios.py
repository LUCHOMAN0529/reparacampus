"""Casos de uso que cambian datos.

Cada operación sigue el orden de arquitectura.md, sección 4.3: rol, visibilidad,
estado, datos y, solo al final, una transacción que guarda estado e historial juntos.
"""
from . import dominio
from .db import transaccion
from .reloj import a_texto


def _registrar_evento(db, incidencia_id, actor_id, accion, momento, motivo=None, solucion_id=None, cierre_id=None):
    """Único punto que escribe en el historial."""
    origen, destino, _rol = dominio.TRANSICIONES[accion]
    db.execute(
        """INSERT INTO eventos (incidencia_id, actor_id, accion, estado_anterior, estado_nuevo,
                                motivo, solucion_id, cierre_id, ocurrido_en)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (incidencia_id, actor_id, accion, origen, destino, motivo, solucion_id, cierre_id, momento),
    )


def registrar_incidencia(db, usuario, datos, ahora):
    """S01. Devuelve el código generado."""
    dominio.exigir_rol(usuario["rol"], "CREAR")
    limpio = dominio.validar_registro(datos)
    prioridad = dominio.calcular_prioridad(limpio["impacto"], limpio["riesgo_personas"])
    momento = a_texto(ahora)

    with transaccion(db):
        # BEGIN IMMEDIATE ya tomó el bloqueo de escritura: el consecutivo no se repite.
        nuevo_id = db.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM incidencias").fetchone()[0]
        codigo = f"INC-{nuevo_id:06d}"
        db.execute(
            """INSERT INTO incidencias (id, codigo, solicitante_id, ubicacion, categoria, descripcion,
                                        impacto, riesgo_personas, prioridad, estado, creada_en)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'REGISTRADA', ?)""",
            (
                nuevo_id,
                codigo,
                usuario["id"],
                limpio["ubicacion"],
                limpio["categoria"],
                limpio["descripcion"],
                limpio["impacto"],
                int(limpio["riesgo_personas"]),
                prioridad,
                momento,
            ),
        )
        _registrar_evento(db, nuevo_id, usuario["id"], "CREAR", momento)
    return codigo
