# Decisiones: confirmadas y pendientes

Versión 0.2 · 2026-10-08.

Este registro separa lo que ya decidió una persona de lo que solo ha propuesto el asistente de IA. Una propuesta del asistente, o algo conversado solo con el autor, **no** es una decisión del equipo ni de la docente.

## Decisiones tomadas por el autor (Luis Carlo Daza Ospino)

Constan en la conversación de trabajo con el asistente el 2026-10-08. Las instrucciones de las etapas llegaron como texto pegado en esa conversación.

| N.º | Decisión | Evidencia | Efecto en el repositorio |
|---|---|---|---|
| D-01 | Continuar el trabajo con supuestos, porque la docente no puede ser consultada antes del cierre. | Nota escrita al final del documento de revisión que entregó: «continuaremos haciendo el trabajo creando nosotros mismos el trabajo». Es una nota dentro de un documento, no un mensaje directo. | Preguntas Q1 a Q3 «sin respuesta» en `specs/00-problema-y-alcance.md`. |
| D-02 | Pedir a los compañeros su opinión con un formato. | «dame un documento con el espacio para que ellos escriban lo que les parece». | `docs/revision/Formato_revision_SPECS.docx`. |
| D-04 | Hacer una segunda revisión de las SPECS con ChatGPT y contrastarla con el código. | «La revisión documental […] se realizó en una conversación con ChatGPT»; «observaciones documentales que debes contrastar». | `docs/revision/revision-asistida-ia-02-chatgpt.md`. |
| D-05 | Trabajar por etapas autorizadas una a una: correcciones documentales, pruebas y evidencias. | «Autorizo avanzar por etapas». | Commits `46e8995`, `83861a7`, `3d283d4`, `6b99fec`, `925d22d`, `1335535`, `688972d`, `984669f`. |
| D-07 | No implementar el token CSRF; queda como mejora opcional y limitación declarada. | «No agregues CSRF todavía; déjalo como mejora opcional»; «Declara honestamente las limitaciones […] incluida la ausencia de protección CSRF si no se implementa». | Limitación declarada en README, arquitectura y riesgos. |
| D-08 | No marcar ninguna revisión humana como hecha ni atribuir aprobaciones a compañeros. | «No marques revisiones humanas como completadas»; «No inventes revisiones, aprobaciones, contribuciones». | «Decisión de revisión: Pendiente» en todas las SPECS. |
| D-09 | No cambiar código de producción para hacer pasar una prueba, ni cambiar una SPEC para que coincida con un resultado fallido. | Reglas de la Etapa 2 y de la instrucción de cierre. | `app/` no cambia desde `786cf42`. |
| D-10 | Usar PlantUML, descargado de su repositorio oficial, para exportar los diagramas. | Respondió «si» a la descarga. | `docs/diseno/img/`. |
| D-11 | Integrar todas las ramas en `main`, repetir la validación, generar el documento de entrega y crear el tag `release-examen`, sin esperar las revisiones de los compañeros y declarando que faltan. Reemplaza la indicación anterior de no integrar (D-06 en la versión 0.1 de este registro). | Instrucción de cierre: «integres el proyecto, ejecutes las verificaciones finales y prepares los archivos de entrega». | Fusiones `87f4572` a `8130550`; tag `release-examen`. |

**Corrección respecto de la versión 0.1.** Allí figuraba como D-03 «seguir con la implementación sin esperar la revisión de las SPECS». El autor nunca lo dijo de forma expresa: el asistente lo dedujo. Pasa a la lista A como A-8.

## A. Decisiones que el autor puede confirmar individualmente

Son propuestas del asistente o hechos que solo necesitan la palabra del autor. **Siguen sin confirmar.**

