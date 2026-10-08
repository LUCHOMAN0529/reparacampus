# Herramientas e implementación

## Herramientas y versiones

| Actividad | Herramienta | Versión |
|---|---|---|
| Asistente de IA (especificación, código, pruebas, contraste e integración) | Claude Code (aplicación de escritorio), modelo Claude Opus 5.5 | — |
| Asistente de IA (segunda revisión documental de las SPECS) | ChatGPT | Modelo no indicado |
| Servidor | Python + Flask | Python 3.14.3 · Flask 3.1.3 (Werkzeug 3.1.9, Jinja2 3.1.6) |
| Persistencia | SQLite, módulo `sqlite3` de la biblioteca estándar | 3.50.4 |
| Interfaz | HTML, CSS y JavaScript con plantillas Jinja | — |
| Pruebas | pytest y cliente de pruebas de Flask | 9.1.1 |
| Versiones y equipo | Git y GitHub | Git 2.53.0 |
| Modelado | PlantUML | 1.2026.8 |
| SPECS | Markdown versionado en `specs/` | — |
| Documento final | Microsoft Word, exportado a PDF | — |

## Cómo se usó la IA

Se usaron dos asistentes: Claude Code para especificar, implementar, probar y contrastar, y ChatGPT para una segunda revisión documental de las SPECS. Se entregó al asistente el enunciado, y después cada SPEC con su plan, el modelo de estados y los contratos compartidos. La implementación se pidió en cambios acotados: una rama y un commit por SPEC, con las pruebas de esa SPEC ejecutadas antes de pasar a la siguiente. No se generó la aplicación con un único prompt.

## Evidencia de las cinco funcionalidades

| Funcionalidad | SPEC | Rama | Commit | Pruebas | Cómo verla en el prototipo |
|---|---|---|---|---|---|
| Registrar | S01 | `feat/s01-registrar` | `7bc08f2` | 26 + 5 de concurrencia | `solicitante1` → Nueva incidencia |
| Priorizar y asignar | S02 | `feat/s02-priorizar-asignar` | `8479352` | 21 + 1 de atomicidad | `coordinador1` → Incidencias → abrir una REGISTRADA → Asignar |
| Atender | S03 | `feat/s03-atender` | `20ebd53` | 19 + 2 de atomicidad | `tecnico1` → Incidencias → Iniciar atención → Registrar solución |
| Validar y reabrir | S04 | `feat/s04-validar` | `70468c0` | 43 + 3 de integración + 3 de atomicidad | `solicitante1` → abrir la incidencia → Confirmar, Rechazar o Reabrir |
| Consultar, historial y tablero | S05 | `feat/s05-consultar-historizar` | `786cf42` | 46 aprobadas | Cualquier usuario → Incidencias; `coordinador1` → Tablero |

La autenticación con las cinco cuentas ficticias está en `feat/base` (commit `c5e7ef7`, 7 pruebas).

La columna de pruebas cuenta las que existen en la versión integrada. Las ramas `feat/*` se conservan con las pruebas de su momento; las agregadas después (commits `de49d68` y `6b99fec`) llegaron a `main` con la rama `docs/evidencias`.
