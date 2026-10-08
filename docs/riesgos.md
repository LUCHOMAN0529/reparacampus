# Riesgos y controles

Versión 0.2 · 2026-10-08 · evidencias sobre el commit `6b99fec` (176 pruebas aprobadas).

Cuatro riesgos: dos relacionados con la IA y dos con el producto. Cada control es algo que existe en el repositorio y se puede ejecutar; una advertencia en un prompt no cuenta como control.

Los responsables son una **propuesta del asistente** basada en la propuesta de revisores. Ningún integrante la ha aceptado todavía: es una decisión del equipo (ver [decisiones](decisiones.md), categoría B).

## R1 (IA) · La IA inventa una regla de negocio

| Aspecto | Detalle |
|---|---|
| Riesgo | El asistente agrega una transición o un permiso que el caso no tiene; por ejemplo, que el técnico o el coordinador puedan cerrar un reporte. |
| Causa | El modelo completa con lo que es habitual en otros sistemas de tickets, no con lo que dice el enunciado. |
| Ocurrió | Sí. El 2026-10-08 una revisión generada con IA propuso “aclarar que solo el coordinador cierra”, lo contrario de RF04. Ver [revisión asistida](revision/revision-asistida-ia-2026-10-08.md), sugerencia 7. |
| Impacto | Incidencias cerradas sin que el solicitante compruebe la solución: justo el problema que el cliente quiere eliminar. |
| Control 1 | Las transiciones y el rol que ejecuta cada una están en un solo lugar, `dominio.TRANSICIONES`; una operación que no esté allí no existe. |
| Control 2 | Criterios que prohíben el cierre por otros roles: AC-S03-07 y AC-S04-04, con pruebas. |
| Control 3 | Toda sugerencia de IA se contrasta con el enunciado, el código y las pruebas antes de aceptarla, y el resultado queda escrito. Así se trataron las 13 sugerencias de la primera revisión y las 24 observaciones de la segunda. |
| Responsable propuesto | Cristian David Diaz España (revisor propuesto de S04). Sin confirmar. |
| Verificación | `test_p_s04_05_solo_el_duenio_valida` y `test_no_hay_rutas_para_editar_o_borrar` aprobadas. Mutación M8 (permitir que el técnico cierre): **31 pruebas fallan**. |

## R2 (IA) · Las pruebas aceptan el mismo error que el código

| Aspecto | Detalle |
|---|---|
| Riesgo | El asistente escribe el código y sus pruebas con la misma interpretación equivocada, y todo pasa en verde. |
| Causa | Mismo autor para ambos; esperados calculados con la función que se está probando; pruebas que solo miran el código de respuesta. |
| Impacto | Falsa confianza: un defecto llega a la entrega con un reporte de pruebas “aprobado”. |
| Control 1 | Los resultados esperados se escriben en las SPECS antes que la prueba y en las pruebas son valores literales, no llamadas a producción. En la segunda revisión los criterios AC-S01-10, AC-S02-10, AC-S03-09 y AC-S04-11 se escribieron (SPECS v0.3) antes de que existieran sus pruebas. |
| Control 2 | Las pruebas comprueban los efectos en la base (estado, técnico, soluciones, cierres, eventos), no solo la respuesta HTTP. Las de atomicidad comparan las cinco tablas fila a fila. |
| Control 3 | Prueba de mutación: se introduce un error a la vez y se verifica que alguna prueba falle. |
| Control 4 | La matriz SPEC/código se llena criterio por criterio, lo que revela criterios sin prueba. |
| Control 5 | Una segunda revisión con otro asistente (ChatGPT) sobre las SPECS, contrastada después con el código. |
| Responsable propuesto | Jorge Luis González Arroyo (revisor propuesto de S05). Sin confirmar. |
| Verificación | [Validación, sección 6](validacion/validacion.md): doce mutaciones (M1 a M12), las doce detectadas. La matriz reveló el hallazgo H-03 y la segunda revisión el H-05; ambos se cerraron con pruebas nuevas (`de49d68`, `6b99fec`) sin que apareciera ningún defecto del código. |
| Límite | Código, pruebas y contraste siguen viniendo de asistentes de IA. La revisión de otro integrante, que es el control que el examen exige, no se ha hecho. |

## R3 (producto) · Un usuario accede a reportes ajenos

