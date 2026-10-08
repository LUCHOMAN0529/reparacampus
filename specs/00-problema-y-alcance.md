# Problema, alcance, preguntas y supuestos

| Campo | Valor |
|---|---|
| Versión | 0.3 (borrador en revisión) |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |
| Revisor | Asignado: Rafael Eduardo May Recuero. Revisión pendiente |
| Fecha | 2026-10-08 |

## 1. Necesidad

> “Nos reportan un daño por un mensaje, lo atendemos por otro y a veces lo damos por cerrado sin saber si quedó resuelto”.

La coordinación de mantenimiento de la Universidad Simón Bolívar no tiene un registro único de las incidencias de infraestructura. Los reportes llegan por canales distintos, no queda constancia de quién los atiende y se cierran sin que la persona afectada confirme la solución.

El prototipo ReparaCampus debe permitir **registrar** reportes, **priorizarlos**, **asignar** su atención y **comprobar** la solución con quien reportó, dejando un historial que no pueda alterarse.

## 2. Actores y permisos

| Actor | Puede | No puede |
|---|---|---|
| Solicitante | Registrar incidencias; consultar las propias; confirmar, rechazar o reabrir la solución de las propias. | Ver o operar incidencias ajenas; asignar; atender. |
| Coordinador | Consultar todas las incidencias; asignar un técnico activo a una incidencia REGISTRADA; ver el tablero. | Registrar; atender; confirmar, rechazar o reabrir en nombre del solicitante; reasignar. |
| Técnico | Consultar sus asignaciones; iniciar la atención; registrar la solución. | Ver u operar incidencias no asignadas a él; cerrar; asignar. |

El servidor obtiene identidad y rol de la sesión y comprueba rol y pertenencia en cada operación. Ocultar un botón no es un control.

## 3. Requisitos y especificaciones

| Requisito | Resumen | Historia | SPEC |
|---|---|---|---|
| RF01 | Registrar una incidencia | H01 | [S01](S01-registrar/spec.md) |
| RF02 | Calcular prioridad y asignar técnico | H02 | [S02](S02-priorizar-asignar/spec.md) |
| RF03 | Iniciar atención y registrar solución | H03 | [S03](S03-atender/spec.md) |
| RF04 | Confirmar, rechazar y reabrir | H04 | [S04](S04-validar/spec.md) |
| RF05 | Consultar, historizar y tablero | H05 | [S05](S05-consultar-historizar/spec.md) |

## 4. Alcance

**Incluye:** aplicación web con lógica en servidor y persistencia en SQLite; inicio y cierre de sesión con cinco cuentas ficticias (dos solicitantes, un coordinador, dos técnicos activos); las cinco funcionalidades anteriores; historial inmutable.

**Excluye (límites del prototipo):** adjuntos, notificaciones, hosting, IA dentro del producto, edición de reportes, cierre automático, reasignación de una incidencia ya ASIGNADA, restricción por especialidad del técnico, gestión de usuarios y autorregistro.

**Catálogos fijos:**

- Ubicaciones: `LAB-01`, `AULA-201`, `BIB-01`.
- Categorías: `ELECTRICIDAD`, `HIDRAULICA`, `MOBILIARIO`, `TIC`.
- Impacto: `BAJO`, `ALTO`.
- Prioridad (calculada): `CRITICA`, `ALTA`, `NORMAL`.
- Estados: `REGISTRADA`, `ASIGNADA`, `EN_ATENCION`, `PENDIENTE_VALIDACION`, `CERRADA`.

## 5. Reglas que no pueden cambiarse

1. Solo existen las transiciones descritas en el caso (ver [diagrama de estados](../docs/diseno/estados.puml)).
2. Una operación rechazada conserva estado e historial.
3. No hay cierre automático, edición de reportes ni reasignación.
4. El coordinador no confirma ni reabre en nombre del solicitante.
5. La reapertura se acepta si el tiempo desde el último cierre es menor o igual a 48 horas, calculado por el servidor con fechas UTC.
6. Los límites de texto se aplican después de retirar los espacios externos.
7. Estado e historial se guardan juntos, sin efectos parciales.
8. Los textos no se ejecutan como HTML ni como scripts.

