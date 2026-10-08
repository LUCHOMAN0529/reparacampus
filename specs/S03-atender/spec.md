# SPEC S03 · Atender una incidencia

| Campo | Valor |
|---|---|
| Versión | 0.2 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Asignado: José Leonardo Hernández Pedrosa. Revisión pendiente |
| Fecha | 2026-10-08 |
| Requisito asociado | RF03 |

**Cambios de la versión 0.2 (2026-10-08):** sin cambios de contenido; se descartó una sugerencia errónea (ver registro). Origen: [revisión asistida por IA](../../docs/revision/revision-asistida-ia-2026-10-08.md), que no reemplaza la revisión del integrante asignado.

## Historia (H03)

Como **técnico**, quiero **iniciar la atención de las incidencias que tengo asignadas y registrar la solución que apliqué**, para **que el solicitante pueda comprobarla y quede constancia de mi trabajo**.

## Alcance y exclusiones

**Incluye:** inicio de atención (`ASIGNADA → EN_ATENCION`); registro de solución (`EN_ATENCION → PENDIENTE_VALIDACION`), también después de un rechazo o una reapertura; eventos en el historial.

**Excluye:** cierre por parte del técnico, edición o borrado de una solución registrada, atención por un técnico distinto del asignado, adjuntos, registro de tiempos o materiales.

## Entradas

| Operación | Campo | Tipo | Obligatorio | Valores o límites |
|---|---|---|---|---|
| Iniciar | `codigo` (en la ruta) | texto | Sí | Código de una incidencia asignada al técnico. |
| Registrar solución | `codigo` (en la ruta) | texto | Sí | Igual. |
| Registrar solución | `solucion` | texto | Sí | De 20 a 800 caracteres después de retirar espacios externos. |

## Precondiciones y permisos

- Sesión iniciada con rol `TECNICO`. Solicitante y coordinador reciben 403.
- La incidencia existe y está asignada al técnico de la sesión. Si no existe o está asignada a otro técnico, la respuesta es 404 (supuesto Q1).
- Iniciar exige estado `ASIGNADA`; registrar solución exige `EN_ATENCION`. En otro estado, 409.

## Reglas y proceso

**Iniciar atención.**

1. Comprobar sesión, rol y que la incidencia está asignada al técnico.
2. Comprobar estado `ASIGNADA`.
3. En una transacción: cambiar a `EN_ATENCION` e insertar el evento `INICIAR_ATENCION`.

**Registrar solución.**

1. Comprobar sesión, rol y asignación.
2. Comprobar estado `EN_ATENCION`.
3. Retirar espacios externos y validar la longitud.
4. En una transacción: insertar la solución (incidencia, técnico, texto, fecha), cambiar a `PENDIENTE_VALIDACION` e insertar el evento `REGISTRAR_SOLUCION` enlazado a esa solución.

Cada solución es un registro nuevo. Las soluciones anteriores nunca se modifican ni se eliminan.

## Salidas y cambios persistidos

- Iniciar: `estado = EN_ATENCION`; evento `INICIAR_ATENCION` (`ASIGNADA → EN_ATENCION`).
- Registrar solución: fila nueva en `soluciones`; `estado = PENDIENTE_VALIDACION`; evento `REGISTRAR_SOLUCION` (`EN_ATENCION → PENDIENTE_VALIDACION`) con referencia a la solución.
- Respuesta: redirección 302 al detalle.

## Errores y efectos que deben evitarse

| Situación | Respuesta | Efecto |
|---|---|---|
| Rol distinto de técnico | 403 | Ninguno |
| Incidencia inexistente o asignada a otro técnico | 404 | Ninguno |
| Iniciar en estado distinto de `ASIGNADA` | 409 | Ninguno |
| Registrar solución en estado distinto de `EN_ATENCION` | 409 | Ninguno |
| Solución ausente o fuera de 20–800 caracteres | 400 | Ninguno |

No debe ocurrir: una solución guardada sin cambio de estado o un cambio de estado sin solución; que el técnico pase la incidencia a `CERRADA`; que se pierda o sobrescriba una solución anterior.

## Criterios de aceptación

**AC-S03-01 (iniciar atención).** Dada la incidencia `INC-000001` en `ASIGNADA` con técnico `tecnico1`, cuando `tecnico1` inicia la atención, entonces queda `EN_ATENCION` y el historial suma un evento `INICIAR_ATENCION` de `tecnico1` de `ASIGNADA` a `EN_ATENCION` con su fecha.

