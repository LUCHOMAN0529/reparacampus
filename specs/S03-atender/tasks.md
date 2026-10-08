# Tareas · S03 Atender

Versión 0.3 · 2026-10-08. Cada tarea se registra como issue de GitHub con su RF, SPEC y AC.

El estado refleja lo que existe en el repositorio. «Implementada» significa que el código y sus pruebas están en una rama, no que la tarea esté terminada: ninguna tarea se da por terminada hasta que su pull request sea revisado por otro integrante. El revisor lo define el equipo.

| Tarea | Descripción | AC | Archivos | Prueba | Responsable | Revisor | Estado |
|---|---|---|---|---|---|---|---|
| T-S03-01 | Tabla `soluciones` de solo inserción. | AC-S03-02, 06 | `app/schema.sql` | P-S03-02 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `c5e7ef7`; pendiente de pull request y revisión |
| T-S03-02 | Servicio de inicio de atención con comprobación de asignación y estado. | AC-S03-01, 03, 04 | `app/servicios.py` | P-S03-01, P-S03-03 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `20ebd53`; pendiente de pull request y revisión |
| T-S03-03 | Servicio de registro de solución con validación de 20 a 800 caracteres. | AC-S03-02 a 06 | `app/servicios.py`, `app/dominio.py` | P-S03-02, P-S03-04, P-S03-05 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `20ebd53`; pendiente de pull request y revisión |
| T-S03-04 | Rutas y bloques de la interfaz del técnico. | AC-S03-01, 02, 08 | `app/rutas.py`, `app/templates/incidencia_detalle.html` | P-S03-01, P-S03-02 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `20ebd53`; pendiente de pull request y revisión |
| T-S03-05 | Pruebas automatizadas de S03. | Todos | `tests/test_s03_atencion.py` | P-S03-01 a 11 | Luis Carlo Daza Ospino, con IA | Por asignar | Implementada en `20ebd53`, `de49d68`; pendiente de pull request y revisión |
| T-S03-06 | Prueba de que iniciar y registrar solución no dejan efectos parciales. | AC-S03-09 | `tests/` | P-S03-12 | Por asignar | Por asignar | Por hacer |
