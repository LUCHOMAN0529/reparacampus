# ADR-001 · Reglas de negocio en una capa de dominio y servicios, con SQL directo sobre SQLite

| Campo | Valor |
|---|---|
| Estado | Propuesta, pendiente de revisión del equipo |
| Fecha | 2026-10-08 |
| Autor | Luis Carlo Daza Ospino, con asistencia de IA (Claude) |

## Contexto

El caso exige que las reglas se ejecuten en el servidor, que estado e historial se guarden juntos sin efectos parciales, que una operación rechazada no deje rastro y que el plazo de 48 horas se pueda probar sin esperar tiempo real. El equipo trabaja con Flask y SQLite, tiene una semana y varias personas programan en paralelo.

## Decisión

1. Separar el monolito en tres capas: rutas (HTTP), lógica de negocio (`dominio`, `servicios`, `consultas`) y persistencia.
2. Escribir las reglas —validaciones, prioridad, transiciones, plazo, porcentaje— como funciones puras en `dominio`, sin dependencia de Flask ni de la base.
3. Hacer de cada operación un servicio que ejecuta una única transacción con el módulo `sqlite3` de la biblioteca estándar y SQL explícito.
4. Obtener la hora de un reloj inyectable.

## Alternativas consideradas

| Alternativa | A favor | En contra |
|---|---|---|
| Reglas dentro de las funciones de ruta | Menos archivos; rápido al inicio. | Las reglas quedan mezcladas con HTTP; cada ruta repetiría permisos y transiciones; difícil probar sin servidor. |
| ORM (Flask-SQLAlchemy) | Menos SQL manual; modelos declarativos. | Otra dependencia y otra capa que aprender en una semana; el control de la transacción y de los disparadores es menos visible. |
| Reglas en la base (disparadores para todo) | Imposible saltarlas desde el código. | Difíciles de leer, probar y relacionar con cada AC; los mensajes de error son pobres. |
| **Capa de dominio + servicios + SQL directo (elegida)** | Cada regla está en un solo lugar y se prueba sola; la transacción es explícita; sin dependencias adicionales. | Más SQL escrito a mano; hay que mantener la disciplina de no poner reglas en las rutas. |

## Consecuencias

- Las pruebas unitarias cubren `dominio` sin base de datos; las de integración usan el cliente de Flask contra un archivo SQLite real.
- La tabla de transiciones es el único lugar donde se define qué cambios de estado existen. Una transición inventada (por una persona o por la IA) no funciona si no está allí.
- La base conserva una segunda barrera: restricciones `CHECK`, unicidad de la asignación y disparadores de inmutabilidad.
- Cambiar de SQLite a otro motor exigiría revisar el SQL y los disparadores. Se acepta porque el prototipo no lo requiere.
- Un integrante puede trabajar en la interfaz, otro en un servicio y otro en las pruebas con pocos conflictos.
