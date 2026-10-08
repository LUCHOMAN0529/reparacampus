# Tareas · S02 Priorizar y asignar

Versión 0.5 · 2026-10-08. Cada tarea se registra como issue de GitHub con su RF, SPEC y AC.

El estado refleja lo que existe en el repositorio. «Implementada» significa que el código y sus pruebas existen y están integrados en `main`, no que la tarea esté terminada: ninguna se da por terminada hasta que otro integrante la revise. La integración la hizo el autor sin esa revisión. El revisor lo define el equipo.

| Tarea | Descripción | AC | Archivos | Prueba | Responsable | Revisor | Estado |
|---|---|---|---|---|---|---|---|
| T-S02-01 | Función pura de prioridad e integración en el registro. | AC-S02-01, 02, 03, 09 | `app/dominio.py`, `app/servicios.py` | P-S02-01 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `c5e7ef7`, `7bc08f2`; integrada en `main`; revisión de otro integrante pendiente |
| T-S02-02 | Tabla `asignaciones` con unicidad por incidencia. | AC-S02-04, 06 | `app/schema.sql` | P-S02-02, P-S02-03 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `c5e7ef7`; integrada en `main`; revisión de otro integrante pendiente |
| T-S02-03 | Servicio de asignación con comprobaciones de rol, estado y técnico. | AC-S02-04 a 08 | `app/servicios.py`, `app/dominio.py` | P-S02-02 a 05 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `8479352`; integrada en `main`; revisión de otro integrante pendiente |
| T-S02-04 | Ruta de asignación y bloque en el detalle para el coordinador. | AC-S02-04 | `app/rutas.py`, `app/templates/incidencia_detalle.html` | P-S02-02 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `8479352`; integrada en `main`; revisión de otro integrante pendiente |
| T-S02-05 | Pruebas automatizadas de S02. | Todos | `tests/test_s02_prioridad_asignacion.py` | P-S02-01 a 09 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `8479352`, `de49d68`; integrada en `main`; revisión de otro integrante pendiente |
| T-S02-06 | Prueba de que la asignación no deja efectos parciales. | AC-S02-10 | `tests/test_atomicidad.py` | P-S02-10 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `6b99fec`; integrada en `main`; revisión de otro integrante pendiente |
