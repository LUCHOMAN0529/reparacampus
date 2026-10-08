# Bitácora de IA

Seis intervenciones relevantes: especificación, revisión, código, pruebas, una segunda revisión con sus pruebas, y la integración final. No se copia la conversación completa.

> **Pendiente de Luis:** los campos “Decisión humana” recogen lo que consta en la conversación. Donde dice *por confirmar*, la decisión todavía no ha sido expresada por una persona y no debe entregarse así. La lista completa de lo confirmado y lo pendiente está en [decisiones.md](decisiones.md).
>
> Ninguna decisión de esta bitácora es del equipo: todas son del autor o propuestas del asistente. Las revisiones de los demás integrantes siguen pendientes.

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
| Decisión humana y justificación | *Por confirmar por Luis.* Propuesta del asistente: aceptar cuatro sugerencias, dar ocho por ya cubiertas o aclaradas y descartar una. El borrador no se registró como revisión de ningún integrante porque él mismo advierte que no lo es. |
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
| Corrección y verificación | (Estado a ese momento; la intervención 5 lo amplía a 176 pruebas y doce mutaciones.) Se agregaron cinco casos (de 148 a 153). Se introdujeron ocho errores, uno a la vez: todos hicieron fallar entre 2 y 31 pruebas. La instalación y las pruebas se repitieron en una copia limpia. |
| Archivo / commit / prueba | `tests/` · commit `de49d68` · `docs/validacion/validacion.md`, secciones 5 y 6 |

---

## Intervención 5 · Segunda revisión y pruebas derivadas

| Campo | Contenido |
|---|---|
| Fecha / autor / herramienta / modelo | 2026-10-08 · Luis Carlo Daza Ospino · ChatGPT para la revisión documental (modelo no indicado); Claude Code · Claude Opus 5.5 para el contraste, las correcciones y las pruebas |
| Historia y SPEC / versión | H01 a H05 · S01 a S05 v0.2 → v0.3 → v0.4 |
| Objetivo y contexto | Revisar las SPECS con un segundo asistente y comprobar cada observación contra el código y las pruebas antes de aceptar nada. Se entregaron al asistente las 24 observaciones y la instrucción de auditar primero, sin modificar archivos. |
| Prompt o instrucción | Instrucciones sucesivas del autor: «Empieza con la auditoría. No modifiques ni integres nada hasta presentarme el diagnóstico»; después, la autorización de la Etapa 1 (correcciones documentales), la de la Etapa 2 (pruebas) y la de la Etapa 3 (evidencias), cada una con sus límites. |
| Respuesta relevante | Diagnóstico: 11 observaciones ya cubiertas, 6 con prueba existente pero mal reflejada en la SPEC y 7 vacíos reales; ningún defecto del código. Cuatro criterios nuevos (AC-S01-10, AC-S02-10, AC-S03-09, AC-S04-11) escritos antes que sus pruebas. Después, 23 casos de prueba: atomicidad de seis transiciones, registros simultáneos, riesgo estricto y motivos solo con espacios. |
| Decisión humana y justificación | **Confirmadas por Luis:** trabajar por etapas autorizadas una a una; no integrar pull requests, no crear el tag ni el PDF final; no agregar el token CSRF por ahora; no marcar revisiones humanas como hechas; no cambiar código de producción ni ajustar una SPEC a un resultado fallido. **Por confirmar por Luis:** si acepta las pruebas nuevas y si mantiene los supuestos SUP-12, SUP-13 y SUP-14. |
| Error o limitación | En el diagnóstico el asistente contó “27 observaciones, 17 cubiertas y 10 vacíos”; eran 24, con 11, 6 y 7. En la intervención 2 había escrito “nueve” sugerencias cubiertas donde eran ocho. Limitaciones: la prueba de concurrencia usa ocho hilos de un mismo proceso contra SQLite y no es una prueba de carga; la atomicidad se prueba con un fallo en el último paso de la transacción; con más carga, un escritor podría agotar la espera de 5 segundos del bloqueo de SQLite. |
| Corrección y verificación | Los recuentos se corrigieron en el registro de revisión y en esta bitácora. Verificación: `python -m pytest` dio 176 aprobadas y 0 fallidas sobre `6b99fec`; las pruebas nuevas se ejecutaron primero una por una. Cuatro mutaciones (M9 a M12) confirmaron que las pruebas nuevas fallan cuando se rompe lo que vigilan. No apareció ningún defecto y `app/` no se modificó. |
| Archivo / commit / prueba | `docs/revision/revision-asistida-ia-02-chatgpt.md` (`46e8995`) · SPECS v0.3 (`83861a7`) y v0.4 (`1335535`) · `tests/test_atomicidad.py`, `tests/test_concurrencia.py` (`6b99fec`) · `docs/validacion/validacion.md` (`925d22d`) |

---

## Intervención 6 · Integración y cierre

| Campo | Contenido |
|---|---|
| Fecha / autor / herramienta / modelo | 2026-10-08 · Luis Carlo Daza Ospino · Claude Code · Claude Opus 5.5 |
| Historia y SPEC / versión | H01 a H05 · S01 a S05 v0.5 |
| Objetivo y contexto | Integrar las ocho ramas en una sola versión, dejar la documentación coherente, repetir la validación sobre la versión integrada y preparar la entrega. |
| Prompt o instrucción | «Necesito que trabajes sobre el repositorio real, corrijas los defectos encontrados, integres el proyecto, ejecutes las verificaciones finales y prepares los archivos de entrega», con la prohibición de inventar revisiones, aprobaciones o datos. |
| Respuesta relevante | Análisis previo: las ramas forman una cadena lineal desde `a06aaf2` y ningún archivo fue modificado por los dos lados. Ocho fusiones sin conflictos en la rama `integracion/release-examen`, en orden de dependencia. Después, correcciones documentales, validación, tag y documento de entrega. |
| Decisión humana y justificación | **Confirmada por Luis:** integrar y cerrar sin esperar las revisiones de sus compañeros, declarando esa ausencia. Esta decisión reemplaza su indicación anterior de no integrar. La aceptación del resultado por el equipo sigue pendiente. |
| Error o limitación | La auditoría previa encontró errores del asistente en la evidencia: una decisión del autor registrada sin que él la hubiera expresado (implementar antes de la revisión), un recuento inexacto de ejecuciones de la prueba de concurrencia (55 en lugar de 65) y revisores escritos como «asignados» cuando solo estaban propuestos. Limitación: los pull requests no fueron revisados por otro integrante, y el asistente no puede editar la descripción del pull request #2 ni crear issues en GitHub. |
| Corrección y verificación | Los tres errores se corrigieron en `docs/decisiones.md`, `docs/validacion/validacion.md` y las SPECS v0.5. La validación final consta en `docs/validacion/ejecucion-final.md`, con el SHA probado y la salida de pytest. |
| Archivo / commit / prueba | Fusiones `87f4572` a `8130550` · `docs/validacion/ejecucion-final.md` · tag `release-examen` |
