# Comentarios de los integrantes sobre las SPECS

Cada integrante leyó la parte del documento de entrega que le correspondía y respondió la [encuesta de revisión](Encuesta_revision_integrantes.docx). Las respuestas se copian **tal como las escribió cada persona**, sin corregirlas. Después de cada una se indica qué se hizo con ella.

Los comentarios llegaron después de que el código estuviera escrito e integrado, así que no cuentan como revisión previa a la implementación.

## Decisiones al cierre

Al final del 2026-10-13, poco antes del cierre de la entrega, el autor pidió a cada integrante una decisión explícita sobre su parte. Las respuestas llegaron por WhatsApp y el autor las transmitió; no hay captura en el repositorio.

| Integrante | Parte | Decisión | Nota |
|---|---|---|---|
| Rafael Eduardo May Recuero | S01 v0.6 | Aprobada | Indicó que aprueba por el tiempo disponible |
| Jean Marco Oyola De Martino | S02 v0.6 | Aprobada | Respondió lo mismo que Rafael, según el autor |
| José Leonardo Hernández Pedrosa | S03 v0.6 | Aprobada | Respondió lo mismo que Rafael, según el autor |
| Cristian David Diaz España | S04 v0.5 | Aprobada | Respondió lo mismo que Rafael, según el autor |
| Jorge Luis González Arroyo | S05 v0.6 | Aprobada | Respondió después de los demás |

Son aprobaciones dadas al cierre y bajo presión de tiempo, después de la integración. Se registran tal como llegaron, sin presentarlas como una revisión previa.

| Integrante | Parte | Recibido | Estado |
|---|---|---|---|
| Rafael Eduardo May Recuero | S01 Registrar | 2026-10-13, entregado al autor | Recibido |
| Jean Marco Oyola De Martino | S02 Priorizar y asignar | 2026-10-13, entregado al autor | Recibido |
| José Leonardo Hernández Pedrosa | S03 Atender | 2026-10-13, entregado al autor | Recibido |
| Cristian David Diaz España | S04 Validar | 2026-10-13, entregado al autor | Recibido |
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

## Cristian David Diaz España · S04 Confirmar, rechazar y reabrir

Recibido el 2026-10-13. El integrante declara que usó ChatGPT como apoyo.

**1. Con tus palabras: ¿qué hace esta parte del sistema?**

> Esta parte permite gestionar la decisión final sobre una incidencia, confirmando si fue resuelta o rechazándola si la solución no fue satisfactoria. También permite reabrir una incidencia cuando el problema continúa o vuelve a presentarse.

**2. ¿Hay algo que no se entienda o que te parezca mal definido? ¿Qué?**

> Sería importante aclarar quién tiene permiso para confirmar, rechazar o reabrir una incidencia y qué condiciones deben cumplirse en cada caso. También debería definirse qué sucede con el estado de la incidencia y si es obligatorio justificar un rechazo o una reapertura.

**3. ¿Cambiarías o agregarías algo? ¿Qué y por qué?**

> Agregaría un campo para registrar el motivo del rechazo o de la reapertura, además de guardar la fecha y el usuario que realizó cada acción. Esto permitiría llevar un mejor seguimiento de las incidencias y mantener un historial de los cambios realizados.

**4. ¿Usaste IA para revisarla? Si sí: ¿cuál, y con qué parte de su respuesta estás de acuerdo y con cuál no?**

> Sí, utilicé ChatGPT como apoyo para revisar la funcionalidad e identificar posibles mejoras. Estoy de acuerdo con la recomendación de definir mejor los permisos, las condiciones de cada acción y el registro de los cambios. Sin embargo, estas sugerencias deben contrastarse con la documentación del proyecto antes de afirmar que son problemas reales del módulo.

### Qué se hizo con cada observación

Siguiendo su propia indicación de contrastar las sugerencias con la documentación, las cinco se compararon con S04 y con el código. Las cinco ya estaban definidas e implementadas, así que no hubo cambios.

