# SPEC S05 · Consultar, historizar y tablero

| Campo | Valor |
|---|---|
| Versión | 0.3 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Asignado: Jorge Luis González Arroyo. Revisión pendiente |
| Fecha | 2026-10-08 |
| Requisito asociado | RF05 |

**Cambios de la versión 0.2 (2026-10-08):** se distingue filtro inválido de filtro válido sin resultados y se aclara quién ve el historial. Origen: [revisión asistida por IA](../../docs/revision/revision-asistida-ia-2026-10-08.md), que no reemplaza la revisión del integrante asignado.

**Cambios de la versión 0.3 (2026-10-08):** se define el orden y el desempate del historial; AC-S05-04 incluye al técnico asignado; la tabla de pruebas refleja las pruebas reales (inmutabilidad en las tres tablas, operaciones rechazadas, cantidades del tablero y redondeo). Origen: [segunda revisión asistida por IA](../../docs/revision/revision-asistida-ia-02-chatgpt.md), que tampoco reemplaza la revisión del integrante asignado.

## Historia (H05)

Como **coordinador, solicitante o técnico**, quiero **consultar las incidencias que me corresponden, con filtros y con su historial completo, y como coordinador ver un tablero de resumen**, para **saber en qué va cada caso y comprobar qué ocurrió sin depender de mensajes sueltos**.

## Alcance y exclusiones

**Incluye:** listado según permisos con filtros por estado y prioridad; detalle con historial; historial inmutable; tablero del coordinador con cantidades por estado y prioridad, críticas no cerradas y porcentaje de cierre.

**Excluye:** edición o borrado del historial, búsqueda por texto, paginación, exportación, gráficos, métricas de tiempos y tablero para otros roles.

## Entradas

| Operación | Campo | Tipo | Obligatorio | Valores o límites |
|---|---|---|---|---|
| Listar | `estado` | texto | No | Vacío, o uno de los cinco estados. |
| Listar | `prioridad` | texto | No | Vacío, o `CRITICA`, `ALTA`, `NORMAL`. |
| Detalle | `codigo` (en la ruta) | texto | Sí | Código de una incidencia visible para el usuario. |
| Tablero | — | — | — | Sin parámetros. |

## Precondiciones y permisos

Todas las consultas exigen sesión iniciada. La visibilidad la decide el servidor con la identidad de la sesión:

| Rol | Listado y detalle | Tablero |
|---|---|---|
| Solicitante | Solo las incidencias que registró. | 403 |
| Técnico | Solo las incidencias que tiene asignadas. | 403 |
| Coordinador | Todas. | Permitido |

Abrir el detalle de una incidencia inexistente o no visible responde 404 (supuesto Q1).

## Reglas y proceso

**Listado.** Aplicar primero la visibilidad por rol y después los filtros. Con ambos filtros, se combinan con “y”. Un filtro vacío no restringe. Un valor fuera del catálogo responde 400. Orden: más recientes primero.

**Historial.** Cada creación y cada transición exitosa agrega un evento con autor, fecha UTC, estado anterior, estado nuevo y acción. Según la acción, el evento enlaza la solución, el cierre o el motivo. El detalle muestra los eventos en el orden en que se registraron, que coincide con el cronológico. Si dos eventos tienen la misma marca de tiempo, el desempate es el identificador consecutivo del evento, que la base asigna al insertarlo. Se muestran con el texto de las soluciones, los motivos de rechazo y reapertura, y los cierres.

Quien puede ver el detalle de una incidencia ve su historial completo: el solicitante dueño, el técnico asignado y el coordinador.

**Inmutabilidad.** No existe ninguna operación para editar o borrar eventos, soluciones o cierres. La base de datos rechaza cualquier `UPDATE` o `DELETE` sobre esas tablas. Una operación rechazada no agrega eventos.

**Tablero.**

