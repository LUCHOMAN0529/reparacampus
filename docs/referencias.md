# Referencias

Fuentes consultadas para el flujo de desarrollo guiado por especificaciones. Solo se listan las que realmente se abrieron.

| Fuente | Enlace | Consultada | Para qué se usó |
|---|---|---|---|
| Enunciado del examen: *Especifica. Construye. Verifica.* Universidad Simón Bolívar, Ingeniería de Software I | <https://examen-isi-specs-abril.ing-llanos-bravo.chatgpt.site> | 2026-10-08 | Requisitos RF01 a RF05, reglas, plantillas y rúbrica. |
| GitHub Spec Kit, *Spec-Driven Development Quickstart* | <https://github.github.com/spec-kit/quickstart.html> | 2026-10-08 | Flujo especificar → aclarar → planear → tareas → implementar → converger, y los archivos `spec.md`, `plan.md` y `tasks.md`. |
| Kiro, *Specs* | <https://kiro.dev/docs/specs/> | 2026-10-08 | Flujo en tres fases: requisitos, diseño y tareas. |

## Correspondencia con este repositorio

El equipo usó Markdown versionado, sin instalar Spec Kit ni Kiro. La estructura equivale así:

| Paso de Spec Kit | Fase de Kiro | En ReparaCampus |
|---|---|---|
| specify | Requisitos (`requirements.md`) | `specs/S0x-*/spec.md`: historia, entradas, reglas y criterios de aceptación |
| clarify | Requisitos | Preguntas al cliente y supuestos en `specs/00-problema-y-alcance.md` |
| plan | Diseño (`design.md`) | `specs/S0x-*/plan.md` y `docs/diseno/` |
| checklist | — | Formato de revisión en `docs/revision/` |
| tasks | Tareas (`tasks.md`) | `specs/S0x-*/tasks.md` |
| analyze | — | Revisión de consistencia entre SPEC, plan y tareas |
| implement | Ejecución de tareas | Una rama y un commit por SPEC |
| converge | — | Matriz SPEC frente a código en `docs/validacion/validacion.md` |

Las consultas a estas dos guías se hicieron después de escribir las SPECS; sirvieron para comprobar la correspondencia, no para generarlas.
