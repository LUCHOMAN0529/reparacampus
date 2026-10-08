"""Lecturas. La visibilidad por rol se define aquí una sola vez."""
from .dominio import COORDINADOR, SOLICITANTE, NoEncontrada

_SELECT_INCIDENCIA = """
    SELECT i.*, s.nombre AS solicitante_nombre, t.nombre AS tecnico_nombre
    FROM incidencias i
    JOIN usuarios s ON s.id = i.solicitante_id
    LEFT JOIN usuarios t ON t.id = i.tecnico_id
"""


def _visibilidad(usuario):
    """Condición SQL de lo que el usuario puede ver: propias, asignadas o todas."""
    if usuario["rol"] == COORDINADOR:
        return "1 = 1", ()
    if usuario["rol"] == SOLICITANTE:
        return "i.solicitante_id = ?", (usuario["id"],)
    return "i.tecnico_id = ?", (usuario["id"],)


def obtener(db, usuario, codigo):
    """Devuelve la incidencia solo si existe y el usuario puede verla; si no, 404 (Q1)."""
    condicion, parametros = _visibilidad(usuario)
    fila = db.execute(
        f"{_SELECT_INCIDENCIA} WHERE i.codigo = ? AND {condicion}", (codigo, *parametros)
    ).fetchone()
    if fila is None:
        raise NoEncontrada("La incidencia no existe.")
    return fila


def historial(db, incidencia_id):
    """Eventos en orden cronológico con autor, solución, motivo y cierre."""
    return db.execute(
        """SELECT e.id, e.accion, e.estado_anterior, e.estado_nuevo, e.motivo, e.ocurrido_en,
                  u.nombre AS actor_nombre, u.rol AS actor_rol,
                  s.texto AS solucion_texto, e.cierre_id
           FROM eventos e
           JOIN usuarios u ON u.id = e.actor_id
           LEFT JOIN soluciones s ON s.id = e.solucion_id
           WHERE e.incidencia_id = ?
           ORDER BY e.id""",
        (incidencia_id,),
    ).fetchall()
