# Diseño de ReparaCampus

| Campo | Valor |
|---|---|
| Versión | 0.1 (borrador en revisión, previo a la implementación) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Pendiente: otro integrante del equipo |
| Fecha | 2026-10-08 |

Este documento se ajustará a la versión final del código. Los diagramas están en PlantUML junto a este archivo.

## 1. Componentes

Monolito modular en tres capas. Diagrama: [componentes.puml](componentes.puml).

| Capa | Módulo | Responsabilidad | No hace |
|---|---|---|---|
| Interfaz | `app/templates/`, `app/static/` | Formularios, listados, detalle, tablero. Muestra u oculta acciones según rol y estado. | No decide permisos ni reglas. |
| Entrada HTTP | `app/rutas.py` | Lee la petición, llama a servicios o consultas, traduce errores a códigos HTTP. | No contiene reglas de negocio ni SQL. |
| Entrada HTTP | `app/auth.py` | Inicio y cierre de sesión, carga del usuario de la sesión, decoradores de sesión y rol. | |
| Lógica de negocio | `app/dominio.py` | Catálogos, validaciones, prioridad, tabla de transiciones, plazo de reapertura, porcentaje. Funciones puras. | No conoce Flask ni la base. |
| Lógica de negocio | `app/servicios.py` | Casos de uso que cambian datos. Cada uno es una transacción: estado + registros + evento. | |
| Lógica de negocio | `app/consultas.py` | Lecturas con la visibilidad por rol. | No modifica datos. |
| Lógica de negocio | `app/reloj.py` | Única fuente de la hora UTC; reemplazable en pruebas. | |
| Persistencia | `app/db.py`, `app/schema.sql` | Conexión SQLite por petición, esquema, seed ficticio. | |

**Dónde se ejecutan las reglas:** siempre en el servidor, en `dominio` y `servicios`. La interfaz solo evita mostrar acciones que el servidor rechazaría.

## 2. Modelo de datos

Diagrama: [datos.puml](datos.puml).

| Tabla | Contenido | Notas |
|---|---|---|
| `usuarios` | Cuenta, nombre, rol, hash de contraseña, activo. | Cinco cuentas ficticias en el seed. |
| `incidencias` | Código, solicitante, ubicación, categoría, descripción, impacto, riesgo, prioridad, estado actual, técnico. | Único registro que se actualiza; solo cambian `estado` y, una vez, `tecnico_id`. |
| `asignaciones` | Incidencia, técnico, coordinador, fecha. | `incidencia_id` único: no hay reasignación. |
| `soluciones` | Incidencia, técnico, texto, fecha. | Solo inserción. |
| `cierres` | Incidencia, solución confirmada, solicitante, fecha. | Solo inserción; uno por cada confirmación. |
| `eventos` | Incidencia, actor, acción, estado anterior, estado nuevo, motivo, solución, cierre, fecha. | Solo inserción; es el historial. |

Las fechas se guardan como texto ISO 8601 en UTC con microsegundos (`2026-10-08T15:04:05.000000Z`). Los catálogos tienen restricciones `CHECK`. Las claves foráneas están activas.

`eventos`, `soluciones` y `cierres` tienen disparadores que abortan cualquier `UPDATE` o `DELETE`.

## 3. Estados y transiciones

Diagrama: [estados.puml](estados.puml).

| Acción | Origen | Destino | Quién | SPEC |
|---|---|---|---|---|
| `CREAR` | — | `REGISTRADA` | Solicitante | S01 |
| `ASIGNAR` | `REGISTRADA` | `ASIGNADA` | Coordinador | S02 |
| `INICIAR_ATENCION` | `ASIGNADA` | `EN_ATENCION` | Técnico asignado | S03 |
| `REGISTRAR_SOLUCION` | `EN_ATENCION` | `PENDIENTE_VALIDACION` | Técnico asignado | S03 |
| `CONFIRMAR_SOLUCION` | `PENDIENTE_VALIDACION` | `CERRADA` | Solicitante dueño | S04 |
| `RECHAZAR_SOLUCION` | `PENDIENTE_VALIDACION` | `EN_ATENCION` | Solicitante dueño | S04 |
| `REABRIR` | `CERRADA` | `EN_ATENCION` | Solicitante dueño, hasta 48 h después del último cierre | S04 |

