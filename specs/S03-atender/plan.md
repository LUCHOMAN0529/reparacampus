# Plan de diseño · S03 Atender

Versión 0.5 · 2026-10-08 · ajustado a la implementación · depende de [arquitectura](../../docs/diseno/arquitectura.md), S01 y S02.

## Componentes que intervienen

| Capa | Elemento | Responsabilidad |
|---|---|---|
| Rutas | `POST /incidencias/<codigo>/iniciar` | Llamar al servicio de inicio. |
| Rutas | `POST /incidencias/<codigo>/solucion` | Leer `solucion`, llamar al servicio. |
| Dominio | `dominio.validar_texto(valor, minimo, maximo, campo)` | Recorte y límites; se reutiliza en S04 para los motivos. |
| Servicio | `servicios.iniciar_atencion(...)` y `servicios.registrar_solucion(...)` | Comprobaciones y transacción. |
| Consultas | `consultas.obtener(db, usuario, codigo)` | Devuelve la incidencia solo si el usuario puede verla; si no, 404. Se comparte con S04 y S05. |
| Interfaz | Bloques “Iniciar atención” y “Registrar solución” en el detalle | Visibles solo al técnico asignado y en el estado correspondiente. |
| Persistencia | Tabla `soluciones`, solo inserción | Disparadores que impiden modificar o borrar. |

## Decisiones

- La pertenencia se comprueba comparando `incidencias.tecnico_id` con el usuario de la sesión, nunca con un dato del formulario.
- La solución y el cambio de estado van en la misma transacción; si el evento falla, no queda la solución.
- El evento guarda `solucion_id` para que el historial muestre el texto sin duplicarlo.

## Orden de comprobaciones

Sesión → rol → visibilidad (asignación) → estado → validación del texto → transacción.
