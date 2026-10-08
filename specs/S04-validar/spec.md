# SPEC S04 · Validar la solución: confirmar, rechazar y reabrir

| Campo | Valor |
|---|---|
| Versión | 0.4 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Asignado: Cristian David Diaz España. Revisión pendiente |
| Fecha | 2026-10-08 |
| Requisito asociado | RF04 |

**Cambios de la versión 0.2 (2026-10-08):** se agregan los límites 300 y 301 a la prueba P-S04-04. Origen: [revisión asistida por IA](../../docs/revision/revision-asistida-ia-2026-10-08.md), que no reemplaza la revisión del integrante asignado.

**Cambios de la versión 0.3 (2026-10-08):** se define «solución vigente»; se precisa que un motivo formado solo por espacios se rechaza; nuevo AC-S04-11 (sin efectos parciales); la tabla de pruebas refleja las pruebas reales e identifica las que faltan. Origen: [segunda revisión asistida por IA](../../docs/revision/revision-asistida-ia-02-chatgpt.md), que tampoco reemplaza la revisión del integrante asignado.

**Cambios de la versión 0.4 (2026-10-08):** las pruebas P-S04-15 y P-S04-16 ya están automatizadas y se registran con su nombre real. No cambia ningún requisito ni criterio.

## Historia (H04)

Como **solicitante dueño de una incidencia**, quiero **confirmar o rechazar la solución propuesta y reabrir el caso si el daño reaparece poco después del cierre**, para **que una incidencia solo quede cerrada cuando yo compruebe que se resolvió**.

## Alcance y exclusiones

**Incluye:** confirmar (`PENDIENTE_VALIDACION → CERRADA`); rechazar con motivo (`PENDIENTE_VALIDACION → EN_ATENCION`); reabrir con motivo dentro de 48 horas desde el último cierre (`CERRADA → EN_ATENCION`); conservación de técnico, soluciones y cierres.

**Excluye:** cierre automático por tiempo; confirmación, rechazo o reapertura por el coordinador o el técnico; cambio de técnico al rechazar o reabrir; reapertura fuera de plazo; edición de motivos.

## Entradas

| Operación | Campo | Tipo | Obligatorio | Valores o límites |
|---|---|---|---|---|
| Confirmar | `codigo` (en la ruta) | texto | Sí | Código de una incidencia propia. |
| Rechazar | `motivo` | texto | Sí | De 10 a 300 caracteres después de retirar espacios externos. |
| Reabrir | `motivo` | texto | Sí | De 10 a 300 caracteres después de retirar espacios externos. |

La hora efectiva de cada operación la fija el servidor en UTC. Cualquier fecha enviada por el cliente se ignora.

## Precondiciones y permisos

- Sesión iniciada con rol `SOLICITANTE`. Coordinador y técnico reciben 403.
- La incidencia existe y su autor es el usuario de la sesión. Si no existe o es de otro solicitante, la respuesta es 404 (supuesto Q1).
- Confirmar y rechazar exigen `PENDIENTE_VALIDACION`. Reabrir exige `CERRADA`. En otro estado, 409.
- Reabrir exige que el tiempo transcurrido desde el último cierre sea menor o igual a 48 horas. Fuera de plazo, 409.

## Reglas y proceso

**Solución vigente.** Es la última solución registrada para la incidencia, es decir, la que la llevó al estado `PENDIENTE_VALIDACION` actual. Si hubo rechazos o reaperturas, las soluciones anteriores se conservan pero ya no son la vigente.

**Confirmar.** En una transacción: registrar un cierre (incidencia, solución vigente, quién confirma, fecha), cambiar a `CERRADA` e insertar el evento `CONFIRMAR_SOLUCION` enlazado al cierre.

**Rechazar.** Validar el motivo. En una transacción: cambiar a `EN_ATENCION` e insertar el evento `RECHAZAR_SOLUCION` con el motivo y la referencia a la solución rechazada. El técnico no cambia. La solución rechazada se conserva.

**Reabrir.**

1. Comprobar sesión, rol, pertenencia y estado `CERRADA`.
2. Tomar la fecha del cierre más reciente de la incidencia.
3. Calcular `ahora_utc − fecha_del_último_cierre` con el reloj del servidor. Si es mayor que 48 horas, rechazar con 409.
4. Validar el motivo.
5. En una transacción: cambiar a `EN_ATENCION` e insertar el evento `REABRIR` con el motivo y la referencia al cierre que se reabre. El técnico no cambia. Todos los cierres y soluciones anteriores se conservan.