No existe ninguna otra transición. Esta tabla se implementa una sola vez en `dominio.TRANSICIONES` y todos los servicios la consultan.

## 4. Contratos compartidos

### 4.1 Rutas

| Método y ruta | Rol | SPEC |
|---|---|---|
| `GET`, `POST /login`; `POST /logout` | Cualquiera | Autenticación |
| `GET /` | Con sesión | Redirige al listado o al tablero |
| `GET /incidencias?estado=&prioridad=` | Con sesión | S05 |
| `GET`, `POST /incidencias/nueva` | Solicitante | S01 |
| `GET /incidencias/<codigo>` | Con visibilidad | S05 |
| `POST /incidencias/<codigo>/asignar` | Coordinador | S02 |
| `POST /incidencias/<codigo>/iniciar` | Técnico asignado | S03 |
| `POST /incidencias/<codigo>/solucion` | Técnico asignado | S03 |
| `POST /incidencias/<codigo>/confirmar` | Solicitante dueño | S04 |
| `POST /incidencias/<codigo>/rechazar` | Solicitante dueño | S04 |
| `POST /incidencias/<codigo>/reabrir` | Solicitante dueño | S04 |
| `GET /tablero` | Coordinador | S05 |

Una operación exitosa responde 302 hacia el detalle. Un error muestra la página con el mensaje y el código correspondiente.

### 4.2 Errores

| Código | Significado | Excepción de dominio |
|---|---|---|
| 302 a `/login` | No hay sesión | — |
| 400 | Dato ausente, fuera de catálogo o fuera de límites | `ErrorValidacion` |
| 403 | El rol no puede ejecutar la operación | `ErrorPermiso` |
| 404 | La incidencia no existe o el usuario no puede verla | `NoEncontrada` |
| 409 | El estado actual o el plazo no permiten la operación | `ErrorEstado` |

### 4.3 Orden de comprobación de una operación

1. **Sesión.** ¿Hay un usuario activo en la sesión?
2. **Rol.** ¿Su rol puede ejecutar esta acción?
3. **Visibilidad.** ¿La incidencia existe y le pertenece (dueño o técnico asignado)?
4. **Estado.** ¿El estado actual es el origen de la transición? En la reapertura, ¿está dentro del plazo?
5. **Datos.** ¿El texto o el técnico enviados son válidos?
6. **Transacción.** Cambio de estado, registros asociados y evento; todo o nada.

Si falla cualquier paso del 1 al 5 no se abre ninguna escritura. Si falla el paso 6 se revierte completo.

### 4.4 Transacciones

Cada servicio abre una transacción con `BEGIN IMMEDIATE`, actualiza el estado con una condición sobre el estado de origen (`UPDATE … WHERE id = ? AND estado = ?`), comprueba que afectó una fila, inserta los registros asociados y el evento, y confirma. Ante cualquier excepción se ejecuta `ROLLBACK`. Así estado e historial quedan siempre juntos.

### 4.5 Seguridad

- Contraseñas con `werkzeug.security.generate_password_hash`; nunca en texto plano.
- Sesión de Flask (cookie firmada, `HttpOnly`, `SameSite=Lax`). La sesión guarda solo el identificador del usuario; el rol se lee de la base en cada petición.
- No hay selector de rol: el rol es un atributo de la cuenta.
- Jinja con autoescape; no se usa `safe` con texto del usuario. Las consultas SQL usan parámetros.
- Las operaciones que cambian datos solo aceptan `POST`.

## 5. Flujo de validación de una operación

Secuencia del rechazo de una solución, con permisos y evento: [secuencia-rechazo.puml](secuencia-rechazo.puml).

## 6. Decisión de arquitectura

[ADR-001: reglas de negocio en una capa de dominio y servicios, con SQL directo sobre SQLite](adr-001-capa-de-dominio.md).

## 7. Registro de revisión

| Fecha | Versión | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.1 | Pendiente | Pendiente | |
