# Validación: SPEC frente a código

| Campo | Valor |
|---|---|
| Versión del código | commit `de49d68` (rama `docs/evidencias`) |
| SPECS | S01 a S05, versión 0.2 |
| Fecha de ejecución | 2026-10-08 |
| Comando | `python -m pytest` |
| Resultado | **153 pruebas aprobadas, 0 fallidas**, en 33,3 s |
| Entorno | Windows 11, Python 3.14.3, Flask 3.1.3, SQLite 3.50.4, pytest 9.1.1 |
| Datos | Cada prueba crea un archivo SQLite temporal con las cinco cuentas del seed y un reloj controlado que inicia en `2026-10-01T08:00:00Z` |

El SHA y el resultado se volverán a registrar sobre el tag `release-examen` cuando se integren los pull requests.

## 1. Matriz de trazabilidad

| Requisito | Historia | SPEC | Criterios | Tareas | Código principal | Commit | Archivo de pruebas | Pruebas |
|---|---|---|---|---|---|---|---|---|
| RF01 Registrar | H01 | S01 v0.2 | AC-S01-01 a 09 | T-S01-01 a 06 | `dominio.validar_registro`, `servicios.registrar_incidencia`, `rutas.nueva` | `7bc08f2` | `tests/test_s01_registro.py` | 20 |
| RF02 Priorizar y asignar | H02 | S02 v0.2 | AC-S02-01 a 09 | T-S02-01 a 05 | `dominio.calcular_prioridad`, `servicios.asignar` | `8479352` | `tests/test_s02_prioridad_asignacion.py` | 21 |
| RF03 Atender | H03 | S03 v0.2 | AC-S03-01 a 08 | T-S03-01 a 05 | `servicios.iniciar_atencion`, `servicios.registrar_solucion` | `20ebd53` | `tests/test_s03_atencion.py` | 19 |
| RF04 Validar | H04 | S04 v0.2 | AC-S04-01 a 10 | T-S04-01 a 06 | `servicios.confirmar`, `rechazar`, `reabrir`; `dominio.dentro_de_plazo_reapertura` | `70468c0` | `tests/test_s04_validacion.py`, `tests/test_integracion.py` | 37 + 3 |
| RF05 Consultar e historizar | H05 | S05 v0.2 | AC-S05-01 a 13 | T-S05-01 a 06 | `consultas.listar`, `historial`, `tablero`; disparadores de `schema.sql` | `786cf42` | `tests/test_s05_consulta_tablero.py` | 46 |
| Autenticación (límites del prototipo) | — | Alcance | AC-S05-13 | T-S01-01, 02 | `auth.py`, `db.py` | `c5e7ef7` | `tests/test_auth.py` | 7 |

Esquema, transiciones y errores compartidos: commit `c5e7ef7`. Estados faltantes de AC-S02-06 y AC-S03-04: commit `de49d68`.

## 2. Diez escenarios automatizados de referencia

Los esperados se escribieron en las SPECS antes de ejecutar y aparecen como literales en las pruebas; ninguno se calcula con la función de producción. Todos se ejecutaron con `python -m pytest` el 2026-10-08 sobre `de49d68`.

