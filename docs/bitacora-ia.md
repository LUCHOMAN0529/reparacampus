# Bitácora de IA

Cuatro intervenciones relevantes, una por etapa: especificación, revisión, código y pruebas. No se copia la conversación completa.

> **Pendiente de Luis:** los campos “Decisión humana” recogen lo que consta en la conversación. Donde dice *por confirmar*, la decisión todavía no ha sido expresada por una persona y no debe entregarse así.

---

## Intervención 1 · Especificación

| Campo | Contenido |
|---|---|
| Fecha / autor / herramienta / modelo | 2026-10-08 · Luis Carlo Daza Ospino · Claude Code (aplicación de escritorio) · Claude Opus 5.5 |
| Historia y SPEC / versión | H01 a H05 · S01 a S05 v0.1 |
| Objetivo y contexto | Convertir RF01 a RF05 en cinco historias y cinco SPECS con la plantilla del examen. Se entregó el enunciado completo en PDF y los nombres del equipo. |
| Prompt o instrucción | «hagamos este proyecto», con la captura de la actividad; después, el PDF del enunciado y la lista de integrantes. |
| Respuesta relevante | Cinco SPECS con entre 8 y 13 criterios Dado/Cuando/Entonces, plan y tareas por SPEC, tres preguntas al cliente y once supuestos. El asistente se detuvo antes de programar y pidió la revisión de otro integrante, citando la regla central del examen. |
| Decisión humana y justificación | Luis no aprobó las SPECS él mismo: pidió un formato para que sus compañeros opinaran. Decidió además continuar con los supuestos, porque la docente no puede ser consultada antes del cierre. |
| Error o limitación | La tabla de pruebas de S03 afirmaba que la solución de ejemplo tenía 49 caracteres; tiene 50. Limitación: las preguntas al cliente quedaron sin respuesta. |
| Corrección y verificación | Se quitó la cifra antes de versionar. Los supuestos se declararon uno por uno en `specs/00-problema-y-alcance.md`. |
| Archivo / commit / prueba | `specs/` · commits `c96e01b`, `50fb915`, `d301e48` |

---

## Intervención 2 · Revisión

| Campo | Contenido |
|---|---|
| Fecha / autor / herramienta / modelo | 2026-10-08 · Luis Carlo Daza Ospino · borrador de revisión generado con un asistente de IA (**herramienta por indicar**); evaluado con Claude Code · Claude Opus 5.5 |
| Historia y SPEC / versión | S01 a S05 v0.1 → v0.2 |
| Objetivo y contexto | Obtener observaciones sobre las SPECS usando el formato de revisión. El asistente que generó el borrador solo tuvo el formato y el README; no leyó las SPECS porque consultó la rama `main`. |
| Prompt o instrucción | Se entregó el PDF «ReparaCampus_revision_borrador_simulado» para incorporarlo y continuar. |
| Respuesta relevante | Trece sugerencias. Entre ellas: «aclarar que solo el coordinador cierra». |
| Decisión humana y justificación | *Por confirmar por Luis.* Propuesta del asistente: aceptar cuatro sugerencias, dar nueve por ya cubiertas o aclaradas y descartar una. El borrador no se registró como revisión de ningún integrante porque él mismo advierte que no lo es. |
| Error o limitación | **Regla inventada:** el coordinador no cierra; según RF04 cierra el solicitante dueño. Además, toda la lista de comprobación venía en «Pendiente». |
| Corrección y verificación | La sugerencia errónea se descartó y se contrastó con AC-S04-04. Las aceptadas produjeron la versión 0.2. La mutación M8 confirma que las pruebas impiden que otro rol cierre (31 fallos). |
| Archivo / commit / prueba | `docs/revision/revision-asistida-ia-2026-10-08.md` · commit `a06aaf2` · `test_p_s04_05_solo_el_duenio_valida` |

---

## Intervención 3 · Código

| Campo | Contenido |
|---|---|
| Fecha / autor / herramienta / modelo | 2026-10-08 · Luis Carlo Daza Ospino · Claude Code · Claude Opus 5.5 |
| Historia y SPEC / versión | H01 a H05 · S01 a S05 v0.2 |
| Objetivo y contexto | Implementar las cinco funcionalidades a partir de las SPECS, el diseño y los contratos compartidos (transiciones, errores, orden de comprobación). |
| Prompt o instrucción | «por el momento solo continuaremos haciendo el trabajo». El asistente trabajó en cambios acotados: una rama y un commit por SPEC, con las pruebas de esa SPEC ejecutadas antes de pasar a la siguiente. |
| Respuesta relevante | `feat/base` y `feat/s01` a `feat/s05`. Reglas en `dominio.py`, operaciones transaccionales en `servicios.py`, visibilidad en `consultas.py`. |
| Decisión humana y justificación | Luis abrió la aplicación y reportó: «hay algunas paginas que no salen bien», con capturas. Tres eran plantillas abiertas como archivo, sin servidor; la cuarta, servida por Flask, se veía bien. Aceptación del código: *por confirmar por Luis* y sujeta a la revisión de cada pull request. |
| Error o limitación | Un comando de edición dañó las tildes de `app/servicios.py` al implementar S02. Limitación: el código se escribió antes de la revisión de las SPECS por otro integrante. |
| Corrección y verificación | Se restauró el archivo desde Git y se rehízo el cambio; 45 pruebas aprobadas antes del commit. El archivo dañado nunca se versionó. |
| Archivo / commit / prueba | `app/` · commits `c5e7ef7`, `7bc08f2`, `8479352`, `20ebd53`, `70468c0`, `786cf42` |

---

## Intervención 4 · Pruebas

| Campo | Contenido |
|---|---|
| Fecha / autor / herramienta / modelo | 2026-10-08 · Luis Carlo Daza Ospino · Claude Code · Claude Opus 5.5 |
| Historia y SPEC / versión | S01 a S05 v0.2 |
| Objetivo y contexto | Automatizar los escenarios del examen, incluidas tres pruebas de integración, y comprobar que la batería detecta errores reales. |
| Prompt o instrucción | «ahora que veine». El asistente propuso completar la evidencia de validación y comenzó por verificar las pruebas. |
| Respuesta relevante | 153 pruebas con esperados literales tomados de las SPECS; reloj controlado para el plazo de 48 horas; ocho mutaciones del código. |
| Decisión humana y justificación | *Por confirmar por Luis.* |
| Error o limitación | Todas las pruebas pasaron en la primera ejecución, lo que por sí solo no demuestra que puedan fallar. Al llenar la matriz se vio que AC-S02-06 y AC-S03-04 no se probaban en todos los estados. Limitación: código y pruebas vienen del mismo asistente. |
| Corrección y verificación | Se agregaron cinco casos (de 148 a 153). Se introdujeron ocho errores, uno a la vez: todos hicieron fallar entre 2 y 31 pruebas. La instalación y las pruebas se repitieron en una copia limpia. |
| Archivo / commit / prueba | `tests/` · commit `de49d68` · `docs/validacion/validacion.md`, secciones 5 y 6 |