- Cantidad por estado, para los cinco estados, incluidos los que están en cero.
- Cantidad por prioridad, para las tres prioridades, incluidas las que están en cero.
- Lista de incidencias con prioridad `CRITICA` cuyo estado actual no es `CERRADA`.
- Porcentaje de cierre = incidencias actualmente `CERRADAS` / total × 100, con un decimal, redondeo aritmético y coma decimal. Con cero incidencias muestra `0,0 %`.

## Salidas y cambios persistidos

Las consultas no modifican datos.

- Listado: código, ubicación, categoría, prioridad, estado, fecha y, según el rol, solicitante y técnico.
- Detalle: datos de la incidencia e historial.
- Tablero: los cuatro bloques anteriores.

## Errores y efectos que deben evitarse

| Situación | Respuesta |
|---|---|
| Sin sesión | 302 al inicio de sesión |
| Filtro con valor fuera del catálogo | 400 |
| Detalle de una incidencia inexistente o no visible | 404 |
| Tablero solicitado por solicitante o técnico | 403 |

No debe ocurrir: que un filtro amplíe la visibilidad; que el listado o el detalle revelen incidencias ajenas; que un evento cambie o desaparezca; que el texto del usuario se interprete como HTML; un porcentaje calculado sobre cierres históricos en lugar del estado actual.

## Criterios de aceptación

**AC-S05-01 (visibilidad del listado).** Dadas dos incidencias de `solicitante1` y una de `solicitante2`, de las cuales una está asignada a `tecnico1`, cuando cada usuario abre el listado, entonces `solicitante1` ve sus dos, `solicitante2` ve la suya, `tecnico1` ve solo la asignada, `tecnico2` no ve ninguna y el coordinador ve las tres.

**AC-S05-02 (filtros).** Dado el coordinador y un conjunto con incidencias en distintos estados y prioridades, cuando filtra por `estado=ASIGNADA`, entonces ve solo las `ASIGNADA`; cuando filtra por `prioridad=CRITICA`, entonces ve solo las `CRITICA`; cuando aplica ambos, entonces ve solo las que cumplen los dos. Dado un solicitante, cuando filtra, entonces el resultado nunca incluye incidencias ajenas.

**AC-S05-03 (filtro inválido).** Dado un usuario con sesión iniciada, cuando lista con `estado=ABIERTA` o `prioridad=URGENTE`, entonces recibe 400. Cuando lista con un valor válido que ninguna incidencia visible cumple, entonces recibe 200 con la lista vacía.

**AC-S05-04 (historial completo).** Dada una incidencia que recorrió registro, asignación, inicio, solución, rechazo, nueva solución, confirmación y reapertura, cuando su dueño, el técnico asignado o el coordinador abre el detalle, entonces el historial muestra ocho eventos en orden cronológico, cada uno con autor, fecha, estado anterior, estado nuevo y acción, e incluye el texto de las dos soluciones, el motivo del rechazo, el cierre y el motivo de la reapertura.

**AC-S05-05 (historial inmutable).** Dado un historial con eventos, cuando se intenta ejecutar `UPDATE` o `DELETE` sobre `eventos`, `soluciones` o `cierres`, entonces la base de datos lo rechaza y los registros no cambian. No existe ninguna ruta de la aplicación para editar o borrar historial.

**AC-S05-06 (operación rechazada sin rastro).** Dada una incidencia con N eventos, cuando se rechaza una operación por permiso, estado, plazo o datos inválidos, entonces la incidencia conserva su estado y sigue teniendo exactamente N eventos.

**AC-S05-07 (tablero vacío).** Dado el coordinador y ninguna incidencia registrada, cuando abre el tablero, entonces ve cero en todos los estados y prioridades, ninguna crítica pendiente y un porcentaje de cierre de `0,0 %`.

**AC-S05-08 (porcentaje de cierre).** Dadas cuatro incidencias de las cuales una está `CERRADA`, cuando el coordinador abre el tablero, entonces el porcentaje de cierre es `25,0 %`. Cuando esa incidencia se reabre, entonces el porcentaje es `0,0 %` y su cierre anterior sigue en el historial.