| ID | SPEC / AC | Tipo | Entrada | Esperado | Observado |
|---|---|---|---|---|---|
| P-S01-01 | S01 / AC-S01-01 | Funcional | `solicitante1` registra `LAB-01`, `ELECTRICIDAD`, `BAJO`, riesgo `false` | 302; `INC-000001`, `REGISTRADA`, `NORMAL`; 1 evento `CREAR` | Igual al esperado |
| P-S01-02 | S01 / AC-S01-03 | Límites | Descripción de 19, 20, 500 y 501 caracteres | 400, 302, 302, 400; 2 incidencias | Igual al esperado |
| P-S02-01 | S02 / AC-S02-01 a 03 | Regla | (riesgo, impacto): (sí, BAJO), (sí, ALTO), (no, ALTO), (no, BAJO) | `CRITICA`, `CRITICA`, `ALTA`, `NORMAL` | Igual al esperado |
| P-S02-03 | S02 / AC-S02-06 | Estado | Segunda asignación a `tecnico2` | 409; técnico `tecnico1`; 1 asignación; 2 eventos | Igual al esperado |
| P-S03-03 | S03 / AC-S03-03 | Permisos | `tecnico2` inicia o soluciona la incidencia de `tecnico1` | 404; sin cambios | Igual al esperado |
| P-S03-04 | S03 / AC-S03-04 | Estado | Solución con la incidencia en `ASIGNADA` | 409; 0 soluciones; 2 eventos | Igual al esperado |
| P-S04-01 | S04 / AC-S04-01 | **Integración** | Registrar → asignar → iniciar → proponer → confirmar | `CERRADA`; 1 solución; 1 cierre; 5 eventos en orden | Igual al esperado |
| P-S04-02 | S04 / AC-S04-02, AC-S03-06 | **Integración** | … → proponer → rechazar “El daño sigue presente” → nueva solución → confirmar | Tras el rechazo: `EN_ATENCION`, `tecnico1`, 1 solución. Final: `CERRADA`, 2 soluciones, 1 cierre, 7 eventos | Igual al esperado |
| P-S04-03 | S04 / AC-S04-06, 07, 09 | **Integración** | Cierre en `2026-10-01T10:00Z` → reapertura a las 48 h exactas → nueva solución → nuevo cierre → reapertura a 48 h + 1 µs del segundo cierre | 302; `CERRADA` con 2 soluciones y 2 cierres, 8 eventos; después 409 sin cambios | Igual al esperado |
| P-S05-03 | S05 / AC-S05-07, 08 | Tablero | Sin incidencias; una cerrada de cuatro; tras reabrirla | `0,0 %`; `25,0 %`; `0,0 %` con 1 cierre conservado | Igual al esperado |

Las tres de integración se ejecutan solas con `python -m pytest -m integracion`: recorren el flujo por HTTP, cada paso con la sesión del actor que corresponde, contra un archivo SQLite real, y comprueban los efectos con una conexión independiente.

## 3. Matriz SPEC frente a código

Estado de cada criterio de aceptación sobre `de49d68`. “Observado” resume el resultado de la prueba y los efectos en la base.

### S01 · Registrar (RF01, H01) — `app/dominio.py`, `app/servicios.py`, `app/rutas.py`

| Criterio | Comportamiento esperado | Prueba | Observado y efectos en la base | Estado |
|---|---|---|---|---|
| AC-S01-01 | Registro válido crea incidencia `REGISTRADA` con código, autor y fecha, y un evento `CREAR` | `test_p_s01_01_registro_valido` | 302; 1 fila en `incidencias`, 1 en `eventos`; fecha del reloj del servidor | Cumple |
| AC-S01-02 | Otros roles 403; sin sesión, redirección; nada se crea | `test_p_s01_04_otros_roles_no_registran`, `test_sin_sesion_no_registra` | 403 y 302; 0 filas | Cumple |
| AC-S01-03 | Descripción de 20 a 500 tras retirar espacios | `test_p_s01_02_limites_de_la_descripcion`, `test_los_espacios_externos_no_cuentan` | 19 y 501: 400; 20 y 500: 302; se guarda recortada | Cumple |
| AC-S01-04 | Impacto inválido se rechaza | `test_p_s01_03_valores_invalidos` (`MEDIO`, `alto`, vacío) | 400; 0 filas | Cumple |
| AC-S01-05 | Riesgo inválido o ausente se rechaza | `test_p_s01_03_valores_invalidos` (`quiza`, ausente) | 400; 0 filas | Cumple |
| AC-S01-06 | Ubicación o categoría fuera de catálogo se rechaza | `test_p_s01_03_valores_invalidos` | 400; 0 filas | Cumple |
| AC-S01-07 | El texto no se ejecuta como HTML | `test_p_s01_05_el_texto_no_se_ejecuta_como_html`, `test_el_listado_no_ejecuta_html` | Guardado literal; la página lo muestra escapado | Cumple |
| AC-S01-08 | El servidor ignora código, estado, prioridad, autor y fecha enviados | `test_p_s01_06_el_servidor_ignora_campos_generados` | `REGISTRADA`, `NORMAL`, autor de la sesión | Cumple |
| AC-S01-09 | Si falla el evento no queda la incidencia | `test_sin_efectos_parciales_si_falla_el_evento` | 0 incidencias, 0 eventos | Cumple |

### S02 · Priorizar y asignar (RF02, H02) — `app/dominio.py`, `app/servicios.py`

