# Issues y tablero de GitHub

Textos listos para crear el tablero y los issues en GitHub. Cada issue relaciona requisito, SPEC, criterios y tareas.

> Estado al 2026-10-08: solo existe el issue #1. El tablero y los issues 2 a 8 no se han creado: el asistente no tiene acceso de escritura a GitHub. Las ramas ya están integradas en `main`, así que estos issues sirven ahora para registrar la revisión de cada parte, no para integrar.

## Tablero (GitHub Projects)

1. En el repositorio: **Projects → New project → Board**. Nombre: `ReparaCampus`.
2. Columnas: **Por hacer**, **En progreso**, **En revisión**, **Terminado**.
3. Agrega los ocho issues de abajo y asigna a cada uno su responsable y su revisor.
4. Mueve cada tarjeta a **En revisión** al abrir su pull request y a **Terminado** al integrarlo.

## Issues

En el cuerpo de cada pull request escribe `Closes #N` con el número del issue, para que queden enlazados.

| N.º | Título | Rama del pull request | Responsable | Revisor |
|---|---|---|---|---|
| 1 | SPECS S01 a S05 y diseño: revisión y aprobación | `specs/s01-s05` | Por asignar | Por asignar |
| 2 | Base: esquema, sesión y reglas de dominio | `feat/base` | Por asignar | Por asignar |
| 3 | RF01 · S01 Registrar una incidencia | `feat/s01-registrar` | Por asignar | Por asignar |
| 4 | RF02 · S02 Priorizar y asignar | `feat/s02-priorizar-asignar` | Por asignar | Por asignar |
| 5 | RF03 · S03 Atender una incidencia | `feat/s03-atender` | Por asignar | Por asignar |
| 6 | RF04 · S04 Confirmar, rechazar y reabrir | `feat/s04-validar` | Por asignar | Por asignar |
| 7 | RF05 · S05 Consultar, historizar y tablero | `feat/s05-consultar-historizar` | Por asignar | Por asignar |
| 8 | Evidencias: validación, riesgos, bitácora y PDF | `docs/evidencias` | Por asignar | Por asignar |

### Issue 1 · SPECS S01 a S05 y diseño: revisión y aprobación

```
Requisitos: RF01 a RF05
Artefactos: specs/00-problema-y-alcance.md, specs/S01..S05 (spec, plan, tasks), docs/diseno/

Qué hay que hacer
- [ ] S01 revisada por su revisor asignado, con fecha, versión y decisión
- [ ] S02 revisada
- [ ] S03 revisada
- [ ] S04 revisada
- [ ] S05 revisada
- [ ] Alcance, supuestos y diseño revisados
- [ ] Observaciones incorporadas y SPECS aprobadas como v1.0

Cómo revisar: docs/revision/Formato_revision_SPECS.docx
Terminado cuando: cada SPEC tiene su tabla "Decisión de revisión" llena por una persona distinta del autor.
```

### Issue 2 · Base: esquema, sesión y reglas de dominio

```
Requisitos: límites del prototipo (sesión, hash, persistencia)
SPEC: contratos compartidos de docs/diseno/arquitectura.md
Tareas: T-S01-01, T-S01-02, T-S02-02, T-S03-01, T-S04-01, T-S05-03

Qué hay que comprobar
- [ ] Inicio y cierre de sesión con las cinco cuentas ficticias
- [ ] Contraseñas guardadas con hash
- [ ] No hay selector de rol
- [ ] Tabla de transiciones igual al diagrama de estados
- [ ] python -m pytest tests/test_auth.py pasa (7 pruebas)
```

### Issue 3 · RF01 · S01 Registrar una incidencia

