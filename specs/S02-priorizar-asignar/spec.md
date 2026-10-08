# SPEC S02 · Priorizar y asignar

| Campo | Valor |
|---|---|
| Versión | 0.1 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Pendiente: otro integrante del equipo |
| Fecha | 2026-10-08 |
| Requisito asociado | RF02 |

## Historia (H02)

Como **coordinador de mantenimiento**, quiero **que el sistema calcule la prioridad de cada incidencia y me permita asignarla a un técnico activo**, para **atender primero lo que pone en riesgo a las personas y que cada reporte tenga un responsable**.

## Alcance y exclusiones

**Incluye:** cálculo automático de la prioridad al registrar; asignación de una incidencia `REGISTRADA` a un técnico activo; paso a `ASIGNADA`; evento en el historial.

**Excluye:** reasignación o desasignación, cambio manual de la prioridad, restricción por especialidad del técnico, balanceo de carga y notificaciones.

## Entradas

**Cálculo de prioridad** (no es entrada del usuario; usa los datos validados en S01):

| Dato | Tipo | Valores |
|---|---|---|
| `impacto` | texto | `BAJO`, `ALTO` |
| `riesgo_personas` | booleano | `true`, `false` |

**Asignación:**

| Campo | Tipo | Obligatorio | Valores o límites |
|---|---|---|---|
| `codigo` (en la ruta) | texto | Sí | Código de una incidencia existente. |
| `tecnico_id` | entero | Sí | Identificador de un usuario con rol `TECNICO` y cuenta activa. |

## Precondiciones y permisos

- Sesión iniciada con rol `COORDINADOR`. Solicitante y técnico reciben 403.
- La incidencia existe (si no, 404) y está en `REGISTRADA` (si no, 409).
- El técnico existe, tiene rol `TECNICO` y está activo (si no, 400).

## Reglas y proceso

**Prioridad.** La calcula el servidor; nadie la elige ni la modifica.

| Riesgo para personas | Impacto | Prioridad |
|---|---|---|
| `true` | `BAJO` o `ALTO` | `CRITICA` |
| `false` | `ALTO` | `ALTA` |
| `false` | `BAJO` | `NORMAL` |

**Asignación.**

1. Comprobar sesión y rol.
2. Buscar la incidencia por código.
3. Comprobar que su estado es `REGISTRADA`.
4. Validar el técnico.
5. En una sola transacción: registrar la asignación (incidencia, técnico, coordinador, fecha), fijar el técnico en la incidencia, cambiar el estado a `ASIGNADA` e insertar el evento `ASIGNAR`.

## Salidas y cambios persistidos

- `incidencias.prioridad` fijada al registrar.
- Una fila en `asignaciones`; como máximo una por incidencia.
- `incidencias.tecnico_id` y `estado = ASIGNADA`.
- Un evento `ASIGNAR` con actor coordinador, `REGISTRADA → ASIGNADA`, fecha y técnico asignado.
- Respuesta: redirección 302 al detalle.

## Errores y efectos que deben evitarse

| Situación | Respuesta | Efecto |
|---|---|---|
| Rol distinto de coordinador | 403 | Ninguno |
| Incidencia inexistente | 404 | Ninguno |
| Incidencia en estado distinto de `REGISTRADA` | 409 | Ninguno; conserva el técnico original |
| Técnico ausente, inexistente, inactivo o usuario que no es técnico | 400 | Ninguno |

No debe ocurrir: una incidencia `ASIGNADA` sin técnico; dos asignaciones para la misma incidencia; un cambio de técnico después de asignar; una prioridad distinta de la que da la tabla.

## Criterios de aceptación

**AC-S02-01 (prioridad crítica).** Dado un registro válido con riesgo para personas `true`, cuando se crea la incidencia con impacto `BAJO` o con impacto `ALTO`, entonces su prioridad es `CRITICA` en ambos casos.

