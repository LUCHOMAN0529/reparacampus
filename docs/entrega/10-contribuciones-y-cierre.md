# Contribuciones y cierre

## Contribuciones por integrante

Estado al 2026-10-08, tomado del historial de Git y de GitHub. Lo que no se ha hecho figura como pendiente.

| Integrante | Tareas | Artefactos y commits | Revisión realizada | Resultado |
|---|---|---|---|---|
| Luis Carlo Daza Ospino | SPECS, diseño, implementación, pruebas, evidencias e integración, con asistencia de IA | `specs/`, `docs/`, `app/`, `tests/`; todos los commits del repositorio son de su autoría | No aplica: es el autor | {{PRUEBAS}} |
| Rafael Eduardo May Recuero | Propuesta: revisión de S01, del alcance y del diseño | Ninguno registrado | Pendiente | Pendiente |
| Jean Marco Oyola De Martino | Propuesta: revisión de S02 | Ninguno registrado | Pendiente | Pendiente |
| José Leonardo Hernández Pedrosa | Propuesta: revisión de S03 | Ninguno registrado | Pendiente | Pendiente |
| Cristian David Diaz España | Propuesta: revisión de S04 | Ninguno registrado | Pendiente | Pendiente |
| Jorge Luis González Arroyo | Propuesta: revisión de S05 | Ninguno registrado | Pendiente | Pendiente |

La asignación de revisores es una propuesta que el equipo no ha confirmado. El requisito de que cada integrante aporte una contribución verificable y revise al menos un cambio de otra persona **no está cumplido** a esta fecha.

## Integración

El 2026-10-08 el autor integró en `main` las ocho ramas de trabajo, en orden de dependencia y sin conflictos: `specs/s01-s05` (pull request #2), `feat/base`, `feat/s01-registrar`, `feat/s02-priorizar-asignar`, `feat/s03-atender`, `feat/s04-validar`, `feat/s05-consultar-historizar` y `docs/evidencias`. Las ramas se conservan. Ningún pull request fue revisado por otro integrante antes de integrarse.

## Conclusión

**Cumplimiento.** El prototipo permite autenticarse con las cinco cuentas ficticias y ejecutar registro, prioridad, asignación, atención, validación, reapertura, filtros, tablero e historial según permisos. Los 53 criterios de aceptación de las cinco SPECS están en “Cumple”. Resultado de la batería sobre el tag de entrega: {{PRUEBAS}}. Doce errores introducidos a propósito fueron detectados por las pruebas.

**Pendientes y desviaciones que se declaran.**

- El código se escribió y se integró sin que otro integrante revisara las SPECS ni los cambios. El historial de Git muestra ese orden.
- Todos los commits son de un solo integrante.
- Las tres preguntas al cliente quedaron sin respuesta; se trabajó con supuestos declarados.
- El recorrido manual en navegador con los cinco usuarios no lo ha hecho ninguna persona. Existe un recorrido automatizado por HTTP contra el servidor real, descrito en la sección de validación.
- La concurrencia se probó con ocho registros simultáneos en un mismo proceso contra SQLite; no hay prueba de carga. Con más carga, un registro podría fallar por la espera del bloqueo, sin dejar datos parciales.
- Los formularios no llevan token CSRF.
- Los responsables de los riesgos y los revisores son propuestas sin confirmar por el equipo.
- El tablero de GitHub Projects y los issues 2 a 8 no se crearon; solo existe el issue #1.

**Aceptación del equipo.** Pendiente. Ningún integrante distinto del autor ha registrado su aceptación. El detalle de lo confirmado y lo pendiente está en `docs/decisiones.md`.
