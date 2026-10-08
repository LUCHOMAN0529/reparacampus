# SPEC S04 · Validar la solución: confirmar, rechazar y reabrir

| Campo | Valor |
|---|---|
| Versión | 0.2 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Asignado: Cristian David Diaz España. Revisión pendiente |
| Fecha | 2026-10-08 |
| Requisito asociado | RF04 |

**Cambios de la versión 0.2 (2026-10-08):** se agregan los límites 300 y 301 a la prueba P-S04-04. Origen: [revisión asistida por IA](../../docs/revision/revision-asistida-ia-2026-10-08.md), que no reemplaza la revisión del integrante asignado.

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

**AC-S04-03 (motivo de rechazo inválido).** Dado un reporte propio `PENDIENTE_VALIDACION`, cuando el solicitante lo rechaza con un motivo de 9 caracteres, de 301, vacío o de 9 rodeados de espacios, entonces recibe 400 y el reporte sigue `PENDIENTE_VALIDACION` sin eventos nuevos. Con exactamente 10 o exactamente 300 se acepta.

**AC-S04-04 (pertenencia y rol).** Dada la incidencia de `solicitante1` en `PENDIENTE_VALIDACION`, cuando `solicitante2` intenta confirmarla o rechazarla, entonces recibe 404 sin cambios. Cuando lo intenta el coordinador o el técnico asignado, entonces recibe 403 sin cambios. Lo mismo aplica a la reapertura de una incidencia `CERRADA`.

**AC-S04-05 (estados incompatibles).** Dada una incidencia propia en `REGISTRADA`, `ASIGNADA`, `EN_ATENCION` o `CERRADA`, cuando su dueño intenta confirmarla o rechazarla, entonces recibe 409 sin cambios. Dada una incidencia propia en un estado distinto de `CERRADA`, cuando su dueño intenta reabrirla, entonces recibe 409 sin cambios.

**AC-S04-06 (reabrir en el límite).** Dada una incidencia propia `CERRADA` cuyo último cierre ocurrió en `2026-10-01T10:00:00Z` con técnico `tecnico1`, cuando su dueño la reabre con el motivo “La fuga volvió a aparecer” y el reloj del servidor marca `2026-10-03T10:00:00Z` (exactamente 48 horas), entonces queda `EN_ATENCION` con `tecnico1`, se conservan el cierre y la solución anteriores, y el historial suma un evento `REABRIR` con el motivo.

**AC-S04-07 (reabrir fuera de plazo).** Dada la misma incidencia `CERRADA`, cuando su dueño intenta reabrirla y el reloj del servidor marca `2026-10-03T10:00:00.000001Z` (48 horas y un microsegundo), entonces recibe 409 y la incidencia sigue `CERRADA` con el mismo historial.

**AC-S04-08 (motivo de reapertura inválido).** Dada una incidencia propia `CERRADA` dentro del plazo, cuando su dueño la reabre con un motivo de 9 caracteres, de 301 o vacío, entonces recibe 400 y sigue `CERRADA` sin eventos nuevos.

**AC-S04-09 (cierres sucesivos).** Dada una incidencia reabierta a la que el técnico registró una solución nueva, cuando su dueño la confirma, entonces queda `CERRADA` con dos cierres y dos soluciones conservados, y el plazo de una nueva reapertura se cuenta desde el segundo cierre.

**AC-S04-10 (hora del servidor).** Dada una incidencia propia `CERRADA` fuera de plazo, cuando su dueño envía la reapertura con un campo de fecha dentro del plazo, entonces el campo se ignora y recibe 409.

## Diseño y tareas vinculadas a cada AC

Diseño en [plan.md](plan.md); tareas en [tasks.md](tasks.md).

| AC | Tareas |
|---|---|
| AC-S04-01, 09 | T-S04-01, T-S04-02, T-S04-05 |
| AC-S04-02, 03 | T-S04-03, T-S04-05 |
| AC-S04-04, 05 | T-S04-02, T-S04-03, T-S04-04 |
| AC-S04-06, 07, 08, 10 | T-S04-04, T-S04-05 |
| Todos | T-S04-06 |

## Pruebas y resultados esperados

| ID | AC | Entrada | Esperado |
|---|---|---|---|
| P-S04-01 | AC-S04-01 | Integración: registrar → asignar → iniciar → proponer → confirmar | `CERRADA`; 1 solución; 1 cierre; 5 eventos en orden `CREAR`, `ASIGNAR`, `INICIAR_ATENCION`, `REGISTRAR_SOLUCION`, `CONFIRMAR_SOLUCION` |
| P-S04-02 | AC-S04-02, AC-S03-06 | Integración: … → proponer → rechazar “El daño sigue presente” → nueva solución → confirmar | Tras el rechazo: `EN_ATENCION`, `tecnico1`, 1 solución. Al final: `CERRADA`, 2 soluciones, 1 cierre, 7 eventos |
| P-S04-03 | AC-S04-06, 07, 09 | Integración: cierre en `T` → reapertura en `T + 48 h` → nueva solución → nuevo cierre; y otra incidencia con reapertura en `T + 48 h + 1 µs` | Primera: `CERRADA`, 2 soluciones, 2 cierres, 8 eventos. Segunda: 409, `CERRADA`, 5 eventos |
| P-S04-04 | AC-S04-03 | Rechazo con motivo de 9, 301, 10 y 300 caracteres | 9 y 301: 400, `PENDIENTE_VALIDACION`. 10 y 300: 302, `EN_ATENCION` |
| P-S04-05 | AC-S04-04 | `solicitante2` confirma la incidencia de `solicitante1`; el coordinador la confirma | 404; 403; `PENDIENTE_VALIDACION`; 4 eventos |

Las pruebas del plazo usan un reloj controlado inyectado en la aplicación. No se espera tiempo real ni se cambia el reloj del sistema.

## Decisión de revisión / versión aprobada

| Fecha | Versión revisada | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.2 | Cristian David Diaz España (asignado) | Pendiente | |
