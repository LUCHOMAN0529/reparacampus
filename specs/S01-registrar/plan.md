# Plan de diseño · S01 Registrar

Versión 0.3 · 2026-10-08 · ajustado a la implementación · depende de [arquitectura](../../docs/diseno/arquitectura.md).

## Componentes que intervienen

| Capa | Elemento | Responsabilidad |
|---|---|---|
| Interfaz | `templates/incidencia_nueva.html` | Formulario con listas de catálogo y opción explícita Sí/No para el riesgo. |
| Rutas | `GET` y `POST /incidencias/nueva` | Leer el formulario, llamar al servicio, traducir errores a 400/403. |
| Autenticación | `requiere_rol("SOLICITANTE")` | Sesión y rol antes de cualquier lectura de datos. |
| Dominio | `dominio.validar_registro(datos)` | Validación pura de los cinco campos; devuelve datos limpios o errores por campo. |
| Dominio | `dominio.calcular_prioridad(impacto, riesgo)` | Regla de S02. |
| Servicio | `servicios.registrar_incidencia(db, usuario, datos, ahora)` | Transacción: incidencia + código + evento `CREAR`. |
| Persistencia | Tablas `incidencias` y `eventos` | Restricciones `CHECK` de catálogo como segunda barrera. |

## Decisiones

- La validación vive en el dominio, sin dependencia de Flask, para probarla sin servidor.
- El código se deriva del identificador autoincremental dentro de la misma transacción: `INC-` + identificador con seis dígitos.
- La fecha proviene del reloj del servidor, que la aplicación toma de su configuración (`RELOJ`, por defecto `reloj.ahora_utc`), nunca del formulario.
- El consecutivo se calcula dentro de la transacción, después de `BEGIN IMMEDIATE`, que serializa a los escritores; la columna `codigo` es única en la base.
- El servicio recibe solo los cinco campos permitidos; cualquier otro campo de la petición se descarta en la ruta.
- Jinja escapa automáticamente; no se usa el filtro `safe` con texto del usuario.

## Orden de comprobaciones

Sesión → rol → validación de datos → transacción.