## 6. Preguntas al cliente

Estas preguntas están **sin responder**. El 2026-10-08 el equipo informó que no puede consultar a la docente antes del cierre de la entrega: la única sesión con ella coincide con el día del parcial. Por eso el prototipo se construye con el supuesto indicado y cada pregunta se declara como pendiente. Una respuesta de la IA no es una decisión del cliente.

| ID | Pregunta | Por qué importa | Supuesto de trabajo | Respuesta del cliente |
|---|---|---|---|---|
| Q1 | Cuando un solicitante o un técnico intenta abrir u operar una incidencia que no le pertenece, ¿el sistema debe decir que no tiene permiso o debe responder como si la incidencia no existiera? | Define si se revela la existencia de reportes ajenos y qué código de respuesta se prueba. | Se responde 404 (no encontrada), sin revelar que existe. | Sin respuesta; se mantiene el supuesto |
| Q2 | ¿El porcentaje de cierre del tablero cuenta las incidencias que están CERRADAS en este momento o las que alguna vez se cerraron? ¿Cómo se redondea el decimal? | Cambia el resultado tras una reapertura y en valores como 1/3. | Cuenta el estado actual, de modo que reabrir reduce el porcentaje. Redondeo aritmético (mitad hacia arriba): 1/3 = 33,3 %; 2/3 = 66,7 %. | Sin respuesta; se mantiene el supuesto |
| Q3 | ¿Con qué precisión se mide el plazo de 48 horas de la reapertura y qué significa “un instante después”? | Determina el caso límite que se prueba. | El servidor compara marcas UTC con precisión de microsegundos: exactamente 48 h se acepta; 48 h más un microsegundo se rechaza. | Sin respuesta; se mantiene el supuesto |

## 7. Supuestos pendientes de confirmar

| ID | Supuesto | SPEC afectada |
|---|---|---|
| SUP-01 | El código de la incidencia tiene el formato `INC-000001`, consecutivo y generado por el servidor. | S01 |
| SUP-02 | El riesgo para personas se envía como valor explícito `true` o `false`. Un valor ausente se rechaza: no se asume `false`. | S01 |
| SUP-03 | Los valores de catálogo se comparan de forma exacta, con distinción de mayúsculas: `alto` se rechaza. | S01 |
| SUP-04 | La longitud de un texto se cuenta en caracteres después de retirar espacios externos; los espacios y saltos de línea interiores cuentan. | S01, S03, S04 |
| SUP-05 | Un técnico solo ve las incidencias que tiene asignadas, no las que están sin asignar. | S03, S05 |
| SUP-06 | Un técnico es “activo” si su cuenta está marcada como activa. Una cuenta inactiva no puede iniciar sesión ni recibir asignaciones. | S02 |
| SUP-07 | El plazo de reapertura se cuenta desde el cierre más reciente; cada reapertura y nuevo cierre reinicia el plazo. | S04 |
| SUP-08 | El coordinador ve el detalle y el historial completo de todas las incidencias, pero solo puede asignar. | S05 |
| SUP-09 | Los filtros de estado y prioridad se combinan con “y”. Un valor de filtro fuera del catálogo se rechaza con error en lugar de devolver una lista vacía. | S05 |
| SUP-10 | En el tablero, “CRITICA no cerradas” lista las incidencias con prioridad CRITICA cuyo estado actual no es CERRADA. | S05 |
| SUP-11 | Las contraseñas de las cinco cuentas ficticias se publican en el README, porque son datos de prueba. | Autenticación |
| SUP-12 | La «solución vigente» de una incidencia es la última registrada; es la que se confirma o se rechaza. | S04 |
| SUP-13 | El historial se muestra en el orden en que se registraron los eventos; ante dos eventos con la misma marca de tiempo, el desempate es su identificador consecutivo. | S05 |
| SUP-14 | Registros enviados a la vez se atienden uno tras otro; todos se crean, con códigos consecutivos distintos. | S01 |

## 8. Registro de revisión

| Fecha | Versión | Revisor | Decisión | Observaciones |
|---|---|---|---|---|
| Pendiente | 0.3 | Rafael Eduardo May Recuero (asignado) | Pendiente | |