El límite es inclusivo: exactamente 48 horas se acepta; 48 horas más un microsegundo se rechaza (supuesto Q3).

## Salidas y cambios persistidos

| Operación | Estado | Registros nuevos |
|---|---|---|
| Confirmar | `CERRADA` | Una fila en `cierres`; evento `CONFIRMAR_SOLUCION`. |
| Rechazar | `EN_ATENCION` | Evento `RECHAZAR_SOLUCION` con motivo. |
| Reabrir | `EN_ATENCION` | Evento `REABRIR` con motivo. |

`incidencias.tecnico_id` no cambia en ninguna de las tres. Respuesta: redirección 302 al detalle.

## Errores y efectos que deben evitarse

| Situación | Respuesta | Efecto |
|---|---|---|
| Rol distinto de solicitante | 403 | Ninguno |
| Incidencia inexistente o de otro solicitante | 404 | Ninguno |
| Confirmar o rechazar fuera de `PENDIENTE_VALIDACION` | 409 | Ninguno |
| Reabrir fuera de `CERRADA` | 409 | Ninguno |
| Reabrir después de 48 horas | 409 | Ninguno |
| Motivo ausente o fuera de 10–300 caracteres | 400 | Ninguno |

No debe ocurrir: un cierre sin evento o un evento sin cierre; pérdida de una solución o de un cierre anterior; cambio de técnico; uso de una hora elegida por el navegador; que el coordinador o el técnico cierren o reabran.

## Criterios de aceptación

**AC-S04-01 (confirmar).** Dada la incidencia propia `INC-000001` en `PENDIENTE_VALIDACION` con técnico `tecnico1` y una solución registrada, cuando `solicitante1` la confirma, entonces queda `CERRADA`, existe un cierre con esa solución, `solicitante1` y la fecha del servidor, y el historial suma un evento `CONFIRMAR_SOLUCION` de `PENDIENTE_VALIDACION` a `CERRADA`.

**AC-S04-02 (rechazar).** Dado un reporte propio `PENDIENTE_VALIDACION` con técnico `tecnico1` y solución registrada, cuando el solicitante lo rechaza con “El daño sigue presente”, entonces queda `EN_ATENCION`, conserva `tecnico1` y la solución anterior, y registra quién rechazó, cuándo y por qué.

**AC-S04-03 (motivo de rechazo inválido).** Dado un reporte propio `PENDIENTE_VALIDACION`, cuando el solicitante lo rechaza con un motivo de 9 caracteres, de 301, vacío, formado solo por espacios o de 9 rodeados de espacios, entonces recibe 400 y el reporte sigue `PENDIENTE_VALIDACION` sin eventos nuevos. Con exactamente 10 o exactamente 300 se acepta.

**AC-S04-04 (pertenencia y rol).** Dada la incidencia de `solicitante1` en `PENDIENTE_VALIDACION`, cuando `solicitante2` intenta confirmarla o rechazarla, entonces recibe 404 sin cambios. Cuando lo intenta el coordinador o el técnico asignado, entonces recibe 403 sin cambios. Lo mismo aplica a la reapertura de una incidencia `CERRADA`.

**AC-S04-05 (estados incompatibles).** Dada una incidencia propia en `REGISTRADA`, `ASIGNADA`, `EN_ATENCION` o `CERRADA`, cuando su dueño intenta confirmarla o rechazarla, entonces recibe 409 sin cambios. Dada una incidencia propia en un estado distinto de `CERRADA`, cuando su dueño intenta reabrirla, entonces recibe 409 sin cambios.

**AC-S04-06 (reabrir en el límite).** Dada una incidencia propia `CERRADA` cuyo último cierre ocurrió en `2026-10-01T10:00:00Z` con técnico `tecnico1`, cuando su dueño la reabre con el motivo “La fuga volvió a aparecer” y el reloj del servidor marca `2026-10-03T10:00:00Z` (exactamente 48 horas), entonces queda `EN_ATENCION` con `tecnico1`, se conservan el cierre y la solución anteriores, y el historial suma un evento `REABRIR` con el motivo.

**AC-S04-07 (reabrir fuera de plazo).** Dada la misma incidencia `CERRADA`, cuando su dueño intenta reabrirla y el reloj del servidor marca `2026-10-03T10:00:00.000001Z` (48 horas y un microsegundo), entonces recibe 409 y la incidencia sigue `CERRADA` con el mismo historial.

