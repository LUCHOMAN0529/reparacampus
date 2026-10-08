# Revisión asistida por IA de las SPECS v0.1

| Campo | Valor |
|---|---|
| Fecha | 2026-10-08 |
| Documento recibido | `ReparaCampus_revision_borrador_simulado.pdf`, entregado por Luis Carlo Daza Ospino |
| Naturaleza | Propuesta **simulada** generada con un asistente de IA sobre el formato de revisión |
| Versión de las SPECS | 0.1 |

## Qué es y qué no es

El documento recibido se declara a sí mismo como “propuesta simulada” y advierte que **no constituye revisiones realizadas ni aprobaciones personales de los estudiantes**. Además, quien lo generó no leyó las SPECS: consultó la rama `main`, donde aún no estaban, y dejó toda la lista de comprobación en “Pendiente”.

Por eso:

- **No cuenta como la revisión previa que exige el examen.** La revisión de cada integrante sigue pendiente y así consta en cada SPEC.
- Los nombres que aparecen en el documento se toman solo como una **propuesta** de revisor por SPEC.
- Sus sugerencias se evaluaron una por una contra las SPECS reales, como cualquier otra salida de IA. El resultado está abajo.

## Propuesta de revisores

Los nombres salen del borrador simulado. Ningún integrante ha confirmado esta asignación (ver `docs/decisiones.md`, B-2).

| SPEC | Revisor propuesto | Estado |
|---|---|---|
| S01 | Rafael Eduardo May Recuero | Pendiente |
| S02 | Jean Marco Oyola De Martino | Pendiente |
| S03 | José Leonardo Hernández Pedrosa | Pendiente |
| S04 | Cristian David Diaz España | Pendiente |
| S05 | Jorge Luis González Arroyo | Pendiente |
| Alcance y diseño | Rafael Eduardo May Recuero | Pendiente |

## Sugerencias evaluadas

Evaluación preparada con el asistente (Claude) y pendiente de confirmación por el autor de las SPECS.

| N.º | SPEC | Sugerencia de la IA | Decisión | Justificación y comprobación |
|---|---|---|---|---|
| 1 | S01 | Que cada error indique código HTTP, mensaje y ausencia de cambios. | Ya cubierta | Tabla “Errores y efectos” de S01 v0.1. |
| 2 | S01 | Pruebas con descripción de 19, 20, 500 y 501 caracteres. | **Aceptada** | AC-S01-03 ya tenía los cuatro límites, pero P-S01-02 solo probaba 19 y 20. Se amplió P-S01-02. |
| 3 | S01 | Definir si se normalizan espacios y mayúsculas. | Ya cubierta | SUP-03 (comparación exacta) y SUP-04 (recorte de espacios externos). |
| 4 | S02 | Documentar la tabla de prioridad, el 409 de la asignación repetida, el 400 del técnico inválido y la prohibición de reasignar. | Ya cubierta | Tabla de prioridad y AC-S02-06, 07 de S02 v0.1. |
| 5 | S03 | Decidir entre 404 y 403 para el técnico no asignado con el docente. | Ya cubierta | Es la pregunta Q1; queda como supuesto pendiente. |
| 6 | S03 | Pruebas de 19, 20, 800 y 801 caracteres. | Ya cubierta | P-S03-05 de S03 v0.1. |
| 7 | S03 | “Aclarar que solo el coordinador cierra”. | **Descartada: es un error** | Contradice RF04 y la regla “el coordinador no confirma ni reabre en nombre del solicitante”. Quien cierra es el solicitante dueño. AC-S04-04 exige 403 para el coordinador. Se conserva como ejemplo de regla inventada por la IA (riesgo de la Parte 4). |
| 8 | S04 | Dejar Q3 como supuesto pendiente; especificar UTC, cierre de referencia y límite inclusivo; conservación de soluciones y cierres. | Ya cubierta | Reglas de reapertura y AC-S04-06, 07, 09 de S04 v0.1. |
| 9 | S04 | Pruebas con motivo de 9, 10, 300 y 301 caracteres. | **Aceptada** | AC-S04-03 tenía los cuatro límites, pero P-S04-04 solo probaba 9 y 10. Se amplió P-S04-04. |
| 10 | S05 | Distinguir filtro inválido de búsqueda sin resultados. | **Aceptada** | No estaba dicho. Se agregó a AC-S05-03: valor válido sin coincidencias responde 200 con lista vacía. |
| 11 | S05 | Precisar qué roles pueden consultar el historial. | **Aceptada** | Estaba implícito en la visibilidad. Se agregó una frase explícita en “Reglas y proceso”. |
| 12 | S05 | Definir numerador, denominador, redondeo y caso vacío del porcentaje. | Ya cubierta | Regla del tablero y AC-S05-07, 08 de S05 v0.1. |
| 13 | General | Subir los archivos de `specs/` y `docs/diseno/` a la rama pública. | Aclarada | Están en la rama `specs/s01-s05`; llegarán a `main` cuando se integre su pull request. |

## Resultado

Las SPECS pasan a la versión 0.2 con los cambios 2, 9, 10 y 11. El campo “Decisión de revisión” de cada SPEC sigue en **Pendiente** hasta que el integrante propuesto la lea y registre su decisión.