**AC-S05-09 (cantidades y críticas).** Dadas cuatro incidencias —dos `CRITICA` (una `CERRADA`, una `ASIGNADA`), una `ALTA` `REGISTRADA` y una `NORMAL` `REGISTRADA`—, cuando el coordinador abre el tablero, entonces ve por estado: `REGISTRADA` 2, `ASIGNADA` 1, `EN_ATENCION` 0, `PENDIENTE_VALIDACION` 0, `CERRADA` 1; por prioridad: `CRITICA` 2, `ALTA` 1, `NORMAL` 1; y en críticas no cerradas solo la `ASIGNADA`.

**AC-S05-10 (permiso del tablero).** Dado un solicitante o un técnico con sesión iniciada, cuando abre el tablero, entonces recibe 403.

**AC-S05-11 (detalle ajeno).** Dada una incidencia de `solicitante1`, cuando `solicitante2` abre su detalle, entonces recibe 404. Dada una incidencia asignada a `tecnico1`, cuando `tecnico2` abre su detalle, entonces recibe 404.

**AC-S05-12 (persistencia).** Dadas incidencias y eventos guardados, cuando la aplicación se detiene y vuelve a iniciar sobre el mismo archivo de base de datos, entonces el listado, el detalle y el historial muestran los mismos datos.

**AC-S05-13 (acceso con cuentas).** Dado un visitante sin sesión, cuando abre el listado, un detalle o el tablero, entonces es redirigido al inicio de sesión. Dadas credenciales incorrectas, cuando intenta iniciar sesión, entonces no obtiene sesión.

## Diseño y tareas vinculadas a cada AC

Diseño en [plan.md](plan.md); tareas en [tasks.md](tasks.md).

| AC | Tareas |
|---|---|
| AC-S05-01, 02, 03, 13 | T-S05-01, T-S05-04 |
| AC-S05-04, 11 | T-S05-02, T-S05-04 |
| AC-S05-05, 06 | T-S05-03 |
| AC-S05-07 a 10 | T-S05-05 |
| AC-S05-12 | T-S05-06 |
| Todos | T-S05-06 |

## Pruebas y resultados esperados

El resultado esperado se define aquí, antes de ejecutar, y no se calcula con la función de producción. Salvo que se indique otra cosa, cada prueba parte de una base SQLite nueva y aislada que solo contiene las cinco cuentas del seed, con el reloj del servidor fijado en `2026-10-01T08:00:00Z`. «Por automatizar» significa que la prueba todavía no existe.