| N.º | Qué hay que decidir | Propuesta del asistente | Dónde queda registrado |
|---|---|---|---|
| A-1 | Qué hacer con las 13 sugerencias de la primera revisión simulada. | Aceptar 4, dar 8 por cubiertas o aclaradas y descartar 1 por errónea («solo el coordinador cierra»). | `docs/bitacora-ia.md`, intervención 2 |
| A-2 | Si acepta el código generado. | Aceptarlo. | Intervención 3 |
| A-3 | Si acepta las pruebas y la comprobación por mutación. | Aceptarlas. | Intervenciones 4 y 5 |
| A-4 | Con qué herramienta se generó el primer borrador de revisión (el PDF «simulado»). | Ninguna: es un dato que solo conoce el autor. | Intervención 2 |
| A-5 | Si figura como responsable de las 32 tareas, con la nota «con IA». | Sí, porque todos los commits son suyos. | `specs/*/tasks.md` |
| A-6 | Si mantiene los supuestos SUP-12 (solución vigente), SUP-13 (desempate del historial) y SUP-14 (registros simultáneos, con su alcance). | Mantenerlos: describen lo que el código hace y las pruebas confirman en el alcance probado. | `specs/00-problema-y-alcance.md` |
| A-7 | Si los códigos de los integrantes van en la portada. El enunciado los pide; el autor dijo que no hacían falta. | Incluirlos, por ser un requisito de la portada. | `docs/entrega/datos.json` |
| A-8 | Reconocer que el código se escribió antes de que otro integrante revisara las SPECS. | Declararlo como desviación de la regla central del examen; ya está declarado así en la entrega. | `docs/entrega/10-contribuciones-y-cierre.md` |

## B. Decisiones que debe acordar el equipo

Ninguna está tomada. El asistente no puede decidirlas, ni el autor en nombre de los demás.

| N.º | Qué hay que decidir | Estado actual | Quién |
|---|---|---|---|
| B-1 | Revisión de cada SPEC con fecha, versión y decisión. | Pendiente en las cinco SPECS, el alcance y el diseño. El pull request #2 se integró sin revisiones. | El revisor propuesto de cada una: Rafael (S01 y diseño), Jean Marco (S02), José Leonardo (S03), Cristian (S04), Jorge Luis (S05) |
| B-2 | Si la asignación de revisores es esa. | Es una propuesta que proviene de un borrador generado con IA; ningún integrante la ha aceptado. | Equipo |
| B-3 | Responsables funcionales de los cuatro riesgos. | Propuesta del asistente, sin confirmar. | Equipo |
| B-4 | Revisor de cada tarea. | «Por asignar» en las 32 tareas. | Equipo |
| B-5 | Aporte verificable de cada integrante y revisión de al menos un cambio de otra persona. | Solo hay commits de un integrante. | Cada integrante |
| B-6 | Nombre del equipo y grupo para la portada. | Sin dato. | Equipo |
| B-7 | Aceptación final del trabajo y pendientes que se declaran. | Sin dato. | Equipo |
| B-8 | Si se agrega el token CSRF. | No implementado; mejora opcional. | Equipo, a propuesta del autor |

### Cómo registrar una revisión

1. Abrir el formato `docs/revision/Formato_revision_SPECS.docx` y la SPEC correspondiente en `specs/`.
2. Llenar la sección de esa SPEC con nombre, fecha, versión revisada (0.5) y decisión.
3. Dejar constancia propia en GitHub: un comentario en el issue #1 o un commit que llene la tabla «Decisión de revisión» de la SPEC. Así queda también el aporte verificable de quien revisa.

## C. Decisiones que dependen de la docente o de una validación externa

| N.º | Qué hay que resolver | Supuesto con el que se trabaja |
|---|---|---|
| C-1 | Q1: ante una incidencia ajena, ¿403 o 404? | 404, sin revelar que existe. |
| C-2 | Q2: ¿el porcentaje de cierre usa el estado actual? ¿cómo se redondea? | Estado actual; redondeo aritmético a un decimal. |
| C-3 | Q3: precisión del plazo de 48 horas. | Exactamente 48 horas se acepta; un microsegundo después se rechaza. |
| C-4 | Si los supuestos SUP-01 a SUP-14 son aceptables para el cliente. | Se declaran uno por uno. |
| C-5 | Si es aceptable que la revisión de las SPECS no haya ocurrido antes del código ni de la integración. | Se declara como desviación de la regla central. |
| C-6 | Si las revisiones asistidas por IA cuentan como evidencia complementaria. | Se presentan como intervenciones de IA, no como revisión de un integrante. |
| C-7 | Nombre de la docente y grupo para la portada. | Sin dato. |
