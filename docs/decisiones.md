# Decisiones: confirmadas y pendientes

Versión 0.1 · 2026-10-08.

Este registro separa lo que ya decidió una persona de lo que solo ha propuesto el asistente de IA. Una propuesta del asistente, o algo conversado solo con el autor, **no** es una decisión del equipo ni de la docente.

## Decisiones ya tomadas por el autor (Luis Carlo Daza Ospino)

Constan en la conversación de trabajo con el asistente el 2026-10-08.

| N.º | Decisión | Efecto en el repositorio |
|---|---|---|
| D-01 | Continuar el trabajo con supuestos, porque la docente no puede ser consultada antes del cierre. | Preguntas Q1 a Q3 «sin respuesta» en `specs/00-problema-y-alcance.md`. |
| D-02 | Pedir a los compañeros su opinión con un formato, en lugar de aprobar él mismo las SPECS. | `docs/revision/Formato_revision_SPECS.docx`. |
| D-03 | Seguir con la implementación sin esperar la revisión de las SPECS. | El código se escribió antes de la revisión; se declara como desviación. |
| D-04 | Hacer una segunda revisión de las SPECS con ChatGPT y contrastarla con el código. | `docs/revision/revision-asistida-ia-02-chatgpt.md`. |
| D-05 | Trabajar por etapas autorizadas una a una: correcciones documentales, pruebas y evidencias. | Commits `46e8995`, `83861a7`, `3d283d4`, `6b99fec`, `925d22d` y los de esta etapa. |
| D-06 | No integrar ningún pull request, no crear el tag ni generar el PDF final hasta nueva autorización. | `main` sigue en `0f3c391`. |
| D-07 | No implementar el token CSRF por ahora; queda como mejora opcional. | Limitación declarada en README, arquitectura y riesgos. |
| D-08 | No marcar ninguna revisión humana como hecha ni atribuir aprobaciones a compañeros. | «Decisión de revisión: Pendiente» en todas las SPECS. |
| D-09 | No cambiar código de producción para hacer pasar una prueba, ni cambiar una SPEC para que coincida con un resultado fallido. | `app/` no cambia desde `786cf42`. |
| D-10 | Usar PlantUML, descargado de su repositorio oficial, para exportar los diagramas. | `docs/diseno/img/`. |

## A. Decisiones que el autor puede confirmar individualmente

Son propuestas del asistente que solo necesitan la palabra del autor. **Siguen sin confirmar.**

| N.º | Qué hay que decidir | Propuesta del asistente | Dónde queda registrado |
|---|---|---|---|
| A-1 | Qué hacer con las 13 sugerencias de la primera revisión simulada. | Aceptar 4, dar 8 por cubiertas o aclaradas y descartar 1 por errónea («solo el coordinador cierra»). | `docs/bitacora-ia.md`, intervención 2 |
| A-2 | Si acepta el código generado en las ramas `feat/*`. | Aceptarlo, sujeto a la revisión de cada pull request. | Intervención 3 |
| A-3 | Si acepta las pruebas y la comprobación por mutación. | Aceptarlas. | Intervenciones 4 y 5 |
| A-4 | Con qué herramienta se generó el primer borrador de revisión (el PDF «simulado»). | Ninguna: es un dato que solo conoce el autor. | Intervención 2 |
| A-5 | Si figura como responsable de las 32 tareas, con la nota «con IA». | Sí, porque todos los commits son suyos. | `specs/*/tasks.md` |
| A-6 | Si mantiene los supuestos SUP-12 (solución vigente), SUP-13 (desempate del historial) y SUP-14 (registros simultáneos, con su alcance). | Mantenerlos: describen lo que el código hace y las pruebas confirman. | `specs/00-problema-y-alcance.md` |
| A-7 | Si los códigos de los integrantes van en la portada. El enunciado los pide; el autor dijo que no hacían falta. | Incluirlos, por ser un requisito de la portada. | `docs/entrega/datos.json` |

## B. Decisiones que debe acordar el equipo

Ninguna está tomada. El asistente no puede decidirlas ni el autor en nombre de los demás.

| N.º | Qué hay que decidir | Estado actual | Quién |
|---|---|---|---|
| B-1 | Revisión de cada SPEC con fecha, versión y decisión. | Pendiente en las cinco SPECS, el alcance y el diseño. El pull request #2 no tiene revisiones. | Cada revisor asignado: Rafael (S01 y diseño), Jean Marco (S02), José Leonardo (S03), Cristian (S04), Jorge Luis (S05) |
| B-2 | Si la asignación de revisores es esa. | Proviene de un borrador generado con IA; ningún integrante la ha aceptado. | Equipo |
| B-3 | Responsables funcionales de los cuatro riesgos. | Propuesta del asistente, sin confirmar. | Equipo |
| B-4 | Revisor de cada tarea y de cada pull request. | «Por asignar» en las 32 tareas. | Equipo |
| B-5 | Aporte verificable de cada integrante y revisión de al menos un cambio de otra persona. | Solo hay commits de un integrante. | Cada integrante |
| B-6 | Nombre del equipo y grupo para la portada. | Sin dato. | Equipo |
| B-7 | Aceptación final del trabajo y pendientes que se declaran. | Sin dato. | Equipo |
| B-8 | Si se agrega el token CSRF antes de entregar. | No implementado; mejora opcional. | Equipo, a propuesta del autor |

## C. Decisiones que dependen de la docente o de una validación externa

| N.º | Qué hay que resolver | Supuesto con el que se trabaja |
|---|---|---|
| C-1 | Q1: ante una incidencia ajena, ¿403 o 404? | 404, sin revelar que existe. |
| C-2 | Q2: ¿el porcentaje de cierre usa el estado actual? ¿cómo se redondea? | Estado actual; redondeo aritmético a un decimal. |
| C-3 | Q3: precisión del plazo de 48 horas. | Exactamente 48 horas se acepta; un microsegundo después se rechaza. |
| C-4 | Si los supuestos SUP-01 a SUP-14 son aceptables para el cliente. | Se declaran uno por uno. |
| C-5 | Si es aceptable que la revisión de las SPECS ocurra después de escribir el código. | Se declara como desviación de la regla central. |
| C-6 | Si las revisiones asistidas por IA cuentan como evidencia complementaria. | Se presentan como intervenciones de IA, no como revisión de un integrante. |
| C-7 | Nombre de la docente, grupo y fecha oficial de entrega para la portada. | Sin dato. |
