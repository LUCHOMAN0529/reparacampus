"""Casos de uso que cambian datos.

Cada operación sigue el orden de arquitectura.md, sección 4.3: rol, visibilidad,
estado, datos y, solo al final, una transacción que guarda estado e historial juntos.
"""
from . import consultas, dominio
from .db import transaccion
from .reloj import a_texto, de_texto


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


def _cambiar_estado(db, incidencia_id, accion, tecnico_id=None):
    """Actualiza el estado solo si sigue en el origen de la transición.

    La condición sobre el estado cubre dos operaciones simultáneas: la segunda
    no afecta ninguna fila y se rechaza sin dejar efectos.
    """
    origen, destino, _rol = dominio.TRANSICIONES[accion]
    cursor = db.execute(
        "UPDATE incidencias SET estado = ?, tecnico_id = COALESCE(?, tecnico_id) WHERE id = ? AND estado = ?",
        (destino, tecnico_id, incidencia_id, origen),
    )
    if cursor.rowcount != 1:
        raise dominio.ErrorEstado("La incidencia cambió de estado; la operación no se aplicó.")


def asignar(db, usuario, codigo, tecnico_id, ahora):
    """S02. Solo el coordinador asigna una incidencia REGISTRADA a un técnico activo."""
    dominio.exigir_rol(usuario["rol"], "ASIGNAR")
    incidencia = consultas.obtener(db, usuario, codigo)
    dominio.exigir_estado(incidencia["estado"], "ASIGNAR")
    tecnico = db.execute(
        "SELECT id FROM usuarios WHERE id = ? AND rol = 'TECNICO' AND activo = 1",
        (tecnico_id if str(tecnico_id or "").isdigit() else None,),
    ).fetchone()
    if tecnico is None:
        raise dominio.ErrorValidacion({"tecnico_id": "Seleccione un técnico activo."})
    momento = a_texto(ahora)

    with transaccion(db):
        _cambiar_estado(db, incidencia["id"], "ASIGNAR", tecnico_id=tecnico["id"])
        db.execute(
            "INSERT INTO asignaciones (incidencia_id, tecnico_id, coordinador_id, asignada_en) VALUES (?, ?, ?, ?)",
            (incidencia["id"], tecnico["id"], usuario["id"], momento),
        )
        _registrar_evento(db, incidencia["id"], usuario["id"], "ASIGNAR", momento)


def iniciar_atencion(db, usuario, codigo, ahora):
    """S03. Solo el técnico asignado pasa ASIGNADA a EN_ATENCION."""
    dominio.exigir_rol(usuario["rol"], "INICIAR_ATENCION")
    incidencia = consultas.obtener(db, usuario, codigo)
    dominio.exigir_estado(incidencia["estado"], "INICIAR_ATENCION")
    momento = a_texto(ahora)

    with transaccion(db):
        _cambiar_estado(db, incidencia["id"], "INICIAR_ATENCION")
        _registrar_evento(db, incidencia["id"], usuario["id"], "INICIAR_ATENCION", momento)


def registrar_solucion(db, usuario, codigo, texto, ahora):
    """S03. Cada solución es un registro nuevo; las anteriores no se tocan."""
    dominio.exigir_rol(usuario["rol"], "REGISTRAR_SOLUCION")
    incidencia = consultas.obtener(db, usuario, codigo)
    dominio.exigir_estado(incidencia["estado"], "REGISTRAR_SOLUCION")
    texto = dominio.validar_texto(texto, dominio.SOLUCION_MIN, dominio.SOLUCION_MAX, "solucion")
    momento = a_texto(ahora)

    with transaccion(db):
        _cambiar_estado(db, incidencia["id"], "REGISTRAR_SOLUCION")
        solucion_id = db.execute(
            "INSERT INTO soluciones (incidencia_id, tecnico_id, texto, registrada_en) VALUES (?, ?, ?, ?)",
            (incidencia["id"], usuario["id"], texto, momento),
        ).lastrowid
        _registrar_evento(
            db, incidencia["id"], usuario["id"], "REGISTRAR_SOLUCION", momento, solucion_id=solucion_id
        )