```
Requisito: RF01 · SPEC: S01 · Criterios: AC-S01-01 a 09
Tareas: T-S01-03, T-S01-04, T-S01-05, T-S01-06

Qué hay que comprobar
- [ ] Registro válido crea INC-000001 en REGISTRADA con evento CREAR
- [ ] Descripción de 19 caracteres se rechaza; de 20 se acepta
- [ ] Impacto y riesgo inválidos se rechazan
- [ ] Coordinador y técnico no pueden registrar
- [ ] El texto con HTML se muestra escapado
- [ ] python -m pytest tests/test_s01_registro.py tests/test_concurrencia.py pasa (26 + 5 pruebas)
```

### Issue 4 · RF02 · S02 Priorizar y asignar

```
Requisito: RF02 · SPEC: S02 · Criterios: AC-S02-01 a 09
Tareas: T-S02-01, T-S02-03, T-S02-04, T-S02-05

Qué hay que comprobar
- [ ] Riesgo = CRITICA; sin riesgo y ALTO = ALTA; sin riesgo y BAJO = NORMAL
- [ ] Solo el coordinador asigna, y solo en REGISTRADA
- [ ] Una segunda asignación responde 409 y conserva el técnico
- [ ] Técnico inactivo o inexistente responde 400
- [ ] python -m pytest tests/test_s02_prioridad_asignacion.py pasa
```

### Issue 5 · RF03 · S03 Atender una incidencia

```
Requisito: RF03 · SPEC: S03 · Criterios: AC-S03-01 a 08
Tareas: T-S03-02, T-S03-03, T-S03-04, T-S03-05

Qué hay que comprobar
- [ ] Solo el técnico asignado inicia la atención y registra la solución
- [ ] Otro técnico recibe 404
- [ ] Solución antes de iniciar responde 409
- [ ] Solución de 19 u 801 caracteres se rechaza; de 20 y 800 se acepta
- [ ] python -m pytest tests/test_s03_atencion.py pasa
```

### Issue 6 · RF04 · S04 Confirmar, rechazar y reabrir

```
Requisito: RF04 · SPEC: S04 · Criterios: AC-S04-01 a 10
Tareas: T-S04-02, T-S04-03, T-S04-04, T-S04-05, T-S04-06

Qué hay que comprobar
- [ ] Solo el solicitante dueño confirma, rechaza y reabre
- [ ] El rechazo conserva técnico y solución, y guarda el motivo
- [ ] Reapertura a las 48 h exactas se acepta; un instante después se rechaza
- [ ] El coordinador y el técnico reciben 403
- [ ] python -m pytest tests/test_s04_validacion.py tests/test_integracion.py tests/test_atomicidad.py pasa (43 + 3 + 6)
```

### Issue 7 · RF05 · S05 Consultar, historizar y tablero

```
Requisito: RF05 · SPEC: S05 · Criterios: AC-S05-01 a 13
Tareas: T-S05-01, T-S05-02, T-S05-04, T-S05-05, T-S05-06

Qué hay que comprobar
- [ ] Cada rol ve solo lo que le corresponde, con y sin filtros
- [ ] El historial muestra soluciones, motivos, cierres y reaperturas
- [ ] El historial no se puede editar ni borrar
- [ ] Tablero: vacío 0,0 %; una cerrada de cuatro 25,0 %
- [ ] Los datos permanecen al reiniciar
- [ ] python -m pytest tests/test_s05_consulta_tablero.py pasa (46 pruebas)
```

### Issue 8 · Evidencias: validación, riesgos, bitácora y PDF

```
Partes 2, 3 y 4 del examen y entrega

Qué hay que hacer
- [ ] Resolver docs/decisiones.md: categoría A (autor), B (equipo) y C (docente)
- [ ] Confirmar las decisiones humanas de docs/bitacora-ia.md
- [ ] Confirmar los responsables de docs/riesgos.md
- [ ] Recorrido manual completo en navegador con los cinco usuarios
- [ ] Integrar todos los pull requests y crear el tag release-examen
- [ ] Repetir python -m pytest sobre el tag y registrar el SHA
- [ ] Generar el PDF, abrirlo y revisar secciones, enlaces y legibilidad
- [ ] Cada integrante adjunta el mismo PDF en el aula
```
