# SPEC S01 · Registrar una incidencia

| Campo | Valor |
|---|---|
| Versión | 0.1 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Pendiente: otro integrante del equipo |
| Fecha | 2026-10-08 |
| Requisito asociado | RF01 |

## Historia (H01)

Como **solicitante**, quiero **registrar una incidencia de infraestructura con su ubicación, categoría, descripción, impacto y riesgo para personas**, para **que mantenimiento la conozca por un único canal y quede constancia de mi reporte**.

## Alcance y exclusiones

**Incluye:** formulario de registro, validación en servidor, generación de código, autor, fecha, estado y prioridad, y el evento de creación en el historial.

**Excluye:** adjuntos, edición o eliminación del reporte después de creado, registro en nombre de otra persona y notificaciones. La regla de cálculo de la prioridad se especifica en S02.

## Entradas

| Campo | Tipo | Obligatorio | Valores o límites |
|---|---|---|---|
| `ubicacion` | texto | Sí | Exactamente `LAB-01`, `AULA-201` o `BIB-01`. |
| `categoria` | texto | Sí | Exactamente `ELECTRICIDAD`, `HIDRAULICA`, `MOBILIARIO` o `TIC`. |
| `descripcion` | texto | Sí | De 20 a 500 caracteres después de retirar espacios externos. |
| `impacto` | texto | Sí | Exactamente `BAJO` o `ALTO`. |
| `riesgo_personas` | booleano | Sí | Exactamente `true` o `false`. Ausente se rechaza. |

El cliente no envía código, autor, fecha, estado ni prioridad. Si los envía, el servidor los ignora.

## Precondiciones y permisos

- Sesión iniciada. Sin sesión, el servidor redirige al inicio de sesión y no crea nada.
- Rol `SOLICITANTE`. Coordinador y técnico reciben 403.
- El autor es siempre el usuario de la sesión.

## Reglas y proceso

1. Comprobar sesión y rol.
2. Retirar espacios externos de la descripción.
3. Validar los cinco campos. Si alguno falla, responder 400 con la lista de errores por campo y no guardar nada.
4. Calcular la prioridad con la regla de S02.
5. En una sola transacción: insertar la incidencia con estado `REGISTRADA`, autor y fecha UTC del servidor; generar el código `INC-` más seis dígitos consecutivos; insertar el evento `CREAR`.
6. Confirmar la transacción y redirigir al detalle de la incidencia.

## Salidas y cambios persistidos

- Una fila en `incidencias` con `codigo`, `solicitante_id`, `ubicacion`, `categoria`, `descripcion`, `impacto`, `riesgo_personas`, `prioridad`, `estado = REGISTRADA`, `creada_en`.
- Una fila en `eventos` con `accion = CREAR`, `actor_id` = autor, `estado_anterior` vacío, `estado_nuevo = REGISTRADA` y la misma fecha.
- Respuesta: redirección 302 al detalle, donde se ve el código generado.

## Errores y efectos que deben evitarse

| Situación | Respuesta | Efecto |
|---|---|---|
| Sin sesión | 302 al inicio de sesión | Ninguno |
| Rol distinto de solicitante | 403 | Ninguno |
| Campo ausente, fuera de catálogo o fuera de límites | 400 con mensaje por campo | Ninguno |

No debe ocurrir: una incidencia sin evento de creación o un evento sin incidencia; texto del usuario interpretado como HTML; autor, fecha, estado o prioridad tomados de la petición.

## Criterios de aceptación

**AC-S01-01 (funcionamiento normal).** Dado el solicitante `solicitante1` con sesión iniciada y ninguna incidencia registrada, cuando envía ubicación `LAB-01`, categoría `ELECTRICIDAD`, descripción “El tomacorriente del puesto 4 no tiene energía”, impacto `BAJO` y riesgo `false`, entonces se crea una incidencia con código `INC-000001`, autor `solicitante1`, fecha UTC del servidor, estado `REGISTRADA` y prioridad `NORMAL`, y su historial tiene exactamente un evento `CREAR` de `solicitante1` hacia `REGISTRADA`.

