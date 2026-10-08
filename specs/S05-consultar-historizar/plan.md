# Plan de diseño · S05 Consultar, historizar y tablero

Versión 0.1 · 2026-10-08 · depende de [arquitectura](../../docs/diseno/arquitectura.md) y de S01 a S04.

## Componentes que intervienen

| Capa | Elemento | Responsabilidad |
|---|---|---|
| Rutas | `GET /incidencias` | Leer filtros, llamar a la consulta, mostrar la lista. |
| Rutas | `GET /incidencias/<codigo>` | Detalle e historial. |
| Rutas | `GET /tablero` | Resumen del coordinador. |
| Dominio | `dominio.validar_filtros(estado, prioridad)` | Catálogo o vacío. |
| Dominio | `dominio.porcentaje_cierre(cerradas, total)` | Función pura con `Decimal` y redondeo mitad hacia arriba; devuelve texto como `25,0 %`. |
| Consultas | `consultas.listar(db, usuario, estado, prioridad)` | Aplica la visibilidad por rol y después los filtros, con parámetros SQL. |
| Consultas | `consultas.historial(db, incidencia_id)` | Eventos con autor, solución, cierre y motivo. |
| Consultas | `consultas.tablero(db)` | Conteos, críticas no cerradas y porcentaje. |
| Servicio | `servicios._registrar_evento(...)` | Único punto que inserta eventos; lo usan todas las transiciones. |
| Persistencia | Disparadores `BEFORE UPDATE` y `BEFORE DELETE` en `eventos`, `soluciones` y `cierres` | Inmutabilidad garantizada por la base. |

## Decisiones

- La condición de visibilidad se construye en un único lugar y se reutiliza en listado, detalle y operaciones, para que un filtro no pueda ampliarla.
- Los filtros se pasan como parámetros de la consulta, nunca concatenados en el SQL.
- El tablero cuenta el estado actual de `incidencias`; no usa la tabla `cierres`, que conserva los cierres históricos.
- Los conteos parten del catálogo de estados y prioridades para mostrar también los ceros.
- La persistencia se prueba abriendo dos instancias sucesivas de la aplicación sobre el mismo archivo SQLite.

## Orden de comprobaciones

Sesión → rol (solo tablero) → validación de filtros → consulta con visibilidad.