| Criterio | Comportamiento esperado | Prueba | Observado y efectos en la base | Estado |
|---|---|---|---|---|
| AC-S02-01 a 03 | Tabla de prioridad | `test_p_s02_01_prioridad_calculada` | `CRITICA`, `CRITICA`, `ALTA`, `NORMAL` | Cumple |
| AC-S02-04 | El coordinador asigna una `REGISTRADA` a un técnico activo | `test_p_s02_02_asignacion_correcta` | `ASIGNADA`; 1 fila en `asignaciones`; evento `ASIGNAR` | Cumple |
| AC-S02-05 | Solicitante y técnico no asignan | `test_p_s02_04_otros_roles_no_asignan` | 403; sigue `REGISTRADA` sin técnico | Cumple |
| AC-S02-06 | Asignación repetida o en otro estado: 409 sin cambios | `test_p_s02_03_asignacion_repetida`, `test_no_se_asigna_fuera_de_registrada`, `test_la_base_impide_una_segunda_asignacion` | 409 en los cuatro estados; conserva `tecnico1`; la base rechaza un segundo registro | Cumple (tras el hallazgo H-03) |
| AC-S02-07 | Técnico ausente, inexistente, inactivo o no técnico: 400 | `test_p_s02_05_tecnico_invalido` | 400; 0 asignaciones | Cumple |
| AC-S02-08 | Incidencia inexistente: 404 | `test_incidencia_inexistente` | 404 | Cumple |
| AC-S02-09 | La prioridad no se manipula | `test_la_prioridad_no_se_cambia_al_asignar`, `test_p_s01_06_…` | Prioridad calculada | Cumple |

### S03 · Atender (RF03, H03) — `app/servicios.py`

| Criterio | Comportamiento esperado | Prueba | Observado y efectos en la base | Estado |
|---|---|---|---|---|
| AC-S03-01 | El técnico asignado inicia la atención | `test_p_s03_01_iniciar_atencion` | `EN_ATENCION`; evento con actor y fecha | Cumple |
| AC-S03-02 | Registra solución y pasa a validación | `test_p_s03_02_registrar_solucion` | `PENDIENTE_VALIDACION`; 1 solución enlazada al evento | Cumple |
| AC-S03-03 | Técnico no asignado 404; otros roles 403 | `test_p_s03_03_tecnico_no_asignado`, `test_otros_roles_no_atienden` | Sin cambios de estado ni eventos | Cumple |
| AC-S03-04 | Estados incompatibles: 409 | `test_p_s03_04_solucion_antes_de_iniciar`, `test_iniciar_en_estado_incompatible`, `test_segunda_solucion_sin_rechazo_se_rechaza` | 409; sin soluciones nuevas | Cumple (tras el hallazgo H-03) |
| AC-S03-05 | Solución de 20 a 800 | `test_p_s03_05_limites_de_la_solucion` | 19, 801 y vacía: 400; 20 y 800: 302 | Cumple |
| AC-S03-06 | Una nueva solución conserva las anteriores | `test_p_s04_02_…`, `test_p_s04_03_…` | 2 filas en `soluciones`, la primera intacta | Cumple |
| AC-S03-07 | El técnico no cierra | `test_p_s04_05_solo_el_duenio_valida` (`tecnico1`, `tecnico2`) | 403; 0 cierres | Cumple; probado en `PENDIENTE_VALIDACION`, que es el único estado desde el que existe el cierre |
| AC-S03-08 | La solución no se ejecuta como HTML | `test_la_solucion_no_se_ejecuta_como_html` | Escapada en el detalle | Cumple |

### S04 · Validar (RF04, H04) — `app/servicios.py`, `app/dominio.py`, `app/reloj.py`