**AC-S04-08 (motivo de reapertura inválido).** Dada una incidencia propia `CERRADA` dentro del plazo, cuando su dueño la reabre con un motivo de 9 caracteres, de 301, vacío o formado solo por espacios, entonces recibe 400 y sigue `CERRADA` sin eventos nuevos.

**AC-S04-09 (cierres sucesivos).** Dada una incidencia reabierta a la que el técnico registró una solución nueva, cuando su dueño la confirma, entonces queda `CERRADA` con dos cierres y dos soluciones conservados, y el plazo de una nueva reapertura se cuenta desde el segundo cierre.

**AC-S04-10 (hora del servidor).** Dada una incidencia propia `CERRADA` fuera de plazo, cuando su dueño envía la reapertura con un campo de fecha dentro del plazo, entonces el campo se ignora y recibe 409.

**AC-S04-11 (sin efectos parciales).** Dada una incidencia propia `PENDIENTE_VALIDACION` o `CERRADA` dentro del plazo, cuando falla el guardado del evento al confirmar, rechazar o reabrir, entonces la transacción se revierte: el estado no cambia, no queda ningún cierre nuevo y el historial no cambia.

## Diseño y tareas vinculadas a cada AC

Diseño en [plan.md](plan.md); tareas en [tasks.md](tasks.md).

| AC | Tareas |
|---|---|
| AC-S04-01, 09 | T-S04-01, T-S04-02, T-S04-05 |
| AC-S04-02, 03 | T-S04-03, T-S04-05 |
| AC-S04-04, 05 | T-S04-02, T-S04-03, T-S04-04 |
| AC-S04-06, 07, 08, 10 | T-S04-04, T-S04-05 |
| Todos | T-S04-06 |
| AC-S04-11 y motivo solo con espacios | T-S04-07 |

## Pruebas y resultados esperados

El resultado esperado se define aquí, antes de ejecutar, y no se calcula con la función de producción. Salvo que se indique otra cosa, cada prueba parte de una base SQLite nueva y aislada que solo contiene las cinco cuentas del seed, con el reloj del servidor fijado en `2026-10-01T08:00:00Z`. Todas las pruebas de esta tabla existen en el repositorio y se ejecutaron el 2026-10-08 dentro de la batería completa (`python -m pytest`: 176 aprobadas sobre `6b99fec`); el detalle está en `docs/validacion/validacion.md` de la rama `docs/evidencias`.

