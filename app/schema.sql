-- Esquema de ReparaCampus. Ver docs/diseno/arquitectura.md, sección 2.
-- Las fechas son texto ISO 8601 en UTC con microsegundos.

CREATE TABLE IF NOT EXISTS usuarios (
    id            INTEGER PRIMARY KEY,
    usuario       TEXT NOT NULL UNIQUE,
    nombre        TEXT NOT NULL,
    rol           TEXT NOT NULL CHECK (rol IN ('SOLICITANTE', 'COORDINADOR', 'TECNICO')),
    password_hash TEXT NOT NULL,
    activo        INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS incidencias (
    id              INTEGER PRIMARY KEY,
    codigo          TEXT NOT NULL UNIQUE,
    solicitante_id  INTEGER NOT NULL REFERENCES usuarios (id),
    ubicacion       TEXT NOT NULL CHECK (ubicacion IN ('LAB-01', 'AULA-201', 'BIB-01')),
    categoria       TEXT NOT NULL CHECK (categoria IN ('ELECTRICIDAD', 'HIDRAULICA', 'MOBILIARIO', 'TIC')),
    descripcion     TEXT NOT NULL CHECK (length(descripcion) BETWEEN 20 AND 500),
    impacto         TEXT NOT NULL CHECK (impacto IN ('BAJO', 'ALTO')),
    riesgo_personas INTEGER NOT NULL CHECK (riesgo_personas IN (0, 1)),
    prioridad       TEXT NOT NULL CHECK (prioridad IN ('CRITICA', 'ALTA', 'NORMAL')),
    estado          TEXT NOT NULL CHECK (estado IN ('REGISTRADA', 'ASIGNADA', 'EN_ATENCION', 'PENDIENTE_VALIDACION', 'CERRADA')),
    tecnico_id      INTEGER REFERENCES usuarios (id),
    creada_en       TEXT NOT NULL,
    -- Una incidencia REGISTRADA no tiene técnico; en cualquier otro estado sí.
    CHECK ((estado = 'REGISTRADA') = (tecnico_id IS NULL))
);

CREATE TABLE IF NOT EXISTS asignaciones (
    id             INTEGER PRIMARY KEY,
    incidencia_id  INTEGER NOT NULL UNIQUE REFERENCES incidencias (id),
    tecnico_id     INTEGER NOT NULL REFERENCES usuarios (id),
    coordinador_id INTEGER NOT NULL REFERENCES usuarios (id),
    asignada_en    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS soluciones (
    id            INTEGER PRIMARY KEY,
    incidencia_id INTEGER NOT NULL REFERENCES incidencias (id),
    tecnico_id    INTEGER NOT NULL REFERENCES usuarios (id),
    texto         TEXT NOT NULL CHECK (length(texto) BETWEEN 20 AND 800),
    registrada_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cierres (
    id             INTEGER PRIMARY KEY,
    incidencia_id  INTEGER NOT NULL REFERENCES incidencias (id),
    solucion_id    INTEGER NOT NULL UNIQUE REFERENCES soluciones (id),
    confirmado_por INTEGER NOT NULL REFERENCES usuarios (id),
    cerrada_en     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eventos (
    id              INTEGER PRIMARY KEY,
    incidencia_id   INTEGER NOT NULL REFERENCES incidencias (id),
    actor_id        INTEGER NOT NULL REFERENCES usuarios (id),
    accion          TEXT NOT NULL CHECK (accion IN ('CREAR', 'ASIGNAR', 'INICIAR_ATENCION', 'REGISTRAR_SOLUCION',
                                                    'CONFIRMAR_SOLUCION', 'RECHAZAR_SOLUCION', 'REABRIR')),
    estado_anterior TEXT,
    estado_nuevo    TEXT NOT NULL,
    motivo          TEXT CHECK (motivo IS NULL OR length(motivo) BETWEEN 10 AND 300),
    solucion_id     INTEGER REFERENCES soluciones (id),
    cierre_id       INTEGER REFERENCES cierres (id),
    ocurrido_en     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_eventos_incidencia ON eventos (incidencia_id, id);
CREATE INDEX IF NOT EXISTS idx_incidencias_solicitante ON incidencias (solicitante_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_tecnico ON incidencias (tecnico_id);

-- Historial inmutable (S05, AC-S05-05): solo se permite insertar.
CREATE TRIGGER IF NOT EXISTS eventos_sin_update BEFORE UPDATE ON eventos
BEGIN SELECT RAISE(ABORT, 'El historial no se puede modificar'); END;
CREATE TRIGGER IF NOT EXISTS eventos_sin_delete BEFORE DELETE ON eventos
BEGIN SELECT RAISE(ABORT, 'El historial no se puede borrar'); END;

CREATE TRIGGER IF NOT EXISTS soluciones_sin_update BEFORE UPDATE ON soluciones
BEGIN SELECT RAISE(ABORT, 'Las soluciones no se pueden modificar'); END;
CREATE TRIGGER IF NOT EXISTS soluciones_sin_delete BEFORE DELETE ON soluciones
BEGIN SELECT RAISE(ABORT, 'Las soluciones no se pueden borrar'); END;

CREATE TRIGGER IF NOT EXISTS cierres_sin_update BEFORE UPDATE ON cierres
BEGIN SELECT RAISE(ABORT, 'Los cierres no se pueden modificar'); END;
CREATE TRIGGER IF NOT EXISTS cierres_sin_delete BEFORE DELETE ON cierres
BEGIN SELECT RAISE(ABORT, 'Los cierres no se pueden borrar'); END;

-- No hay reasignación (S02, AC-S02-06) ni borrado de reportes.
CREATE TRIGGER IF NOT EXISTS asignaciones_sin_update BEFORE UPDATE ON asignaciones
BEGIN SELECT RAISE(ABORT, 'Una asignación no se puede modificar'); END;
CREATE TRIGGER IF NOT EXISTS asignaciones_sin_delete BEFORE DELETE ON asignaciones
BEGIN SELECT RAISE(ABORT, 'Una asignación no se puede borrar'); END;
CREATE TRIGGER IF NOT EXISTS incidencias_sin_delete BEFORE DELETE ON incidencias
BEGIN SELECT RAISE(ABORT, 'Una incidencia no se puede borrar'); END;