**AC-S03-02 (registrar solución).** Dada la incidencia `INC-000001` en `EN_ATENCION` con técnico `tecnico1`, cuando `tecnico1` registra la solución “Se reemplazó el tomacorriente y se probó con carga”, entonces queda `PENDIENTE_VALIDACION`, existe una solución con ese texto, autor `tecnico1` y fecha, y el historial suma un evento `REGISTRAR_SOLUCION` enlazado a ella.

**AC-S03-03 (técnico no asignado y otros roles).** Dada una incidencia asignada a `tecnico1`, cuando `tecnico2` intenta iniciarla o registrarle una solución, entonces recibe 404 y no cambia el estado ni el historial. Cuando lo intenta un solicitante o el coordinador, entonces recibe 403 sin cambios.

**AC-S03-04 (estados incompatibles).** Dada una incidencia en `ASIGNADA`, cuando su técnico registra una solución sin haber iniciado la atención, entonces recibe 409, no se guarda la solución y el estado sigue `ASIGNADA`. Dada una incidencia en `EN_ATENCION`, `PENDIENTE_VALIDACION` o `CERRADA`, cuando su técnico intenta iniciarla, entonces recibe 409 sin cambios. Dada una incidencia en `PENDIENTE_VALIDACION` o `CERRADA`, cuando su técnico registra otra solución, entonces recibe 409 sin cambios.

**AC-S03-05 (límites de la solución).** Dada una incidencia en `EN_ATENCION`, cuando su técnico envía una solución de 19 caracteres, de 801 caracteres, vacía o de 19 caracteres rodeados de espacios, entonces recibe 400 y la incidencia sigue `EN_ATENCION` sin solución ni eventos nuevos. Cuando envía una de exactamente 20 o exactamente 800, entonces se acepta.

**AC-S03-06 (conservación de soluciones).** Dada una incidencia que volvió a `EN_ATENCION` por un rechazo o una reapertura y que ya tiene una solución, cuando su técnico registra una solución nueva, entonces hay dos soluciones, la primera conserva su texto, autor y fecha, y el estado es `PENDIENTE_VALIDACION`.

**AC-S03-07 (el técnico no cierra).** Dado un técnico con una incidencia asignada en cualquier estado, cuando intenta confirmarla, entonces recibe 403 y la incidencia no pasa a `CERRADA`.

**AC-S03-08 (texto no ejecutable).** Dada una solución que contiene `<img src=x onerror=alert(1)>`, cuando se muestra en el detalle, entonces aparece escapada y no como etiqueta.

## Diseño y tareas vinculadas a cada AC

Diseño en [plan.md](plan.md); tareas en [tasks.md](tasks.md).

| AC | Tareas |
|---|---|
| AC-S03-01 | T-S03-02, T-S03-04 |
| AC-S03-02, 06 | T-S03-01, T-S03-03, T-S03-04 |
| AC-S03-03, 04, 07 | T-S03-02, T-S03-03 |
| AC-S03-05 | T-S03-03 |
| AC-S03-08 | T-S03-04 |
| Todos | T-S03-05 |

## Pruebas y resultados esperados

| ID | AC | Entrada | Esperado |
|---|---|---|---|
| P-S03-01 | AC-S03-01 | `tecnico1` inicia `INC-000001` en `ASIGNADA` | 302; `EN_ATENCION`; 3 eventos |
| P-S03-02 | AC-S03-02 | `tecnico1` registra la solución del AC-S03-02 | 302; `PENDIENTE_VALIDACION`; 1 solución; 4 eventos |
| P-S03-03 | AC-S03-03 | `tecnico2` inicia la incidencia de `tecnico1` | 404; `ASIGNADA`; 2 eventos |
| P-S03-04 | AC-S03-04 | `tecnico1` registra solución con la incidencia en `ASIGNADA` | 409; `ASIGNADA`; 0 soluciones; 2 eventos |
| P-S03-05 | AC-S03-05 | Solución de 19 y de 20 caracteres; de 800 y de 801 | 19: 400. 20: 302. 800: 302. 801: 400 |

## Decisión de revisión / versión aprobada

| Fecha | Versión revisada | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.2 | José Leonardo Hernández Pedrosa (asignado) | Pendiente | |