**AC-S01-02 (permisos).** Dado un usuario con rol coordinador o técnico y sesión iniciada, cuando envía un registro con datos válidos, entonces recibe 403 y no se crea incidencia ni evento. Dado un visitante sin sesión, cuando envía el registro, entonces es redirigido al inicio de sesión y no se crea nada.

**AC-S01-03 (límites de la descripción).** Dado un solicitante con sesión iniciada, cuando envía una descripción de 19 caracteres, entonces recibe 400 y no se crea nada; cuando envía una de 20 caracteres, entonces se crea; cuando envía una de 500, entonces se crea; cuando envía una de 501, entonces recibe 400. Los espacios externos no cuentan: 19 caracteres rodeados de espacios se rechazan.

**AC-S01-04 (impacto inválido).** Dado un solicitante con sesión iniciada, cuando envía impacto `MEDIO`, `alto` o vacío, entonces recibe 400 con un error en el campo impacto y no se crea incidencia ni evento.

**AC-S01-05 (riesgo inválido).** Dado un solicitante con sesión iniciada, cuando envía riesgo `quiza` o no envía el campo, entonces recibe 400 con un error en el campo riesgo y no se crea incidencia ni evento.

**AC-S01-06 (catálogos).** Dado un solicitante con sesión iniciada, cuando envía una ubicación o una categoría que no pertenece al catálogo, o no la envía, entonces recibe 400 y no se crea nada.

**AC-S01-07 (texto no ejecutable).** Dado un solicitante con sesión iniciada, cuando registra la descripción `<script>alert(1)</script> la silla está rota`, entonces la descripción se guarda literal y, al mostrar el detalle, la respuesta contiene `&lt;script&gt;` y no contiene la etiqueta `<script>alert(1)</script>`.

**AC-S01-08 (campos generados por el servidor).** Dado un solicitante con sesión iniciada, cuando envía datos válidos junto con `codigo`, `estado=CERRADA`, `prioridad=CRITICA`, `solicitante_id` de otro usuario o una fecha, entonces esos valores se ignoran: el autor es el de la sesión, el estado es `REGISTRADA`, la prioridad es la calculada y la fecha es la del servidor.

**AC-S01-09 (sin efectos parciales).** Dado un fallo al guardar el evento de creación, cuando el servidor procesa el registro, entonces la transacción se revierte y no queda la incidencia.

## Diseño y tareas vinculadas a cada AC

Diseño en [plan.md](plan.md); tareas en [tasks.md](tasks.md).

| AC | Tareas |
|---|---|
| AC-S01-01 | T-S01-01, T-S01-03, T-S01-04, T-S01-05 |
| AC-S01-02 | T-S01-02, T-S01-04 |
| AC-S01-03 a 06 | T-S01-03 |
| AC-S01-07 | T-S01-05 |
| AC-S01-08, 09 | T-S01-04 |
| Todos | T-S01-06 |

## Pruebas y resultados esperados

El resultado esperado se define aquí, antes de ejecutar, y no se calcula con la función de producción.

| ID | AC | Entrada | Esperado |
|---|---|---|---|
| P-S01-01 | AC-S01-01 | Registro válido, `BAJO`, riesgo `false` | 302; 1 incidencia `INC-000001`, `REGISTRADA`, `NORMAL`, autor `solicitante1`; 1 evento `CREAR` |
| P-S01-02 | AC-S01-03 | Descripción de 19 y de 20 caracteres | 19: 400 y 0 incidencias. 20: 302 y 1 incidencia |
| P-S01-03 | AC-S01-04, 05, 06 | Impacto `MEDIO`; riesgo `quiza`; riesgo ausente; ubicación `LAB-99` | 400 en cada caso; 0 incidencias; 0 eventos |
| P-S01-04 | AC-S01-02 | Coordinador y técnico envían un registro válido | 403; 0 incidencias |
| P-S01-05 | AC-S01-07 | Descripción con `<script>` | Guardada literal; el detalle la muestra escapada |
| P-S01-06 | AC-S01-08 | Registro válido con `estado=CERRADA` y `prioridad=CRITICA` | `REGISTRADA`, `NORMAL` |

## Decisión de revisión / versión aprobada

| Fecha | Versión revisada | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.1 | Pendiente | Pendiente | |
