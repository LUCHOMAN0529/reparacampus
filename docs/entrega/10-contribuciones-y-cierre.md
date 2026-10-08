# Contribuciones y cierre

## Contribuciones por integrante

Estado al 2026-10-08. Esta tabla debe actualizarse con lo que cada persona haga realmente antes de la entrega; lo que no se haya hecho se deja como pendiente.

| Integrante | Tareas | Artefactos y commits | Revisión realizada | Resultado |
|---|---|---|---|---|
| Luis Carlo Daza Ospino | SPECS, diseño, implementación, pruebas y evidencias, con asistencia de IA | `specs/`, `docs/`, `app/`, `tests/`; commits de `c96e01b` en adelante, todos de su autoría | No aplica: es el autor | 176 pruebas aprobadas sobre `6b99fec` |
| Rafael Eduardo May Recuero | Revisión de S01 y del diseño | Pendiente | Pendiente | Pendiente |
| Jean Marco Oyola De Martino | Revisión de S02 | Pendiente | Pendiente | Pendiente |
| José Leonardo Hernández Pedrosa | Revisión de S03 | Pendiente | Pendiente | Pendiente |
| Cristian David Diaz España | Revisión de S04 | Pendiente | Pendiente | Pendiente |
| Jorge Luis González Arroyo | Revisión de S05 | Pendiente | Pendiente | Pendiente |

## Conclusión

**Cumplimiento.** El prototipo permite autenticarse con las cinco cuentas ficticias y ejecutar registro, prioridad, asignación, atención, validación, reapertura, filtros, tablero e historial según permisos. Los 53 criterios de aceptación de las cinco SPECS están en “Cumple”, respaldados por 176 pruebas automatizadas, tres de ellas de integración contra una base SQLite real. Doce errores introducidos a propósito fueron detectados por las pruebas.

**Pendientes y desviaciones que se declaran.**

- La revisión de las SPECS por otro integrante no se había realizado cuando se escribió el código. El historial de Git muestra ese orden.
- Las tres preguntas al cliente quedaron sin respuesta; se trabajó con supuestos declarados.
- El recorrido manual completo en navegador con los cinco usuarios no se ha hecho; solo se comprobó a mano el registro.
- La concurrencia se probó con ocho registros simultáneos en un mismo proceso contra SQLite; no hay prueba de carga. Con más carga, un registro podría fallar por la espera del bloqueo, sin dejar datos parciales.
- Los formularios no llevan token CSRF.
- Los responsables de los riesgos y los revisores son propuestas sin confirmar por el equipo.
- {{PENDIENTES_EQUIPO}}

**Aceptación del equipo.** {{ACEPTACION}}