| Aspecto | Detalle |
|---|---|
| Riesgo | Un solicitante lee, confirma o reabre la incidencia de otro, o un técnico atiende una que no tiene asignada, cambiando el código en la dirección o enviando la petición a mano. |
| Causa | Confiar en que la interfaz oculta los botones; comprobar el rol pero no la pertenencia. |
| Impacto | Exposición de reportes de terceros y cierres hechos por quien no corresponde. |
| Control 1 | La identidad sale de la sesión, nunca del formulario. La sesión guarda solo el identificador y el rol se lee de la base en cada petición. |
| Control 2 | La condición de visibilidad está en un único punto, `consultas._visibilidad`, y la usan el listado, el detalle y todas las operaciones. |
| Control 3 | Lo que no es visible responde 404, sin revelar que existe (supuesto Q1). |
| Responsable propuesto | José Leonardo Hernández Pedrosa (revisor propuesto de S03). Sin confirmar. |
| Verificación | `test_p_s05_01_detalle_segun_permisos` (8 casos), `test_un_filtro_no_amplia_la_visibilidad`, `test_p_s03_03_tecnico_no_asignado`, `test_p_s04_05_solo_el_duenio_valida`. Mutación M3 (el solicitante ve todo): **9 pruebas fallan**. |
| Límite | Los formularios no llevan token CSRF; se declara como limitación conocida y mejora opcional. |

## R4 (producto) · Historial engañoso tras una operación fallida

| Aspecto | Detalle |
|---|---|
| Riesgo | Una operación rechazada o interrumpida deja un evento sin cambio de estado, un cambio de estado sin evento, o alguien altera el historial después. |
| Causa | Guardar estado e historial en pasos separados; validar después de escribir; permitir `UPDATE` o `DELETE` sobre el historial. |
| Impacto | El historial deja de ser prueba de lo ocurrido, que es la razón de ser del sistema. |
| Control 1 | Orden fijo: rol, visibilidad, estado y datos se comprueban **antes** de abrir cualquier escritura. |
| Control 2 | Cada operación es una transacción (`BEGIN IMMEDIATE` … `COMMIT`, o `ROLLBACK` ante cualquier error) que guarda estado, registros y evento juntos. |
| Control 3 | Disparadores en la base que abortan `UPDATE` y `DELETE` sobre `eventos`, `soluciones` y `cierres`. No existe ninguna ruta para editar o borrar. |
| Responsable propuesto | Rafael Eduardo May Recuero (revisor propuesto de S01 y del diseño). Sin confirmar. |
| Verificación | `test_las_operaciones_rechazadas_no_dejan_rastro` (siete rechazos; eventos idénticos fila a fila), `test_p_s05_04_el_historial_es_inmutable`. Atomicidad de las siete operaciones que escriben: `test_sin_efectos_parciales_si_falla_el_evento` (registro) y `test_un_fallo_al_guardar_el_evento_revierte_toda_la_operacion` (asignar, iniciar, solución, confirmar, rechazar y reabrir; 6 casos aprobados en `6b99fec`). Mutación M9 (la transacción confirma en lugar de revertir): **7 pruebas fallan**. Mutación M7 (rechazo sin motivo): **3 pruebas fallan**. |
| Límite | El fallo se inyecta en el guardado del evento, que es el último paso de la transacción. No se simulan cortes de energía ni fallos del disco. |

## Riesgos residuales declarados

No forman parte de los cuatro riesgos analizados. Se registran para que la entrega no afirme más de lo que se probó.

| ID | Riesgo residual | Qué se sabe | Qué no se probó |
|---|---|---|---|
| RR-1 | **Espera de bloqueo de SQLite con más carga.** Un escritor espera el bloqueo de la base hasta 5 segundos, el valor por defecto del módulo `sqlite3`. Si muchas operaciones de escritura coinciden, alguna podría agotar esa espera y responder con error. | La transacción no llega a abrirse o se revierte, así que no quedarían datos parciales. Con ocho registros simultáneos no ocurrió en ninguna de las ejecuciones. | No hay prueba con más de ocho escritores, con varios procesos servidores ni de carga sostenida. El caso de agotamiento de la espera no está probado. |
| RR-2 | **Alcance de la prueba de concurrencia.** `test_p_s01_11_registros_simultaneos` usa ocho hilos de un mismo proceso contra un archivo SQLite. | Aprobó en todas sus ejecuciones (65 veces el escenario sobre `6b99fec`, más las de la validación final). La mutación M10 la hace fallar, pero necesitó una pausa artificial de 10 ms para abrir la ventana de carrera. | No es una prueba de carga ni una garantía general de concurrencia. Solo cubre el registro; las transiciones simultáneas sobre una misma incidencia se protegen con la condición sobre el estado de origen, sin prueba con hilos. |
| RR-3 | **Sin token CSRF.** | La cookie de sesión usa `SameSite=Lax` y las operaciones que cambian datos exigen `POST`. | No hay defensa específica ni prueba contra una petición falsificada desde otro sitio. Queda como mejora opcional, no implementada por decisión del autor. |

## Situaciones abiertas del trabajo del equipo

Deben declararse en la entrega si siguen así:

- La revisión de las SPECS por otro integrante no se había hecho cuando se escribió el código; el historial de Git lo muestra. El 2026-10-08 el autor integró todas las ramas en `main` sin que el pull request #2 hubiera recibido ninguna revisión ni comentario.
- Al 2026-10-08 todos los commits son de un solo integrante.
- Las tres preguntas al cliente no tienen respuesta.
- Los responsables de estos riesgos son una propuesta sin confirmar.
