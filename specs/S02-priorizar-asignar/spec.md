# SPEC S02 · Priorizar y asignar

| Campo | Valor |
|---|---|
| Versión | 0.3 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Asignado: Jean Marco Oyola De Martino. Revisión pendiente |
| Fecha | 2026-10-08 |
| Requisito asociado | RF02 |

**Cambios de la versión 0.2 (2026-10-08):** sin cambios de contenido; las sugerencias recibidas ya estaban cubiertas. Origen: [revisión asistida por IA](../../docs/revision/revision-asistida-ia-2026-10-08.md), que no reemplaza la revisión del integrante asignado.

**Cambios de la versión 0.3 (2026-10-08):** se aclara que el rol se comprueba antes que la existencia de la incidencia; nuevo AC-S02-10 (sin efectos parciales); la tabla de pruebas refleja las pruebas reales e identifica la que falta. Origen: [segunda revisión asistida por IA](../../docs/revision/revision-asistida-ia-02-chatgpt.md), que tampoco reemplaza la revisión del integrante asignado.

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
| Rol distinto de coordinador | 403, exista o no la incidencia: el rol se comprueba primero | Ninguno |
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

**AC-S02-10 (sin efectos parciales).** Dada una incidencia `REGISTRADA`, cuando falla el guardado del evento durante la asignación, entonces la transacción se revierte: la incidencia sigue `REGISTRADA` y sin técnico, no hay asignación y el historial no cambia.

## Diseño y tareas vinculadas a cada AC

Diseño en [plan.md](plan.md); tareas en [tasks.md](tasks.md).

| AC | Tareas |
|---|---|
| AC-S02-01 a 03, 09 | T-S02-01 |
| AC-S02-04 | T-S02-02, T-S02-03, T-S02-04 |
| AC-S02-05 a 08 | T-S02-03 |
| Todos | T-S02-05 |
| AC-S02-10 | T-S02-06 |

## Pruebas y resultados esperados

El resultado esperado se define aquí, antes de ejecutar, y no se calcula con la función de producción. Salvo que se indique otra cosa, cada prueba parte de una base SQLite nueva y aislada que solo contiene las cinco cuentas del seed, con el reloj del servidor fijado en `2026-10-01T08:00:00Z`. «Por automatizar» significa que la prueba todavía no existe.

| ID | AC | Precondición y entrada | Esperado | Prueba automatizada |
|---|---|---|---|---|
| P-S02-01 | AC-S02-01, 02, 03 | Registro con (riesgo, impacto): (`true`, `BAJO`); (`true`, `ALTO`); (`false`, `ALTO`); (`false`, `BAJO`) | `CRITICA`; `CRITICA`; `ALTA`; `NORMAL` | `test_p_s02_01_prioridad_calculada` |
| P-S02-02 | AC-S02-04 | `INC-000001` en `REGISTRADA` con 1 evento; a las 08:30 `coordinador1` la asigna a `tecnico1` | 302; `ASIGNADA`; técnico `tecnico1`; 1 asignación con coordinador y fecha `08:30`; eventos `CREAR`, `ASIGNAR` | `test_p_s02_02_asignacion_correcta` |
| P-S02-03 | AC-S02-06 | `INC-000001` ya `ASIGNADA` a `tecnico1`; el coordinador la asigna a `tecnico2` y, en otro caso, de nuevo a `tecnico1` | 409; técnico `tecnico1`; 1 asignación; 2 eventos | `test_p_s02_03_asignacion_repetida` |
| P-S02-04 | AC-S02-05 | `solicitante1` (dueño), `solicitante2` y `tecnico1` intentan asignar una `REGISTRADA` | 403; `REGISTRADA` sin técnico; 1 evento | `test_p_s02_04_otros_roles_no_asignan` |
| P-S02-05 | AC-S02-07 | `tecnico_id` de una cuenta inactiva, de un solicitante, inexistente, ausente y no numérico | 400; `REGISTRADA` sin técnico; 0 asignaciones; 1 evento | `test_p_s02_05_tecnico_invalido` |
| P-S02-06 | AC-S02-06 | `INC-000001` en `EN_ATENCION`, `PENDIENTE_VALIDACION` y `CERRADA`; el coordinador la asigna a `tecnico2` | 409; mismo estado; técnico `tecnico1`; 1 asignación; mismo historial | `test_no_se_asigna_fuera_de_registrada` (commit `de49d68`) |
| P-S02-07 | AC-S02-08 | El coordinador asigna `INC-999999` | 404; 0 asignaciones | `test_incidencia_inexistente` |
| P-S02-08 | AC-S02-09 | Asignación que además envía `prioridad=CRITICA` sobre una incidencia `NORMAL`. En el registro, ver P-S01-06 | La prioridad sigue `NORMAL` | `test_la_prioridad_no_se_cambia_al_asignar` |
| P-S02-09 | AC-S02-06 | Con `INC-000001` asignada, `INSERT` de una segunda asignación y `UPDATE` del técnico directamente en la base | La base rechaza ambos; el técnico sigue siendo `tecnico1` | `test_la_base_impide_una_segunda_asignacion` |
| P-S02-10 | AC-S02-10 | Asignación válida mientras se fuerza un fallo al guardar el evento | La operación falla; `REGISTRADA` sin técnico; 0 asignaciones; 1 evento | Por automatizar (T-S02-06) |

## Decisión de revisión / versión aprobada

| Fecha | Versión revisada | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.3 | Jean Marco Oyola De Martino (asignado) | Pendiente | |
