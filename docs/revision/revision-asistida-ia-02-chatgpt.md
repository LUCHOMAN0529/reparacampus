# Segunda revisión asistida por IA de las SPECS (v0.2)

| Campo | Valor |
|---|---|
| Fecha | 2026-10-08 |
| Quién la pidió | Luis Carlo Daza Ospino, autor de las SPECS |
| Herramienta de la revisión | ChatGPT, en una conversación de Luis (según él informó) |
| Qué se revisó | SPECS S01 a S05 v0.2, de forma documental |
| Contraste | Claude Code (Claude Opus 5.5) contrastó cada observación con las SPECS, el código y las pruebas, sin modificar nada, y ejecutó `python -m pytest`: 153 aprobadas |
| Versión resultante | SPECS, planes, tareas y diseño v0.3 |

## Qué es y qué no es

Es una revisión hecha con asistentes de IA a petición del autor. **No es la revisión de otro integrante** que exige el examen: esa sigue pendiente en cada SPEC y en el pull request #2, que al momento de este registro no tenía ninguna revisión ni comentario. El 2026-10-08 el autor integró esa rama en `main` sin que llegara ninguna.

Las 24 observaciones llegaron como hipótesis de una lectura documental. Ninguna resultó ser un defecto del código; siete señalan vacíos reales en las SPECS o en las pruebas.

## Decisión humana registrada

Luis autorizó trabajar por etapas: primero las correcciones documentales (este cambio), después las pruebas que faltan y por último las evidencias. Indicó no integrar pull requests, no crear el tag, no generar el PDF final, no marcar revisiones humanas como hechas y dejar el token CSRF como mejora opcional.

## Observaciones y resultado del contraste

| N.º | SPEC | Observación | Resultado | Evidencia | Acción |
|---|---|---|---|---|---|
| 1 | S01 | Precisar cómo se interpretan los booleanos del formulario | Cubierta, mejorable | El dominio solo acepta `true` y `false`; lo demás se rechaza | SPEC v0.3 lo dice de forma explícita; prueba P-S01-12 por automatizar |
| 2 | S01 | Las pruebas con `INC-000001` deben usar una base aislada | Cubierta | Cada prueba crea su propio archivo SQLite temporal | Se escribió la precondición en la tabla de pruebas |
| 3 | S01 | Generación de códigos segura ante solicitudes concurrentes | **Vacío real** | El diseño usa `BEGIN IMMEDIATE` y unicidad, pero no hay prueba | AC-S01-10, SUP-14 y P-S01-11 por automatizar |
| 4 | S01 | Especificar mejor la prueba de campos generados por el servidor | Prueba existe; tabla imprecisa | `test_p_s01_06_el_servidor_ignora_campos_generados` envía cinco campos; la tabla nombraba dos | P-S01-06 corregida |
| 5 | S01 | Coherencia de la prioridad con S02 | Cubierta | `test_p_s01_01_registro_valido` y `test_p_s02_01_prioridad_calculada` | Ninguna |
| 6 | S02 | Pruebas de asignación en estados incompatibles y reasignación | Cubierta | `test_p_s02_03_asignacion_repetida`, `test_no_se_asigna_fuera_de_registrada` (commit `de49d68`) | P-S02-06 agregada a la tabla |
| 7 | S02 | Prueba explícita de que el cliente no manipula la prioridad | Prueba existe; sin identificador | `test_la_prioridad_no_se_cambia_al_asignar` | P-S02-08 agregada |
| 8 | S02 | Comportamiento de 404 y 409 | Cubierta | `test_incidencia_inexistente`, `test_p_s02_03_asignacion_repetida` | Se aclaró que el rol se comprueba antes que la existencia |
| 9 | S02 | Unicidad de la asignación también en la base | Cubierta | `UNIQUE (incidencia_id)` y disparadores; `test_la_base_impide_una_segunda_asignacion` | P-S02-09 agregada |
| 10 | S03 | Precondiciones de las pruebas que esperan cantidades de eventos | **Vacío real** (documental) | La tabla daba el conteo final sin el estado de partida | Tabla de pruebas con precondición |
| 11 | S03 | Una solución rechazada no elimina las anteriores | Cubierta | `test_p_s04_02_rechazo_y_nueva_solucion`; disparadores sobre `soluciones` | P-S03-10 la referencia |
| 12 | S03 | Coherencia con el rechazo y la reapertura de S04 | Cubierta | Pruebas de integración | Ninguna |
| 13 | S03 | El técnico no cierra ni se salta la validación | Cubierta | `test_p_s04_05_solo_el_duenio_valida`; mutación M8: 31 pruebas fallan | P-S03-11 la referencia |
| 14 | S04 | Pruebas de motivo vacío en rechazo y reapertura | Cubierta en parte | Vacío sí se prueba en ambos; solo espacios, no | **Vacío real**: P-S04-15 por automatizar |
| 15 | S04 | Definir la solución vigente | **Vacío real** | El código toma la última; la SPEC no lo decía | Definición en S04 y SUP-12 |
| 16 | S04 | Transiciones inválidas de confirmar, rechazar y reabrir | Cubierta | `test_validar_en_estado_incompatible`, `test_reabrir_en_estado_incompatible` | P-S04-09 y 10 agregadas |
| 17 | S04 | Atomicidad de estado, cierres y eventos | **Vacío real** | Solo el registro tiene una prueba que fuerza un fallo | AC-S02-10, AC-S03-09 y AC-S04-11; pruebas por automatizar |
| 18 | S05 | P-S05-04 debe cubrir `eventos`, `soluciones` y `cierres` | Prueba existe; tabla imprecisa | `test_p_s05_04_el_historial_es_inmutable` ya cubre las tres | P-S05-04 corregida |
| 19 | S05 | Prueba explícita de AC-S05-06 | Prueba existe; sin identificador | `test_las_operaciones_rechazadas_no_dejan_rastro` | P-S05-08 agregada |
| 20 | S05 | Prueba verificable de AC-S05-09 | Prueba existe; sin identificador | `test_tablero_cantidades_y_criticas` | P-S05-09 agregada |
| 21 | S05 | Precisar el conteo de eventos de AC-S05-04 | Cubierta | El criterio ya dice ocho eventos y los enumera | P-S05-07 agregada |
| 22 | S05 | Criterio de desempate para eventos con la misma fecha | **Vacío real** | El código ordena por identificador; la SPEC no lo decía | Regla en S05 y SUP-13 |
| 23 | S05 | Caso de redondeo del porcentaje | Prueba existe; sin identificador | `test_formato_y_redondeo_del_porcentaje` | P-S05-10 agregada |
| 24 | S05 | Visibilidad del historial para el técnico asignado | **Vacío real** (documental) | La prueba lo cubría; el criterio no lo nombraba | AC-S05-04 corregido |

**Resumen:** 11 cubiertas, 6 con prueba existente pero mal reflejada en la SPEC y 7 vacíos reales. En el diagnóstico inicial el asistente escribió “27 observaciones, 17 cubiertas y 10 vacíos”; el recuento correcto es este.

## Seguimiento

- Las seis pruebas que quedaron «Por automatizar» (P-S01-11, P-S01-12, P-S02-10, P-S03-12, P-S04-15 y P-S04-16) se implementaron en el commit `6b99fec` de la rama `docs/evidencias`. La batería completa dio 176 pruebas aprobadas y no reveló ningún defecto; el código de producción no se modificó. Las SPECS las registran con su nombre real desde la v0.4.

## Pendiente

- Revisión de cada SPEC por el integrante asignado.
