# Riesgos y controles

Versión 0.1 · 2026-10-08 · evidencias sobre el commit `de49d68`.

Cuatro riesgos: dos relacionados con la IA y dos con el producto. Cada control es algo que existe en el repositorio y se puede ejecutar; una advertencia en un prompt no cuenta como control.

Los responsables son una **propuesta** basada en la asignación de revisores; el equipo debe confirmarlos.

## R1 (IA) · La IA inventa una regla de negocio

| Aspecto | Detalle |
|---|---|
| Riesgo | El asistente agrega una transición o un permiso que el caso no tiene; por ejemplo, que el técnico o el coordinador puedan cerrar un reporte. |
| Causa | El modelo completa con lo que es habitual en otros sistemas de tickets, no con lo que dice el enunciado. |
| Ocurrió | Sí. El 2026-10-08 una revisión generada con IA propuso “aclarar que solo el coordinador cierra”, lo contrario de RF04. Ver [revisión asistida](revision/revision-asistida-ia-2026-10-08.md), sugerencia 7. |
| Impacto | Incidencias cerradas sin que el solicitante compruebe la solución: justo el problema que el cliente quiere eliminar. |
| Control 1 | Las transiciones y el rol que ejecuta cada una están en un solo lugar, `dominio.TRANSICIONES`; una operación que no esté allí no existe. |
| Control 2 | Criterios que prohíben el cierre por otros roles: AC-S03-07 y AC-S04-04, con pruebas. |
| Control 3 | Toda sugerencia de IA se contrasta con el enunciado antes de aceptarla y la decisión queda escrita. |
| Responsable propuesto | Cristian David Diaz España (revisor de S04). |
| Verificación | `test_p_s04_05_solo_el_duenio_valida` y `test_no_hay_rutas_para_editar_o_borrar` aprobadas. Mutación M8 (permitir que el técnico cierre): **31 pruebas fallan**. |

## R2 (IA) · Las pruebas aceptan el mismo error que el código

| Aspecto | Detalle |
|---|---|
| Riesgo | El asistente escribe el código y sus pruebas con la misma interpretación equivocada, y todo pasa en verde. |
| Causa | Mismo autor para ambos; esperados calculados con la función que se está probando; pruebas que solo miran el código de respuesta. |
| Impacto | Falsa confianza: un defecto llega a la entrega con un reporte de pruebas “aprobado”. |
| Control 1 | Los resultados esperados se escribieron en las SPECS antes del código y en las pruebas son valores literales, no llamadas a producción. |
| Control 2 | Las pruebas comprueban los efectos en la base (estado, técnico, soluciones, cierres, eventos), no solo la respuesta HTTP. |
| Control 3 | Prueba de mutación: se introduce un error a la vez y se verifica que alguna prueba falle. |
| Control 4 | La matriz SPEC/código se llena criterio por criterio, lo que revela criterios sin prueba. |
| Responsable propuesto | Jorge Luis González Arroyo (revisor de S05, donde está la mayoría de las pruebas transversales). |
| Verificación | [Validación, sección 6](validacion/validacion.md): ocho mutaciones, las ocho detectadas. La matriz reveló el hallazgo H-03 (estados sin probar) y se corrigió en `de49d68`. |

## R3 (producto) · Un usuario accede a reportes ajenos

| Aspecto | Detalle |
|---|---|
| Riesgo | Un solicitante lee, confirma o reabre la incidencia de otro, o un técnico atiende una que no tiene asignada, cambiando el código en la dirección o enviando la petición a mano. |
| Causa | Confiar en que la interfaz oculta los botones; comprobar el rol pero no la pertenencia. |
| Impacto | Exposición de reportes de terceros y cierres hechos por quien no corresponde. |
| Control 1 | La identidad sale de la sesión, nunca del formulario. La sesión guarda solo el identificador y el rol se lee de la base en cada petición. |
| Control 2 | La condición de visibilidad está en un único punto, `consultas._visibilidad`, y la usan el listado, el detalle y todas las operaciones. |
| Control 3 | Lo que no es visible responde 404, sin revelar que existe (supuesto Q1). |
| Responsable propuesto | José Leonardo Hernández Pedrosa (revisor de S03). |
| Verificación | `test_p_s05_01_detalle_segun_permisos` (8 casos), `test_un_filtro_no_amplia_la_visibilidad`, `test_p_s03_03_tecnico_no_asignado`, `test_p_s04_05_solo_el_duenio_valida`. Mutación M3 (el solicitante ve todo): **9 pruebas fallan**. |

## R4 (producto) · Historial engañoso tras una operación fallida

| Aspecto | Detalle |
|---|---|
| Riesgo | Una operación rechazada o interrumpida deja un evento sin cambio de estado, un cambio de estado sin evento, o alguien altera el historial después. |
| Causa | Guardar estado e historial en pasos separados; validar después de escribir; permitir `UPDATE` o `DELETE` sobre el historial. |
| Impacto | El historial deja de ser prueba de lo ocurrido, que es la razón de ser del sistema. |
| Control 1 | Orden fijo: rol, visibilidad, estado y datos se comprueban **antes** de abrir cualquier escritura. |
| Control 2 | Cada operación es una transacción (`BEGIN IMMEDIATE` … `COMMIT`, o `ROLLBACK` ante cualquier error) que guarda estado, registros y evento juntos. |
| Control 3 | Disparadores en la base que abortan `UPDATE` y `DELETE` sobre `eventos`, `soluciones` y `cierres`. No existe ninguna ruta para editar o borrar. |
| Responsable propuesto | Rafael Eduardo May Recuero (revisor de S01 y del diseño). |
| Verificación | `test_las_operaciones_rechazadas_no_dejan_rastro` (siete rechazos; eventos idénticos fila a fila), `test_sin_efectos_parciales_si_falla_el_evento`, `test_p_s05_04_el_historial_es_inmutable`. Mutación M7 (rechazo sin motivo): **3 pruebas fallan**. |

## Situaciones abiertas del trabajo del equipo

No son parte de los cuatro riesgos, pero deben declararse en la entrega si siguen así:

- La revisión de las SPECS por otro integrante no se había hecho cuando se escribió el código; el historial de Git lo muestra.
- Al 2026-10-08 todos los commits son de un solo integrante.
- Las tres preguntas al cliente no tienen respuesta.