| ID | AC | Precondición y entrada | Esperado | Prueba automatizada |
|---|---|---|---|---|
| P-S05-01 | AC-S05-01, 11 | Tres incidencias: `INC-000001` de `solicitante1` `ASIGNADA` a `tecnico1`, `INC-000002` de `solicitante1`, `INC-000003` de `solicitante2`. Cada usuario abre el listado y varios detalles | Listado: `solicitante1` 2, `solicitante2` 1, `tecnico1` 1, `tecnico2` 0, `coordinador1` 3. Detalle propio 200; ajeno o inexistente 404 | `test_p_s05_01_listado_segun_permisos`, `test_p_s05_01_detalle_segun_permisos` |
| P-S05-02 | AC-S05-02, 03 | Cuatro incidencias: 001 `CRITICA` `ASIGNADA`, 002 `CRITICA` `REGISTRADA`, 003 `ALTA` `ASIGNADA`, 004 `NORMAL` `REGISTRADA` de `solicitante2`. Filtros `estado=ASIGNADA`, `prioridad=CRITICA`, ambos, vacíos, `estado=CERRADA`, `estado=ABIERTA`, `prioridad=URGENTE` | 003 y 001; 002 y 001; 001; las cuatro; 200 y lista vacía; 400; 400. Un solicitante o un técnico nunca ve incidencias ajenas al filtrar | `test_p_s05_02_filtros`, `test_p_s05_02_filtro_invalido`, `test_un_filtro_no_amplia_la_visibilidad` |
| P-S05-03 | AC-S05-07, 08 | Tablero sin incidencias; con una `CERRADA` de cuatro; después de reabrirla | `0,0 %` y ceros en todo; `25,0 %`; `0,0 %` con 1 cierre conservado | `test_p_s05_03_tablero_vacio`, `test_p_s05_03_porcentaje_de_cierre_y_reapertura` |
| P-S05-04 | AC-S05-05 | Con una incidencia `CERRADA`, `UPDATE` y `DELETE` directos sobre `eventos`, `soluciones` y `cierres` | La base rechaza las seis operaciones; el contenido de las tres tablas no cambia | `test_p_s05_04_el_historial_es_inmutable` |
| P-S05-05 | AC-S05-12 | Se crea una incidencia `CERRADA`, y una segunda instancia de la aplicación abre el mismo archivo de base de datos | Mismo listado, mismo detalle y los mismos eventos fila a fila; siguen existiendo 5 usuarios | `test_p_s05_05_los_datos_permanecen_al_reiniciar` |
| P-S05-06 | AC-S05-10, 13 | Tablero como `solicitante1` y `tecnico1`; listado, detalle, tablero y formulario sin sesión | 403; 403; 302 al inicio de sesión en los cuatro | `test_p_s05_06_tablero_solo_para_el_coordinador`, `test_p_s05_06_sin_sesion_redirige_al_login` |
| P-S05-07 | AC-S05-04 | Una incidencia recorre registro, asignación, inicio, solución, rechazo, nueva solución, confirmación y reapertura; abren el detalle `solicitante1`, `coordinador1` y `tecnico1` | 8 eventos con acción, estado anterior y nuevo, actor y fecha; los tres ven las dos soluciones, el motivo del rechazo y el de la reapertura, en ese orden | `test_historial_completo` |
| P-S05-08 | AC-S05-06 | `PENDIENTE_VALIDACION` con 4 eventos; siete operaciones no permitidas: asignar y confirmar como coordinador, iniciar como `tecnico1`, solución como `tecnico2`, confirmar como `solicitante2`, rechazo con motivo corto y reapertura | Respuestas 409, 403, 409, 404, 404, 400 y 409; `PENDIENTE_VALIDACION` con `tecnico1`; eventos idénticos fila a fila; 1 solución, 0 cierres, 1 asignación | `test_las_operaciones_rechazadas_no_dejan_rastro` |
| P-S05-09 | AC-S05-09 | Cuatro incidencias: `CRITICA` `CERRADA`, `CRITICA` `ASIGNADA`, `ALTA` `REGISTRADA`, `NORMAL` `REGISTRADA` | Por estado 2, 1, 0, 0, 1; por prioridad 2, 1, 1; críticas no cerradas: solo `INC-000002`; `25,0 %` | `test_tablero_cantidades_y_criticas` |
| P-S05-10 | AC-S05-07, 08 | Porcentaje para 0 de 0, 1 de 4, 1 de 3, 2 de 3, 1 de 16 y 5 de 5 | `0,0 %`; `25,0 %`; `33,3 %`; `66,7 %`; `6,3 %`; `100,0 %` | `test_formato_y_redondeo_del_porcentaje` |
| P-S05-11 | AC-S05-05 | Se listan las rutas de la aplicación | Ninguna acepta `PUT`, `PATCH` o `DELETE`; solo nueve aceptan `POST`: inicio y cierre de sesión, registro y las seis transiciones | `test_no_hay_rutas_para_editar_o_borrar` |
| P-S05-12 | AC-S01-07 | Descripción con `<b onmouseover=alert(1)>`; el coordinador abre el detalle | Se muestra escapada | `test_el_listado_no_ejecuta_html` |

## Decisión de revisión / versión aprobada

| Fecha | Versión revisada | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.3 | Jorge Luis González Arroyo (asignado) | Pendiente | |
