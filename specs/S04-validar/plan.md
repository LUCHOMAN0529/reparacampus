# Plan de diseño · S04 Validar

Versión 0.3 · 2026-10-08 · ajustado a la implementación · depende de [arquitectura](../../docs/diseno/arquitectura.md), S01, S02 y S03.
Secuencia del rechazo en [secuencia-rechazo.puml](../../docs/diseno/secuencia-rechazo.puml).

## Componentes que intervienen

| Capa | Elemento | Responsabilidad |
|---|---|---|
| Rutas | `POST /incidencias/<codigo>/confirmar`, `/rechazar`, `/reabrir` | Leer `motivo` cuando aplica y llamar al servicio. |
| Dominio | `dominio.validar_texto(motivo, 10, 300, "motivo")` | Recorte y límites. |
| Dominio | `dominio.dentro_de_plazo_reapertura(cerrada_en, ahora)` | Función pura: `ahora − cerrada_en <= 48 h`. |
| Servicio | `servicios.confirmar`, `servicios.rechazar`, `servicios.reabrir` | Comprobaciones y transacción. |
| Reloj | `reloj.ahora_utc()` | Única fuente de la hora; reemplazable en pruebas mediante la configuración de la aplicación. |
| Persistencia | Tabla `cierres`, solo inserción | Un registro por cada confirmación; nunca se borra al reabrir. |

## Decisiones

- El “último cierre” es la fila de `cierres` más reciente de la incidencia (la de mayor identificador). La “solución vigente” es la fila de `soluciones` más reciente (`servicios._solucion_vigente`). No se guarda una fecha de cierre en la incidencia, para que no exista un dato que haya que limpiar al reabrir.
- La reapertura no borra ni marca el cierre: el evento `REABRIR` referencia el cierre que se reabre.
- El plazo se evalúa con objetos de fecha con zona UTC, no comparando cadenas.
- Fuera de plazo se responde 409 porque es una condición del estado del recurso, no un dato mal formado.
- El rechazo no crea fila en una tabla propia: el motivo vive en el evento, que es inmutable.

## Orden de comprobaciones

Sesión → rol → visibilidad (pertenencia) → estado → plazo (solo reabrir) → validación del motivo → transacción.