def _solucion_vigente(db, incidencia_id):
    return db.execute(
        "SELECT id FROM soluciones WHERE incidencia_id = ? ORDER BY id DESC LIMIT 1", (incidencia_id,)
    ).fetchone()["id"]


def confirmar(db, usuario, codigo, ahora):
    """S04. Solo el solicitante dueño cierra; cada confirmación deja un cierre."""
    dominio.exigir_rol(usuario["rol"], "CONFIRMAR_SOLUCION")
    incidencia = consultas.obtener(db, usuario, codigo)
    dominio.exigir_estado(incidencia["estado"], "CONFIRMAR_SOLUCION")
    solucion_id = _solucion_vigente(db, incidencia["id"])
    momento = a_texto(ahora)

    with transaccion(db):
        _cambiar_estado(db, incidencia["id"], "CONFIRMAR_SOLUCION")
        cierre_id = db.execute(
            "INSERT INTO cierres (incidencia_id, solucion_id, confirmado_por, cerrada_en) VALUES (?, ?, ?, ?)",
            (incidencia["id"], solucion_id, usuario["id"], momento),
        ).lastrowid
        _registrar_evento(
            db,
            incidencia["id"],
            usuario["id"],
            "CONFIRMAR_SOLUCION",
            momento,
            solucion_id=solucion_id,
            cierre_id=cierre_id,
        )


def rechazar(db, usuario, codigo, motivo, ahora):
    """S04. Vuelve a EN_ATENCION con el mismo técnico; la solución rechazada se conserva."""
    dominio.exigir_rol(usuario["rol"], "RECHAZAR_SOLUCION")
    incidencia = consultas.obtener(db, usuario, codigo)
    dominio.exigir_estado(incidencia["estado"], "RECHAZAR_SOLUCION")
    motivo = dominio.validar_texto(motivo, dominio.MOTIVO_MIN, dominio.MOTIVO_MAX, "motivo")
    solucion_id = _solucion_vigente(db, incidencia["id"])
    momento = a_texto(ahora)

    with transaccion(db):
        _cambiar_estado(db, incidencia["id"], "RECHAZAR_SOLUCION")
        _registrar_evento(
            db,
            incidencia["id"],
            usuario["id"],
            "RECHAZAR_SOLUCION",
            momento,
            motivo=motivo,
            solucion_id=solucion_id,
        )


def reabrir(db, usuario, codigo, motivo, ahora):
    """S04. Hasta 48 horas después del último cierre, según el reloj del servidor en UTC."""
    dominio.exigir_rol(usuario["rol"], "REABRIR")
    incidencia = consultas.obtener(db, usuario, codigo)
    dominio.exigir_estado(incidencia["estado"], "REABRIR")
    ultimo_cierre = db.execute(
        "SELECT id, cerrada_en FROM cierres WHERE incidencia_id = ? ORDER BY id DESC LIMIT 1",
        (incidencia["id"],),
    ).fetchone()
    if not dominio.dentro_de_plazo_reapertura(de_texto(ultimo_cierre["cerrada_en"]), ahora):
        raise dominio.ErrorEstado("Pasaron más de 48 horas desde el último cierre; ya no se puede reabrir.")
    motivo = dominio.validar_texto(motivo, dominio.MOTIVO_MIN, dominio.MOTIVO_MAX, "motivo")
    momento = a_texto(ahora)

    with transaccion(db):
        _cambiar_estado(db, incidencia["id"], "REABRIR")
        _registrar_evento(
            db,
            incidencia["id"],
            usuario["id"],
            "REABRIR",
            momento,
            motivo=motivo,
            cierre_id=ultimo_cierre["id"],
        )