| ID | AC | Precondición y entrada | Esperado | Prueba automatizada |
|---|---|---|---|---|
| P-S04-01 | AC-S04-01 | Integración: registrar → asignar → iniciar → proponer → confirmar, cada paso con la sesión de su actor | `CERRADA`; técnico `tecnico1`; 1 solución; 1 cierre; 5 eventos en orden `CREAR`, `ASIGNAR`, `INICIAR_ATENCION`, `REGISTRAR_SOLUCION`, `CONFIRMAR_SOLUCION`, con actores `solicitante1`, `coordinador1`, `tecnico1`, `tecnico1`, `solicitante1` | `test_p_s04_01_flujo_de_cierre` |
| P-S04-02 | AC-S04-02, AC-S03-06 | Integración: … → proponer → rechazar «El daño sigue presente» → nueva solución → confirmar | Tras el rechazo: `EN_ATENCION`, `tecnico1`, 1 solución. Al final: `CERRADA`, 2 soluciones en orden, 1 cierre enlazado a la segunda, 7 eventos | `test_p_s04_02_rechazo_y_nueva_solucion` |
| P-S04-03 | AC-S04-06, 07, 09 | Integración: cierre en `2026-10-01T10:00Z` → reapertura a las 48 h exactas → nueva solución → nuevo cierre en `2026-10-03T14:00Z` → reapertura a 48 h + 1 µs del segundo cierre → reapertura a las 48 h exactas del segundo cierre | 302 y `EN_ATENCION` con `tecnico1` y 1 cierre; después `CERRADA` con 2 soluciones, 2 cierres y 8 eventos; después 409 sin cambios; después 302 | `test_p_s04_03_reapertura_y_nuevo_cierre` |
| P-S04-04 | AC-S04-03 | `PENDIENTE_VALIDACION` con 4 eventos; rechazo con motivo de 9, 301, vacío, 9 rodeado de espacios, 10 y 300 caracteres | 9, 301, vacío y con espacios: 400, `PENDIENTE_VALIDACION`, 4 eventos. 10 y 300: 302, `EN_ATENCION` | `test_p_s04_04_limites_del_motivo_de_rechazo` |
| P-S04-05 | AC-S04-04, AC-S03-07 | `PENDIENTE_VALIDACION` de `solicitante1`; confirman y rechazan `solicitante2`, `coordinador1`, `tecnico1` y `tecnico2` | `solicitante2`: 404. Los demás: 403. `PENDIENTE_VALIDACION`; 4 eventos; 0 cierres | `test_p_s04_05_solo_el_duenio_valida` |
| P-S04-06 | AC-S04-01 | `PENDIENTE_VALIDACION`; a las `2026-10-01T10:00Z` el dueño confirma | 302; `CERRADA`; 1 cierre con dueño, fecha y la solución vigente; evento enlazado al cierre | `test_confirmar` |
| P-S04-07 | AC-S04-02 | `PENDIENTE_VALIDACION`; el dueño rechaza con «El daño sigue presente» | 302; `EN_ATENCION`; `tecnico1`; 1 solución intacta; 0 cierres; evento con actor, fecha, motivo y solución rechazada | `test_rechazar_conserva_tecnico_y_solucion` |
| P-S04-08 | AC-S04-04 | `CERRADA` de `solicitante1`; reabren `solicitante2`, `coordinador1` y `tecnico1` | 404; 403; 403. `CERRADA`; 5 eventos | `test_solo_el_duenio_reabre` |
| P-S04-09 | AC-S04-05 | El dueño confirma y rechaza en `REGISTRADA`, `ASIGNADA`, `EN_ATENCION` y `CERRADA` | 409 en los ocho casos; mismo estado y mismo historial | `test_validar_en_estado_incompatible` |
| P-S04-10 | AC-S04-05 | El dueño reabre en `REGISTRADA`, `ASIGNADA`, `EN_ATENCION` y `PENDIENTE_VALIDACION` | 409 en los cuatro casos; mismo estado y mismo historial | `test_reabrir_en_estado_incompatible` |
| P-S04-11 | AC-S04-06 | Último cierre en `2026-10-01T10:00:00Z`; reapertura con el reloj en `2026-10-03T10:00:00Z` | 302; `EN_ATENCION`; `tecnico1`; 1 cierre y 1 solución conservados; evento `REABRIR` con motivo y fecha | `test_reabrir_exactamente_a_las_48_horas` |
| P-S04-12 | AC-S04-07 | Mismo cierre; reapertura con el reloj en `2026-10-03T10:00:00.000001Z` | 409; `CERRADA`; los mismos 5 eventos | `test_reabrir_un_instante_despues_de_48_horas` |
| P-S04-13 | AC-S04-08 | `CERRADA` dentro del plazo; reapertura con motivo de 9, de 301 y vacío | 400; `CERRADA`; 5 eventos | `test_motivo_de_reapertura_invalido` |
| P-S04-14 | AC-S04-10 | `CERRADA` hace 72 h; la reapertura envía campos `fecha` y `ahora` dentro del plazo | 409; `CERRADA` | `test_la_hora_la_decide_el_servidor` |
| P-S04-15 | AC-S04-03, 08 | Rechazo (`PENDIENTE_VALIDACION`, 4 eventos) y reapertura (`CERRADA` dentro del plazo, 5 eventos) con un motivo de 15 espacios, de 300 espacios, y de tabulaciones y saltos de línea | 400; mismo estado y mismo técnico; eventos idénticos fila a fila; sin soluciones ni cierres nuevos | `test_p_s04_15_rechazo_con_motivo_solo_de_espacios`, `test_p_s04_15_reapertura_con_motivo_solo_de_espacios` (commit `6b99fec`, rama `docs/evidencias`) |
| P-S04-16 | AC-S04-11 | Confirmar, rechazar y reabrir mientras se fuerza un fallo al guardar el evento | La operación falla; las cinco tablas quedan idénticas fila a fila (mismo estado, 0 cierres nuevos, mismo historial); sin el fallo, la misma operación se completa | `test_un_fallo_al_guardar_el_evento_revierte_toda_la_operacion`, casos `P-S04-16-confirmar`, `P-S04-16-rechazar` y `P-S04-16-reabrir`, en `tests/test_atomicidad.py` (commit `6b99fec`, rama `docs/evidencias`) |

Las pruebas del plazo usan un reloj controlado inyectado en la aplicación. No se espera tiempo real ni se cambia el reloj del sistema.

## Decisión de revisión / versión aprobada

| Fecha | Versión revisada | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.4 | Cristian David Diaz España (asignado) | Pendiente | |
