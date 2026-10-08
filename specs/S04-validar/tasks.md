# Tareas · S04 Validar

Versión 0.1 · 2026-10-08. Cada tarea se registra como issue de GitHub con su RF, SPEC y AC. El responsable y el revisor los define el equipo.

| Tarea | Descripción | AC | Archivos | Prueba | Responsable | Revisor | Estado |
|---|---|---|---|---|---|---|---|
| T-S04-01 | Tabla `cierres` de solo inserción. | AC-S04-01, 09 | `app/schema.sql` | P-S04-01 | Por asignar | Por asignar | Por hacer |
| T-S04-02 | Servicio de confirmación: cierre, estado y evento. | AC-S04-01, 04, 05, 09 | `app/servicios.py` | P-S04-01, P-S04-05 | Por asignar | Por asignar | Por hacer |
| T-S04-03 | Servicio de rechazo con motivo de 10 a 300 caracteres. | AC-S04-02 a 05 | `app/servicios.py`, `app/dominio.py` | P-S04-02, P-S04-04 | Por asignar | Por asignar | Por hacer |
| T-S04-04 | Reloj inyectable y servicio de reapertura con plazo de 48 horas. | AC-S04-04 a 08, 10 | `app/reloj.py`, `app/servicios.py`, `app/dominio.py` | P-S04-03 | Por asignar | Por asignar | Por hacer |
| T-S04-05 | Rutas y bloques de la interfaz del solicitante. | AC-S04-01, 02, 06 | `app/rutas.py`, `templates/incidencia_detalle.html` | P-S04-01 a 03 | Por asignar | Por asignar | Por hacer |
| T-S04-06 | Pruebas automatizadas de S04, incluidas las tres de integración. | Todos | `tests/test_s04_validacion.py`, `tests/test_integracion.py` | P-S04-01 a 05 | Por asignar | Por asignar | Por hacer |
