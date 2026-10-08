# Tareas · S05 Consultar, historizar y tablero

Versión 0.3 · 2026-10-08. Cada tarea se registra como issue de GitHub con su RF, SPEC y AC.

El estado refleja lo que existe en el repositorio. «Implementada» significa que el código y sus pruebas están en una rama, no que la tarea esté terminada: ninguna tarea se da por terminada hasta que su pull request sea revisado por otro integrante. El revisor lo define el equipo.

| Tarea | Descripción | AC | Archivos | Prueba | Responsable | Revisor | Estado |
|---|---|---|---|---|---|---|---|
| T-S05-01 | Consulta de listado con visibilidad por rol y filtros validados. | AC-S05-01, 02, 03 | `app/consultas.py`, `app/dominio.py` | P-S05-01, P-S05-02 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `786cf42`; pendiente de pull request y revisión |
| T-S05-02 | Consulta de historial con soluciones, motivos y cierres. | AC-S05-04, 11 | `app/consultas.py` | P-S05-01 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `7bc08f2`; pendiente de pull request y revisión |
| T-S05-03 | Disparadores de inmutabilidad y punto único de registro de eventos. | AC-S05-05, 06 | `app/schema.sql`, `app/servicios.py` | P-S05-04 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `c5e7ef7`, `7bc08f2`; pendiente de pull request y revisión |
| T-S05-04 | Rutas y plantillas de listado y detalle. | AC-S05-01 a 04, 13 | `app/rutas.py`, `app/templates/` | P-S05-01, P-S05-02, P-S05-06 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `7bc08f2`, `786cf42`; pendiente de pull request y revisión |
| T-S05-05 | Tablero del coordinador y cálculo del porcentaje. | AC-S05-07 a 10 | `app/consultas.py`, `app/dominio.py`, `app/templates/tablero.html` | P-S05-03, P-S05-06 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `786cf42`; pendiente de pull request y revisión |
| T-S05-06 | Pruebas automatizadas de S05, incluida la persistencia tras reinicio. | Todos | `tests/test_s05_consulta_tablero.py` | P-S05-01 a 12 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `786cf42`; pendiente de pull request y revisión |