| Criterio | Comportamiento esperado | Prueba | Observado y efectos en la base | Estado |
|---|---|---|---|---|
| AC-S04-01 | El dueño confirma y queda `CERRADA` | `test_confirmar`, `test_p_s04_01_flujo_de_cierre` | 1 fila en `cierres` con solución, dueño y fecha | Cumple |
| AC-S04-02 | Rechazo conserva técnico y solución y registra quién, cuándo y por qué | `test_rechazar_conserva_tecnico_y_solucion`, `test_p_s04_02_…` | `EN_ATENCION`, `tecnico1`, solución intacta, evento con motivo | Cumple |
| AC-S04-03 | Motivo de rechazo de 10 a 300 | `test_p_s04_04_limites_del_motivo_de_rechazo` | 9, 301 y vacío: 400; 10 y 300: 302 | Cumple |
| AC-S04-04 | Otro solicitante 404; coordinador y técnico 403 | `test_p_s04_05_solo_el_duenio_valida`, `test_solo_el_duenio_reabre` | Sin cambios; 0 cierres nuevos | Cumple |
| AC-S04-05 | Estados incompatibles: 409 | `test_validar_en_estado_incompatible`, `test_reabrir_en_estado_incompatible` | 409 en los ocho y cuatro casos | Cumple |
| AC-S04-06 | Reapertura a las 48 h exactas | `test_reabrir_exactamente_a_las_48_horas` | 302; `EN_ATENCION`; cierre y solución conservados | Cumple |
| AC-S04-07 | Reapertura a 48 h + 1 µs se rechaza | `test_reabrir_un_instante_despues_de_48_horas` | 409; mismo historial de 5 eventos | Cumple |
| AC-S04-08 | Motivo de reapertura inválido | `test_motivo_de_reapertura_invalido` | 400; sigue `CERRADA` | Cumple |
| AC-S04-09 | Cierres sucesivos; el plazo cuenta desde el último | `test_p_s04_03_reapertura_y_nuevo_cierre` | 2 cierres; 409 a 48 h + 1 µs del segundo; 302 a las 48 h | Cumple |
| AC-S04-10 | La hora la decide el servidor | `test_la_hora_la_decide_el_servidor` | 409 aunque el formulario envíe una fecha dentro del plazo | Cumple |

### S05 · Consultar, historizar y tablero (RF05, H05) — `app/consultas.py`, `app/schema.sql`

| Criterio | Comportamiento esperado | Prueba | Observado y efectos en la base | Estado |
|---|---|---|---|---|
| AC-S05-01 | Listado según rol | `test_p_s05_01_listado_segun_permisos` | 2, 1, 1, 0 y 3 incidencias | Cumple |
| AC-S05-02 | Filtros por estado y prioridad, sin ampliar la visibilidad | `test_p_s05_02_filtros`, `test_un_filtro_no_amplia_la_visibilidad` | Solo coincidencias visibles | Cumple |
| AC-S05-03 | Filtro inválido 400; válido sin resultados 200 | `test_p_s05_02_filtro_invalido`, `test_p_s05_02_filtros` | 400; lista vacía | Cumple |
| AC-S05-04 | Historial completo y ordenado | `test_historial_completo` | 8 eventos con actor, fecha, estados y acción; soluciones y motivos visibles en orden | Cumple |
| AC-S05-05 | Historial inmutable | `test_p_s05_04_el_historial_es_inmutable`, `test_no_hay_rutas_para_editar_o_borrar` | `UPDATE` y `DELETE` abortan en las tres tablas; mismo contenido | Cumple |
| AC-S05-06 | Una operación rechazada no deja rastro | `test_las_operaciones_rechazadas_no_dejan_rastro` | 7 rechazos (403, 404, 409, 400); eventos idénticos fila a fila | Cumple |
| AC-S05-07 | Tablero vacío: ceros y `0,0 %` | `test_p_s05_03_tablero_vacio` | Igual | Cumple |
| AC-S05-08 | 1 de 4 = `25,0 %`; reabrir baja y conserva el cierre | `test_p_s05_03_porcentaje_de_cierre_y_reapertura`, `test_formato_y_redondeo_del_porcentaje` | `25,0 %` → `0,0 %`; 1 cierre | Cumple |
| AC-S05-09 | Cantidades y críticas no cerradas | `test_tablero_cantidades_y_criticas` | Estados 2, 1, 0, 0, 1; prioridades 2, 1, 1; solo `INC-000002` | Cumple |
| AC-S05-10 | Tablero solo para el coordinador | `test_p_s05_06_tablero_solo_para_el_coordinador` | 403 | Cumple |
| AC-S05-11 | Detalle ajeno: 404 | `test_p_s05_01_detalle_segun_permisos` | 404 en los cuatro casos ajenos | Cumple |
| AC-S05-12 | Los datos permanecen al reiniciar | `test_p_s05_05_los_datos_permanecen_al_reiniciar` | Segunda instancia sobre el mismo archivo muestra los mismos datos | Cumple; el reinicio se simula creando otra instancia de la aplicación |
| AC-S05-13 | Sin sesión, redirección; credenciales incorrectas, sin acceso | `test_p_s05_06_sin_sesion_redirige_al_login`, `tests/test_auth.py` | 302 y 401 | Cumple |

