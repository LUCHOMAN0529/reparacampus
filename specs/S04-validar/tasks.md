# Tareas · S04 Validar

Versión 0.3 · 2026-10-08. Cada tarea se registra como issue de GitHub con su RF, SPEC y AC.

El estado refleja lo que existe en el repositorio. «Implementada» significa que el código y sus pruebas están en una rama, no que la tarea esté terminada: ninguna tarea se da por terminada hasta que su pull request sea revisado por otro integrante. El revisor lo define el equipo.

| Tarea | Descripción | AC | Archivos | Prueba | Responsable | Revisor | Estado |
|---|---|---|---|---|---|---|---|
| T-S04-01 | Tabla `cierres` de solo inserción. | AC-S04-01, 09 | `app/schema.sql` | P-S04-01 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `c5e7ef7`; pendiente de pull request y revisión |
| T-S04-02 | Servicio de confirmación: cierre, estado y evento. | AC-S04-01, 04, 05, 09 | `app/servicios.py` | P-S04-01, P-S04-05 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `70468c0`; pendiente de pull request y revisión |
| T-S04-03 | Servicio de rechazo con motivo de 10 a 300 caracteres. | AC-S04-02 a 05 | `app/servicios.py`, `app/dominio.py` | P-S04-02, P-S04-04 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `70468c0`; pendiente de pull request y revisión |
| T-S04-04 | Reloj inyectable y servicio de reapertura con plazo de 48 horas. | AC-S04-04 a 08, 10 | `app/reloj.py`, `app/servicios.py`, `app/dominio.py` | P-S04-03 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `c5e7ef7`, `70468c0`; pendiente de pull request y revisión |
| T-S04-05 | Rutas y bloques de la interfaz del solicitante. | AC-S04-01, 02, 06 | `app/rutas.py`, `app/templates/incidencia_detalle.html` | P-S04-01 a 03 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `70468c0`; pendiente de pull request y revisión |
| T-S04-06 | Pruebas automatizadas de S04, incluidas las tres de integración. | Todos | `tests/test_s04_validacion.py`, `tests/test_integracion.py` | P-S04-01 a 14 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `70468c0`; pendiente de pull request y revisión |
| T-S04-07 | Pruebas de motivo solo con espacios y de que confirmar, rechazar y reabrir no dejan efectos parciales. | AC-S04-03, 08, 11 | `tests/` | P-S04-15, P-S04-16 | Por asignar | Por asignar | Por hacer |
