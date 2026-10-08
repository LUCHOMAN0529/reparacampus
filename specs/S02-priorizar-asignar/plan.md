# Plan de diseño · S02 Priorizar y asignar

Versión 0.3 · 2026-10-08 · ajustado a la implementación · depende de [arquitectura](../../docs/diseno/arquitectura.md) y de S01.

## Componentes que intervienen

| Capa | Elemento | Responsabilidad |
|---|---|---|
| Dominio | `dominio.calcular_prioridad(impacto, riesgo)` | Función pura con la tabla de prioridad. Se invoca desde el registro de S01. |
| Dominio | `dominio.TRANSICIONES` | Tabla única de transiciones permitidas: acción → (estado origen, estado destino, rol). |
| Rutas | `POST /incidencias/<codigo>/asignar` | Leer `tecnico_id`, llamar al servicio. |
| Servicio | `servicios.asignar(db, usuario, codigo, tecnico_id, ahora)` | Comprobaciones y transacción. |
| Interfaz | Bloque de asignación en `incidencia_detalle.html` | Lista de técnicos activos; visible solo al coordinador y en `REGISTRADA`. |
| Persistencia | Tabla `asignaciones` con `incidencia_id` único | La base impide una segunda asignación aunque falle la comprobación del servicio. |

## Decisiones

- La prioridad se guarda en la incidencia al crearla y no se recalcula, porque los datos de origen no se editan.
- “No reasignar” se garantiza en tres niveles: no existe la acción en la tabla de transiciones, el servicio exige `REGISTRADA`, y la base tiene restricción de unicidad.
- La actualización del estado usa la condición `WHERE estado = 'REGISTRADA'` y se verifica que afectó una fila; si no, se revierte y se responde 409. Esto cubre dos asignaciones simultáneas.

## Orden de comprobaciones

Sesión → rol → existencia de la incidencia → estado → validez del técnico → transacción.
