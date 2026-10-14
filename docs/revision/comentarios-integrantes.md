# Comentarios de los integrantes sobre las SPECS

Cada integrante leyó la parte del documento de entrega que le correspondía y respondió la [encuesta de revisión](Encuesta_revision_integrantes.docx). Las respuestas se copian **tal como las escribió cada persona**, sin corregirlas. Después de cada una se indica qué se hizo con ella.

Los comentarios llegaron después de que el código estuviera escrito e integrado, así que no cuentan como revisión previa a la implementación.

| Integrante | Parte | Recibido | Estado |
|---|---|---|---|
| Rafael Eduardo May Recuero | S01 Registrar | — | Sin respuesta |
| Jean Marco Oyola De Martino | S02 Priorizar y asignar | — | Sin respuesta |
| José Leonardo Hernández Pedrosa | S03 Atender | 2026-10-13, entregado al autor | Recibido |
| Cristian David Diaz España | S04 Validar | — | Sin respuesta |
| Jorge Luis González Arroyo | S05 Consultar y tablero | 2026-10-13, entregado al autor | Recibido |

## José Leonardo Hernández Pedrosa · S03 Atender una incidencia

Recibido el 2026-10-13. El integrante declara que usó ChatGPT como apoyo.

**1. Con tus palabras: ¿qué hace esta parte del sistema?**

> Esta parte permite gestionar una incidencia asignándole un técnico y actualizando su estado. También permite registrar la solución del problema para llevar un control de la atención hasta que se resuelva.

**2. ¿Hay algo que no se entienda o que te parezca mal definido? ¿Qué?**

> Me parece que se podría explicar mejor qué sucede cuando una incidencia no puede resolverse y qué condiciones se deben cumplir para cerrarla. Así sería más claro cómo debe actuar el sistema en cada situación.

**3. ¿Cambiarías o agregarías algo? ¿Qué y por qué?**

> Agregaría mensajes de confirmación cuando se actualice una incidencia y validaciones para evitar guardar información incompleta. Esto ayudaría a prevenir errores y facilitaría el uso del sistema.

**4. ¿Usaste IA para revisarla? Si sí: ¿cuál, y con qué parte de su respuesta estás de acuerdo y con cuál no?**

> Sí, utilicé ChatGPT como apoyo para revisar esta parte. Estoy de acuerdo con la idea de mejorar las validaciones y los mensajes de confirmación, porque ayudan a evitar errores. Sin embargo, considero que las sugerencias deben compararse con los requisitos del proyecto antes de aplicarlas.

### Qué se hizo con cada observación

| Observación | Contraste con el enunciado y el código | Acción |
|---|---|---|
| Explicar qué pasa si una incidencia no puede resolverse | El enunciado no define un estado para ese caso y prohíbe agregar transiciones. En el código, la incidencia simplemente sigue `EN_ATENCION` hasta que el técnico registra una solución. | **Aceptada como aclaración.** S03 v0.6 lo dice de forma explícita en «Alcance y exclusiones». No cambia ningún requisito ni el código. |
| Explicar qué condiciones se deben cumplir para cerrarla | Está definido en S04: solo el solicitante dueño cierra, confirmando una solución en `PENDIENTE_VALIDACION`. S03 no lo remitía a S04. | **Aceptada como aclaración.** S03 v0.6 remite a S04. |
| Validaciones para no guardar información incompleta | Ya existen: la solución exige de 20 a 800 caracteres después de retirar espacios (AC-S03-05) y una operación inválida no guarda nada (AC-S03-09). Pruebas aprobadas: `test_p_s03_05_limites_de_la_solucion`, `test_un_fallo_al_guardar_el_evento_revierte_toda_la_operacion`. | Ya cubierta. Sin cambios. |
| Mensajes de confirmación al actualizar una incidencia | Hoy, tras una operación exitosa, la página vuelve al detalle con el estado nuevo y el evento en el historial, pero sin un mensaje explícito. El enunciado no lo exige. | **Registrada como mejora opcional, no implementada.** Implementarla cambiaría código ya etiquetado y probado. |

Su observación de que «las sugerencias deben compararse con los requisitos del proyecto antes de aplicarlas» coincide con el criterio que se siguió para las revisiones asistidas por IA.

El integrante no expresó una decisión de aprobar o rechazar la SPEC; por eso la tabla «Decisión de revisión» de S03 registra el comentario, no una aprobación.

## Jorge Luis González Arroyo · S05 Consultar, historizar y tablero

Recibido el 2026-10-13. El integrante firmó como «Jorge Gonzalez» y declara que usó ChatGPT como apoyo.

**1. Con tus palabras: ¿qué hace esta parte del sistema?**

> Esta parte permite consultar las incidencias registradas, revisar su historial y ver un tablero con información general sobre su estado. Así se puede hacer seguimiento a los casos y conocer cómo van las solicitudes sin tener que revisar cada una por separado.

**2. ¿Hay algo que no se entienda o que te parezca mal definido? ¿Qué?**

> Me parece que sería importante dejar más claro qué información puede consultar cada rol y qué datos se muestran en el tablero. También sería bueno definir mejor cómo se organizan los registros del historial para que sea fácil entender los cambios que ha tenido una incidencia.

**3. ¿Cambiarías o agregarías algo? ¿Qué y por qué?**

> Agregaría filtros por fecha, estado, prioridad y técnico, además de una búsqueda por número de incidencia. Esto ayudaría a encontrar los casos más rápido y haría que el tablero fuera más útil cuando haya muchas incidencias registradas.

**4. ¿Usaste IA para revisarla? Si sí: ¿cuál, y con qué parte de su respuesta estás de acuerdo y con cuál no?**

> Sí, utilicé ChatGPT como apoyo para revisar esta parte del proyecto. Estoy de acuerdo con que el historial y el tablero ayudan a hacer seguimiento a las incidencias, y con que los filtros y la claridad de la información son importantes. No tengo un desacuerdo concreto, aunque considero que las sugerencias de la IA deben compararse con los requisitos del proyecto antes de tomarlas como definitivas.

### Qué se hizo con cada observación

| Observación | Contraste con el enunciado y el código | Acción |
|---|---|---|
| Qué información puede consultar cada rol | S05 ya lo define en la tabla «Precondiciones y permisos». Al revisarlo apareció una imprecisión real: la SPEC decía que el listado muestra solicitante y técnico «según el rol», sin decir cómo, y la interfaz los muestra a todos los roles, siempre dentro de las incidencias que cada uno puede ver. Ningún requisito pide ocultarlos. | **Aceptada.** S05 v0.6 describe lo que muestra el listado sin la condición ambigua. El código no cambia. |
| Qué datos muestra el tablero | Definido en «Reglas y proceso»: cantidades por estado y por prioridad, críticas no cerradas y porcentaje de cierre. | Ya cubierta. Sin cambios. |
| Cómo se organiza el historial | Definido desde la versión 0.3: orden de registro, desempate por identificador, y en cada evento autor, fecha, estado anterior, estado nuevo y acción. | Ya cubierta. Sin cambios. |
| Filtros por estado y prioridad | Exigidos por RF05 e implementados (`test_p_s05_02_filtros`). | Ya cubierta. |
| Filtros por fecha y por técnico, y búsqueda por número de incidencia | No los exige el enunciado; S05 excluía la búsqueda por texto, pero no nombraba estos filtros. | **Registrada como mejora opcional, no implementada.** S05 v0.6 los nombra en las exclusiones. |

Tampoco expresó una decisión de aprobar o rechazar la SPEC; la tabla «Decisión de revisión» de S05 registra el comentario, no una aprobación.

