# Tareas · S01 Registrar

Versión 0.1 · 2026-10-08. Cada tarea se registra como issue de GitHub con su RF, SPEC y AC. El responsable y el revisor los define el equipo.

| Tarea | Descripción | AC | Archivos | Prueba | Responsable | Revisor | Estado |
|---|---|---|---|---|---|---|---|
| T-S01-01 | Esquema de `usuarios`, `incidencias` y `eventos`; seed con las cinco cuentas ficticias. | AC-S01-01 | `app/schema.sql`, `app/db.py` | P-S01-01 | Por asignar | Por asignar | Por hacer |
| T-S01-02 | Inicio y cierre de sesión con contraseñas con hash; decorador de rol. | AC-S01-02 | `app/auth.py`, `templates/login.html` | P-S01-04 | Por asignar | Por asignar | Por hacer |
| T-S01-03 | Validación de los cinco campos en el dominio. | AC-S01-03 a 06 | `app/dominio.py` | P-S01-02, P-S01-03 | Por asignar | Por asignar | Por hacer |
| T-S01-04 | Servicio de registro transaccional: incidencia, código y evento `CREAR`. | AC-S01-01, 02, 08, 09 | `app/servicios.py` | P-S01-01, P-S01-06 | Por asignar | Por asignar | Por hacer |
| T-S01-05 | Ruta y formulario de registro; detalle con texto escapado. | AC-S01-01, 07 | `app/rutas.py`, `templates/` | P-S01-05 | Por asignar | Por asignar | Por hacer |
| T-S01-06 | Pruebas automatizadas de S01. | Todos | `tests/test_s01_registro.py` | P-S01-01 a 06 | Por asignar | Por asignar | Por hacer |