**Resumen:** 49 criterios, 49 en “Cumple”. Ninguno en “Parcial” o “No cumple” sobre `de49d68`.

## 4. Comprobación manual

| Fecha | Qué se hizo | Resultado |
|---|---|---|
| 2026-10-08 | Con el servidor en `localhost:5057`, `solicitante1` inició sesión y registró una incidencia con impacto `ALTO`, riesgo Sí y la descripción `Prueba de humo: <b>chispas</b> …` | Se creó `INC-000001` con prioridad `CRITICA`; la descripción se mostró como texto, sin negrita; el contador de caracteres funcionó; sin errores en la consola |
| 2026-10-08 | Copia limpia: `git clone`, entorno virtual, `pip install -r requirements.txt`, `python -m pytest`, `flask --app app init-db` | Las pruebas pasaron y la base se creó, siguiendo solo el README |

Pendiente de comprobación manual: el recorrido completo en navegador con los cinco usuarios (asignar, atender, rechazar, reabrir y tablero). Está cubierto por las pruebas automatizadas, pero nadie lo ha recorrido a mano.

## 5. Hallazgos y regresión

| ID | Diferencia detectada | Cómo se detectó | Corrección | Regresión |
|---|---|---|---|---|
| H-01 | La SPEC S03 v0.1 decía que la solución de ejemplo tenía 49 caracteres; tiene 50 | Recuento al revisar la tabla de pruebas, antes de versionar | Se quitó la cifra de P-S03-02 | Commit `50fb915`; no afectaba código |
| H-02 | P-S01-02 y P-S04-04 no probaban los límites superiores (500/501 y 300/301) que sus criterios sí exigían | Revisión asistida por IA de las SPECS v0.1 | SPECS v0.2 y casos agregados | Commit `a06aaf2`; pruebas en `7bc08f2` y `70468c0` |
| H-03 | AC-S02-06 exige 409 al asignar en cualquier estado distinto de `REGISTRADA`, pero solo se probaba en `ASIGNADA`; AC-S03-04 no se probaba en `CERRADA` | Al llenar esta matriz criterio por criterio | Cinco casos nuevos | Commit `de49d68`; 153 pruebas aprobadas. El código ya se comportaba bien: faltaba la prueba |
| H-04 | Un comando de edición dañó las tildes de `app/servicios.py` (codificación) durante la implementación de S02 | Lectura del archivo tras el cambio | Se restauró desde Git y se rehízo la edición | 45 pruebas aprobadas antes del commit `8479352`; el archivo dañado nunca se versionó |

## 6. ¿Las pruebas detectan errores?

Las pruebas y el código se generaron con el mismo asistente, así que podrían compartir un mismo error. Para comprobarlo se introdujo **un error a la vez** en una copia del código y se ejecutó la batería completa. Una mutación que no hace fallar ninguna prueba indicaría una prueba complaciente.

Ejecución: 2026-10-08, sobre `de49d68`, 153 pruebas por mutación.

| ID | Error introducido | Pruebas que fallan | Dónde |
|---|---|---|---|
| M1 | Plazo de reapertura exclusivo (`<` en lugar de `<=`) | 2 | Integración, S04 |
| M2 | Prioridad invertida cuando no hay riesgo | 7 | S01, S02, S05 |
| M3 | El solicitante ve todas las incidencias | 9 | S04, S05 |
| M4 | No se comprueba el rol de la operación | 14 | S02, S03, S04, S05 |
| M5 | Los límites de texto cuentan los espacios externos | 3 | S01, S03, S04 |
| M6 | El porcentaje se trunca en lugar de redondear | 2 | S05 |
| M7 | El rechazo no guarda el motivo | 3 | Integración, S04, S05 |
| M8 | El técnico puede cerrar una incidencia | 31 | Integración, S02, S03, S04, S05 |

**Resultado:** las ocho mutaciones fueron detectadas. Es una muestra de ocho errores, no una prueba de mutación exhaustiva.
