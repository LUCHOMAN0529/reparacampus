# SPEC S01 · Registrar una incidencia

| Campo | Valor |
|---|---|
| Versión | 0.4 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Asignado: Rafael Eduardo May Recuero. Revisión pendiente |
| Fecha | 2026-10-08 |
| Requisito asociado | RF01 |

**Cambios de la versión 0.2 (2026-10-08):** se agregan los límites 500 y 501 a la prueba P-S01-02. Origen: [revisión asistida por IA](../../docs/revision/revision-asistida-ia-2026-10-08.md), que no reemplaza la revisión del integrante asignado.

**Cambios de la versión 0.3 (2026-10-08):** se precisa cómo se interpreta el riesgo enviado por el formulario; nuevo AC-S01-10 (registros simultáneos); la tabla de pruebas refleja las pruebas reales e identifica las que faltan. Origen: [segunda revisión asistida por IA](../../docs/revision/revision-asistida-ia-02-chatgpt.md), que tampoco reemplaza la revisión del integrante asignado.

**Cambios de la versión 0.4 (2026-10-08):** las pruebas P-S01-11 y P-S01-12 ya están automatizadas y se registran con su nombre real; se anota el alcance comprobado de AC-S01-10. No cambia ningún requisito ni criterio.

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
| `riesgo_personas` | booleano | Sí | El formulario envía el texto `true` (Sí) o `false` (No). Cualquier otro valor se rechaza: `True`, `1`, `on`, `si`, vacío o campo ausente. No hay valor por defecto. |

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

**AC-S01-10 (registros simultáneos).** Dadas varias solicitudes de registro válidas enviadas al mismo tiempo, cuando el servidor las procesa, entonces todas se crean, cada una con un código distinto y consecutivo y con su propio evento `CREAR`; nunca hay dos incidencias con el mismo código ni una incidencia sin evento. Alcance comprobado: ocho solicitudes simultáneas en un mismo proceso contra SQLite (ver SUP-14); no se ha probado con más carga.

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
| AC-S01-10 | T-S01-07 |

## Pruebas y resultados esperados

El resultado esperado se define aquí, antes de ejecutar, y no se calcula con la función de producción. Salvo que se indique otra cosa, cada prueba parte de una base SQLite nueva y aislada que solo contiene las cinco cuentas del seed, con el reloj del servidor fijado en `2026-10-01T08:00:00Z`. Todas las pruebas de esta tabla existen en el repositorio y se ejecutaron el 2026-10-08 dentro de la batería completa (`python -m pytest`: 176 aprobadas sobre `6b99fec`); el detalle está en `docs/validacion/validacion.md` de la rama `docs/evidencias`.

| ID | AC | Precondición y entrada | Esperado | Prueba automatizada |
|---|---|---|---|---|
| P-S01-01 | AC-S01-01 | `solicitante1` registra `LAB-01`, `ELECTRICIDAD`, la descripción del criterio, `BAJO`, riesgo `false` | 302 al detalle; 1 incidencia `INC-000001`, `REGISTRADA`, `NORMAL`, autor `solicitante1`, fecha `2026-10-01T08:00:00Z`; 1 evento `CREAR` | `test_p_s01_01_registro_valido` |
| P-S01-02 | AC-S01-03 | Descripción de 19, 20, 500 y 501 caracteres, en ese orden | 19: 400 y 0 incidencias. 20: 302. 500: 302. 501: 400. Al final, 2 incidencias y 2 eventos | `test_p_s01_02_limites_de_la_descripcion` |
| P-S01-03 | AC-S01-04, 05, 06 | Diez registros con un único campo inválido: impacto `MEDIO`, `alto` o vacío; riesgo `quiza` o ausente; ubicación `LAB-99` o ausente; categoría `JARDINERIA` o ausente; descripción ausente | 400 en cada caso; 0 incidencias; 0 eventos | `test_p_s01_03_valores_invalidos` |
| P-S01-04 | AC-S01-02 | `coordinador1` y `tecnico1` envían un registro válido | 403; 0 incidencias; 0 eventos | `test_p_s01_04_otros_roles_no_registran` |
| P-S01-05 | AC-S01-07 | Descripción `<script>alert(1)</script> la silla está rota` | Guardada literal; el detalle contiene `&lt;script&gt;` y no la etiqueta | `test_p_s01_05_el_texto_no_se_ejecuta_como_html` |
| P-S01-06 | AC-S01-08 | Registro válido de `solicitante1` que además envía `codigo=INC-777777`, `estado=CERRADA`, `prioridad=CRITICA`, `solicitante_id` de `solicitante2` y `creada_en=2020-01-01…` | Se crea `INC-000001`, `REGISTRADA`, `NORMAL`, autor `solicitante1`, fecha del servidor; no existe `INC-777777` | `test_p_s01_06_el_servidor_ignora_campos_generados` |
| P-S01-07 | AC-S01-02 | Visitante sin sesión envía un registro válido | 302 al inicio de sesión; 0 incidencias | `test_sin_sesion_no_registra` |
| P-S01-08 | AC-S01-03 | Descripción de 19 caracteres rodeada de espacios; de 20 rodeada de espacios y salto de línea | 400; 302 y se guarda sin los espacios externos | `test_los_espacios_externos_no_cuentan` |
| P-S01-09 | AC-S01-09 | Registro válido mientras se fuerza un fallo al guardar el evento | La operación falla; 0 incidencias; 0 eventos | `test_sin_efectos_parciales_si_falla_el_evento` |
| P-S01-10 | AC-S01-01 | Dos registros seguidos, de `solicitante1` y de `solicitante2` | `INC-000001` y `INC-000002`, cada uno con su autor | `test_los_codigos_son_consecutivos` |
| P-S01-11 | AC-S01-10 | Ocho registros válidos enviados a la vez desde ocho hilos de un mismo proceso, cada uno con su sesión; cinco repeticiones | 8 respuestas 302; códigos `INC-000001` a `INC-000008` sin repetir; cada incidencia con su autor, su descripción y un evento `CREAR` | `test_p_s01_11_registros_simultaneos` en `tests/test_concurrencia.py` (commit `6b99fec`, rama `docs/evidencias`) |
| P-S01-12 | AC-S01-05 | Riesgo `True`, `1`, `on`, `TRUE`, `si` y ` true` (con espacio inicial) | 400 en cada caso; 0 incidencias; 0 eventos | `test_p_s01_12_el_riesgo_solo_acepta_true_o_false` (commit `6b99fec`, rama `docs/evidencias`) |

## Decisión de revisión / versión aprobada

| Fecha | Versión revisada | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.4 | Rafael Eduardo May Recuero (asignado) | Pendiente | |
