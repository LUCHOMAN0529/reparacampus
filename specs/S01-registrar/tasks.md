# Tareas · S01 Registrar

Versión 0.5 · 2026-10-08. Cada tarea se registra como issue de GitHub con su RF, SPEC y AC.

El estado refleja lo que existe en el repositorio. «Implementada» significa que el código y sus pruebas existen y están integrados en `main`, no que la tarea esté terminada: ninguna se da por terminada hasta que otro integrante la revise. La integración la hizo el autor sin esa revisión. El revisor lo define el equipo.

| Tarea | Descripción | AC | Archivos | Prueba | Responsable | Revisor | Estado |
|---|---|---|---|---|---|---|---|
| T-S01-01 | Esquema de `usuarios`, `incidencias` y `eventos`; seed con las cinco cuentas ficticias. | AC-S01-01 | `app/schema.sql`, `app/db.py` | P-S01-01 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `c5e7ef7`; integrada en `main`; revisión de otro integrante pendiente |
| T-S01-02 | Inicio y cierre de sesión con contraseñas con hash; decorador de rol. | AC-S01-02 | `app/auth.py`, `app/templates/login.html` | P-S01-04 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `c5e7ef7`; integrada en `main`; revisión de otro integrante pendiente |
| T-S01-03 | Validación de los cinco campos en el dominio. | AC-S01-03 a 06 | `app/dominio.py` | P-S01-02, P-S01-03 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `c5e7ef7`; integrada en `main`; revisión de otro integrante pendiente |
| T-S01-04 | Servicio de registro transaccional: incidencia, código y evento `CREAR`. | AC-S01-01, 02, 08, 09 | `app/servicios.py` | P-S01-01, P-S01-06 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `7bc08f2`; integrada en `main`; revisión de otro integrante pendiente |
| T-S01-05 | Ruta y formulario de registro; detalle con texto escapado. | AC-S01-01, 07 | `app/rutas.py`, `app/templates/` | P-S01-05 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `7bc08f2`; integrada en `main`; revisión de otro integrante pendiente |
| T-S01-06 | Pruebas automatizadas de S01. | Todos | `tests/test_s01_registro.py` | P-S01-01 a 10 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `7bc08f2`; integrada en `main`; revisión de otro integrante pendiente |
| T-S01-07 | Pruebas de registros simultáneos y de valores de riesgo `True`, `1` y `on`. | AC-S01-05, 10 | `tests/test_concurrencia.py`, `tests/test_s01_registro.py` | P-S01-11, P-S01-12 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `6b99fec`; integrada en `main`; revisión de otro integrante pendiente |
