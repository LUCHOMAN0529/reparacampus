# SPEC S03 · Atender una incidencia

| Campo | Valor |
|---|---|
| Versión | 0.4 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Asignado: José Leonardo Hernández Pedrosa. Revisión pendiente |
| Fecha | 2026-10-08 |
| Requisito asociado | RF03 |

**Cambios de la versión 0.2 (2026-10-08):** sin cambios de contenido; se descartó una sugerencia errónea (ver registro). Origen: [revisión asistida por IA](../../docs/revision/revision-asistida-ia-2026-10-08.md), que no reemplaza la revisión del integrante asignado.

**Cambios de la versión 0.3 (2026-10-08):** nuevo AC-S03-09 (sin efectos parciales); la tabla de pruebas indica el estado de partida de cada conteo de eventos, refleja las pruebas reales e identifica la que falta. Origen: [segunda revisión asistida por IA](../../docs/revision/revision-asistida-ia-02-chatgpt.md), que tampoco reemplaza la revisión del integrante asignado.

**Cambios de la versión 0.4 (2026-10-08):** la prueba P-S03-12 ya está automatizada y se registra con su nombre real. No cambia ningún requisito ni criterio.

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

**AC-S03-09 (sin efectos parciales).** Dada una incidencia `ASIGNADA` o `EN_ATENCION`, cuando falla el guardado del evento al iniciar la atención o al registrar la solución, entonces la transacción se revierte: el estado no cambia, no queda ninguna solución nueva y el historial no cambia.

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
| AC-S03-09 | T-S03-06 |

## Pruebas y resultados esperados

El resultado esperado se define aquí, antes de ejecutar, y no se calcula con la función de producción. Salvo que se indique otra cosa, cada prueba parte de una base SQLite nueva y aislada que solo contiene las cinco cuentas del seed, con el reloj del servidor fijado en `2026-10-01T08:00:00Z`. Todas las pruebas de esta tabla existen en el repositorio y se ejecutaron el 2026-10-08 dentro de la batería completa (`python -m pytest`: 176 aprobadas sobre `6b99fec`); el detalle está en `docs/validacion/validacion.md` de la rama `docs/evidencias`.

| ID | AC | Precondición y entrada | Esperado | Prueba automatizada |
|---|---|---|---|---|
| P-S03-01 | AC-S03-01 | `INC-000001` `ASIGNADA` a `tecnico1`, con 2 eventos (`CREAR`, `ASIGNAR`); a las 09:00 `tecnico1` inicia | 302; `EN_ATENCION`; 3 eventos; el tercero es `INICIAR_ATENCION` de `tecnico1` con fecha `09:00` | `test_p_s03_01_iniciar_atencion` |
| P-S03-02 | AC-S03-02 | `INC-000001` `EN_ATENCION`, con 3 eventos; `tecnico1` registra la solución del AC-S03-02 | 302; `PENDIENTE_VALIDACION`; 1 solución de `tecnico1`; 4 eventos; el cuarto enlaza la solución | `test_p_s03_02_registrar_solucion` |
| P-S03-03 | AC-S03-03 | `tecnico2` inicia la incidencia `ASIGNADA` a `tecnico1`, y le registra una solución cuando está `EN_ATENCION` | 404; mismo estado y mismo historial; 0 soluciones | `test_p_s03_03_tecnico_no_asignado` |
| P-S03-04 | AC-S03-04 | `INC-000001` `ASIGNADA`, con 2 eventos; `tecnico1` registra una solución sin iniciar | 409; `ASIGNADA`; 0 soluciones; 2 eventos | `test_p_s03_04_solucion_antes_de_iniciar` |
| P-S03-05 | AC-S03-05 | `INC-000001` `EN_ATENCION`; solución de 19, 20, 800 y 801 caracteres, vacía, y de 19 rodeada de espacios | 19: 400. 20: 302. 800: 302. 801: 400. Vacía: 400. Con espacios: 400. En los rechazos: `EN_ATENCION`, 0 soluciones, 3 eventos | `test_p_s03_05_limites_de_la_solucion` |
| P-S03-06 | AC-S03-03 | `solicitante1` y `coordinador1` intentan iniciar y registrar solución sobre una `ASIGNADA` | 403; `ASIGNADA`; 2 eventos | `test_otros_roles_no_atienden` |
| P-S03-07 | AC-S03-04 | `tecnico1` inicia una incidencia en `EN_ATENCION`, `PENDIENTE_VALIDACION` y `CERRADA` | 409; mismo estado y mismo historial | `test_iniciar_en_estado_incompatible` (`CERRADA` desde `de49d68`) |
| P-S03-08 | AC-S03-04 | `tecnico1` registra otra solución en `PENDIENTE_VALIDACION` y en `CERRADA` | 409; sigue habiendo 1 solución | `test_segunda_solucion_sin_rechazo_se_rechaza` (`CERRADA` desde `de49d68`) |
| P-S03-09 | AC-S03-08 | Solución `<img src=x onerror=alert(1)> se cambió la pieza` | El detalle la muestra escapada | `test_la_solucion_no_se_ejecuta_como_html` |
| P-S03-10 | AC-S03-06 | Nueva solución tras un rechazo y tras una reapertura | Ver P-S04-02 y P-S04-03: 2 soluciones, la primera intacta | `test_p_s04_02_rechazo_y_nueva_solucion`, `test_p_s04_03_reapertura_y_nuevo_cierre` |
| P-S03-11 | AC-S03-07 | `tecnico1` y `tecnico2` intentan confirmar una `PENDIENTE_VALIDACION` | Ver P-S04-05: 403; 0 cierres | `test_p_s04_05_solo_el_duenio_valida` |
| P-S03-12 | AC-S03-09 | Iniciar y registrar solución mientras se fuerza un fallo al guardar el evento | La operación falla; las cinco tablas quedan idénticas fila a fila (mismo estado, 0 soluciones nuevas, mismo historial); sin el fallo, la misma operación se completa | `test_un_fallo_al_guardar_el_evento_revierte_toda_la_operacion`, casos `P-S03-12-iniciar` y `P-S03-12-solucion`, en `tests/test_atomicidad.py` (commit `6b99fec`, rama `docs/evidencias`) |

## Decisión de revisión / versión aprobada

| Fecha | Versión revisada | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.4 | José Leonardo Hernández Pedrosa (asignado) | Pendiente | |