| Observación | Dónde está definido | Prueba aprobada | Acción |
|---|---|---|---|
| Quién puede confirmar, rechazar o reabrir | S04, «Precondiciones y permisos»: solo el solicitante dueño; el coordinador y el técnico reciben 403; otro solicitante, 404 (AC-S04-04) | `test_p_s04_05_solo_el_duenio_valida`, `test_solo_el_duenio_reabre` | Ya cubierta |
| Qué condiciones deben cumplirse | Confirmar y rechazar exigen `PENDIENTE_VALIDACION`; reabrir exige `CERRADA` y un máximo de 48 horas desde el último cierre (AC-S04-05 a 07) | `test_validar_en_estado_incompatible`, `test_reabrir_exactamente_a_las_48_horas`, `test_reabrir_un_instante_despues_de_48_horas` | Ya cubierta |
| Qué pasa con el estado | Confirmar pasa a `CERRADA`; rechazar y reabrir vuelven a `EN_ATENCION` con el mismo técnico (tabla de salidas de S04 y diagrama de estados) | `test_p_s04_01_flujo_de_cierre`, `test_rechazar_conserva_tecnico_y_solucion` | Ya cubierta |
| Si es obligatorio justificar el rechazo o la reapertura | Sí: motivo obligatorio de 10 a 300 caracteres en ambos casos (AC-S04-03 y AC-S04-08) | `test_p_s04_04_limites_del_motivo_de_rechazo`, `test_motivo_de_reapertura_invalido`, `test_p_s04_15_rechazo_con_motivo_solo_de_espacios` | Ya cubierta |
| Registrar motivo, fecha y usuario de cada acción | Cada rechazo y reapertura guarda un evento con motivo, actor y fecha del servidor; el historial no se puede editar (AC-S04-02, AC-S05-04 y 05) | `test_rechazar_conserva_tecnico_y_solucion`, `test_historial_completo`, `test_p_s05_04_el_historial_es_inmutable` | Ya cubierta |

El integrante no expresó una decisión de aprobar o rechazar la SPEC; la tabla «Decisión de revisión» de S04 registra el comentario, no una aprobación.

## Jean Marco Oyola De Martino · S02 Priorizar y asignar

Recibido el 2026-10-13. El integrante declara que usó ChatGPT como apoyo.

**1. Con tus palabras: ¿Qué hace esta parte del sistema?**

> Esta parte permite que el coordinador revise las incidencias registradas, determine su prioridad y asigne un técnico para que se encargue de resolverlas. Así se organiza mejor el trabajo y se puede atender cada problema según su importancia.

**2. ¿Hay algo que no se entienda o que te parezca mal definido? ¿Qué?**

> Me parece que sería importante dejar más claros los criterios que se utilizan para definir la prioridad de una incidencia y cómo se decide qué técnico debe atenderla. También sería bueno especificar qué pasa si no hay técnicos disponibles para recibir una asignación.

**3. ¿Cambiarías o agregarías algo? ¿Qué y por qué?**

> Agregaría una explicación más clara de los niveles de prioridad y una validación que permita comprobar la disponibilidad del técnico antes de asignarle una incidencia. Esto ayudaría a distribuir mejor el trabajo y evitaría asignaciones que después tengan que modificarse.

**4. ¿Usaste IA para revisarla? Si sí: ¿cuál, y con qué parte de su respuesta estás de acuerdo y con cuál no?**

> Sí, utilicé ChatGPT para apoyarme en la revisión de esta parte del sistema. Coincido en que es necesario organizar las incidencias según su prioridad y asignarlas correctamente a los técnicos. Como punto a tener en cuenta, las recomendaciones de la IA deben revisarse y compararse con el código del proyecto para comprobar que realmente se ajusten a lo que está desarrollado.

### Qué se hizo con cada observación

| Observación | Contraste con el enunciado y el código | Acción |
|---|---|---|
| Que el coordinador «determine» la prioridad (respuesta 1) | Según RF02, el coordinador no elige la prioridad: la calcula el sistema a partir del riesgo y el impacto, y nadie puede cambiarla (AC-S02-09, `test_la_prioridad_no_se_cambia_al_asignar`). | Sin cambios. Se anota porque la respuesta describe el funcionamiento de otra forma. |
| Criterios y niveles de prioridad | Definidos en la tabla de prioridad de S02: con riesgo, `CRITICA`; sin riesgo e impacto `ALTO`, `ALTA`; sin riesgo e impacto `BAJO`, `NORMAL` (AC-S02-01 a 03, `test_p_s02_01_prioridad_calculada`). | Ya cubierta. |
| Cómo se decide qué técnico atiende | El enunciado no pone restricción de especialidad. En el código, el coordinador elige libremente entre los técnicos activos; el sistema no recomienda ni reparte. S02 lo daba a entender en las exclusiones, pero no lo decía. | **Aceptada como aclaración.** S02 v0.6 lo dice de forma explícita. |
| Qué pasa si no hay técnicos disponibles | No estaba dicho. En el código, si no hay técnicos activos la lista de selección queda vacía, cualquier intento de asignar responde 400 y la incidencia sigue `REGISTRADA` (mismo comportamiento probado en AC-S02-07 con `test_p_s02_05_tecnico_invalido`). | **Aceptada como aclaración.** S02 v0.6 lo dice. No cambia el código. |
| Validar la disponibilidad del técnico antes de asignar | El sistema ya valida que el técnico exista, tenga rol técnico y esté activo (AC-S02-07). Medir su carga de trabajo no lo pide el enunciado y S02 excluía el balanceo de carga. | Lo primero ya está cubierto. La validación por carga de trabajo queda **registrada como mejora opcional, no implementada**. |
| Evitar asignaciones que después haya que modificar | No existe la reasignación: una asignación no se puede cambiar (AC-S02-06, `test_p_s02_03_asignacion_repetida`). | Ya cubierta. |