**AC-S02-02 (prioridad alta).** Dado un registro válido con riesgo `false` e impacto `ALTO`, cuando se crea la incidencia, entonces su prioridad es `ALTA`.

**AC-S02-03 (prioridad normal).** Dado un registro válido con riesgo `false` e impacto `BAJO`, cuando se crea la incidencia, entonces su prioridad es `NORMAL`.

**AC-S02-04 (asignación normal).** Dada la incidencia `INC-000001` en `REGISTRADA` y el técnico activo `tecnico1`, cuando el coordinador la asigna a `tecnico1`, entonces queda `ASIGNADA` con técnico `tecnico1`, existe una asignación con coordinador, técnico y fecha, y el historial suma un evento `ASIGNAR` del coordinador de `REGISTRADA` a `ASIGNADA`.

**AC-S02-05 (permisos).** Dada una incidencia `REGISTRADA`, cuando un solicitante (incluso su dueño) o un técnico intenta asignarla, entonces recibe 403 y la incidencia sigue `REGISTRADA`, sin técnico y sin eventos nuevos.

**AC-S02-06 (asignación repetida y estado incompatible).** Dada una incidencia ya `ASIGNADA` a `tecnico1`, cuando el coordinador intenta asignarla a `tecnico2` o de nuevo a `tecnico1`, entonces recibe 409, el técnico sigue siendo `tecnico1`, hay una sola asignación y no hay eventos nuevos. Lo mismo ocurre en `EN_ATENCION`, `PENDIENTE_VALIDACION` y `CERRADA`.

**AC-S02-07 (técnico inválido).** Dada una incidencia `REGISTRADA`, cuando el coordinador envía un `tecnico_id` ausente, inexistente, de una cuenta inactiva o de un usuario que no es técnico, entonces recibe 400 y la incidencia sigue `REGISTRADA` sin técnico ni eventos nuevos.

**AC-S02-08 (incidencia inexistente).** Dado el coordinador con sesión iniciada, cuando intenta asignar el código `INC-999999`, entonces recibe 404 y no cambia nada.

**AC-S02-09 (prioridad no manipulable).** Dado cualquier usuario, cuando envía un valor de prioridad en el registro o en la asignación, entonces se ignora y la prioridad sigue siendo la calculada.

## Diseño y tareas vinculadas a cada AC

Diseño en [plan.md](plan.md); tareas en [tasks.md](tasks.md).

| AC | Tareas |
|---|---|
| AC-S02-01 a 03, 09 | T-S02-01 |
| AC-S02-04 | T-S02-02, T-S02-03, T-S02-04 |
| AC-S02-05 a 08 | T-S02-03 |
| Todos | T-S02-05 |

## Pruebas y resultados esperados

| ID | AC | Entrada | Esperado |
|---|---|---|---|
| P-S02-01 | AC-S02-01, 02, 03 | (riesgo `true`, `BAJO`); (`true`, `ALTO`); (`false`, `ALTO`); (`false`, `BAJO`) | `CRITICA`; `CRITICA`; `ALTA`; `NORMAL` |
| P-S02-02 | AC-S02-04 | Coordinador asigna `INC-000001` a `tecnico1` | 302; `ASIGNADA`; técnico `tecnico1`; 1 asignación; 2 eventos (`CREAR`, `ASIGNAR`) |
| P-S02-03 | AC-S02-06 | Segunda asignación a `tecnico2` | 409; técnico `tecnico1`; 1 asignación; 2 eventos |
| P-S02-04 | AC-S02-05 | Solicitante dueño y técnico intentan asignar | 403; `REGISTRADA`; 1 evento |
| P-S02-05 | AC-S02-07 | `tecnico_id` de cuenta inactiva; de un solicitante; inexistente | 400; `REGISTRADA`; 1 evento |

## Decisión de revisión / versión aprobada

| Fecha | Versión revisada | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.1 | Pendiente | Pendiente | |