El integrante no expresó una decisión de aprobar o rechazar la SPEC; la tabla «Decisión de revisión» de S02 registra el comentario, no una aprobación.

## Rafael Eduardo May Recuero · S01 Registrar una incidencia

Recibido el 2026-10-13. El integrante declara que usó Claude como apoyo.

**1. Con tus palabras: ¿Qué hace esta parte del sistema?**

Es la puerta de entrada para cualquier usuario que tenga un inconveniente en las instalaciones. Su función principal es permitir que la persona reporte el problema llenando un formulario básico con la ubicación y una descripción, asegurando que la queja quede guardada en el sistema para que luego le puedan hacer seguimiento.

**2. ¿Hay algo que no se entienda o que te parezca mal definido? ¿Qué?**

Me da la impresión de que no queda del todo claro cómo se clasifican las categorías de los daños. A veces los usuarios no saben exactamente en qué categoría encasillar su problema, y la guía tampoco especifica muy bien qué pasa con los campos opcionales.

**3. ¿Cambiarías o agregarías algo? ¿Qué y por qué?**

Le añadiría una sección obligatoria para subir fotos o capturas del daño de forma rápida. Una imagen ayuda muchísimo más que mil palabras para que el equipo de soporte entienda el problema de entrada sin tener que adivinar.

**4. ¿Usaste IA para revisarla? Si sí: ¿cuál, y con qué parte de su respuesta estás de acuerdo y con cuál no?**

Sí, le pedí una opinión a Claude sobre esta sección. Coincido totalmente en que el flujo del formulario es directo, pero no estuve de acuerdo cuando sugirió agregar validaciones de campos tan estrictas que harían que reportar una emergencia se vuelva un trámite tardado y molesto para el usuario.

### Qué se hizo con cada observación

| Observación | Contraste con el enunciado y el código | Acción |
|---|---|---|
| No queda claro cómo se clasifican las categorías | El enunciado fija las cuatro categorías (`ELECTRICIDAD`, `HIDRAULICA`, `MOBILIARIO`, `TIC`) pero no define qué daños abarca cada una. S01 tampoco lo decía. | **Aceptada como aclaración.** S01 v0.6 dice que el caso no define su alcance, que el solicitante elige la más cercana y que el sistema no la corrige. Una ayuda por categoría en el formulario queda como mejora opcional, no implementada. |
| Qué pasa con los campos opcionales | No hay campos opcionales: RF01 hace obligatorios los cinco, y la tabla de entradas de S01 ya lo indicaba campo por campo. | **Aceptada como aclaración.** S01 v0.6 lo dice en una frase, además de la tabla. |
| Agregar fotos obligatorias del daño | El enunciado lo excluye de forma expresa: «No se requieren adjuntos». S01 ya listaba los adjuntos en las exclusiones. | **No se aplica:** está fuera del alcance definido por el enunciado. Se registra como posible mejora para una versión posterior. |
| Desacuerdo con validaciones «tan estrictas» (sobre la sugerencia de su asistente de IA) | Las validaciones del registro no son una elección del equipo: RF01 exige los cinco campos, los valores del catálogo y una descripción de 20 a 500 caracteres. El formulario no agrega validaciones más allá de esas. | Sin cambios. Se registra su desacuerdo, que coincide con lo implementado: no se añadieron validaciones adicionales. |

El integrante no expresó una decisión de aprobar o rechazar la SPEC; la tabla «Decisión de revisión» de S01 registra el comentario, no una aprobación. También figuraba como revisor propuesto del alcance y del diseño; su comentario solo trata S01, así que esas dos revisiones siguen pendientes.
