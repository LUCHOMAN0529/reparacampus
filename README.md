# ReparaCampus

Prototipo para gestionar incidencias de infraestructura de la Universidad Simón Bolívar.
Segundo examen práctico de Ingeniería de Software I: *Spec-Driven Development con IA*.

> Todos los datos y cuentas de este repositorio son ficticios.

El repositorio sigue el hilo **Requisito → Historia → SPEC → Código → Prueba**.

| Qué | Dónde |
|---|---|
| Problema, alcance, preguntas y supuestos | [`specs/00-problema-y-alcance.md`](specs/00-problema-y-alcance.md) |
| SPECS S01–S05 (especificación, plan y tareas) | [`specs/`](specs/) |
| Diseño: componentes, datos, UML y decisión | [`docs/diseno/`](docs/diseno/arquitectura.md) |
| Revisiones | [`docs/revision/`](docs/revision/) |
| Aplicación | [`app/`](app/) |
| Pruebas automatizadas | [`tests/`](tests/) |

## Versiones

| Componente | Versión usada |
|---|---|
| Python | 3.14.3 |
| Flask | 3.1.3 (Werkzeug 3.1.9, Jinja2 3.1.6) |
| SQLite | 3.50.4 (módulo `sqlite3` de la biblioteca estándar) |
| pytest | 9.1.1 |

Las dependencias instalables están fijadas en [`requirements.txt`](requirements.txt).

## Instalación desde una copia limpia

En Windows (PowerShell):

```powershell
git clone https://github.com/LUCHOMAN0529/reparacampus.git
cd reparacampus
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

En Linux o macOS cambia la activación por `source .venv/bin/activate`.

## Arranque

```powershell
flask --app app run
```

Abre <http://127.0.0.1:5000>. En el primer arranque la aplicación crea `instance/reparacampus.sqlite` con el esquema de [`app/schema.sql`](app/schema.sql) y las cinco cuentas ficticias. Los datos permanecen al reiniciar.

Para crear la base sin arrancar el servidor: `flask --app app init-db`. El comando no borra datos existentes.
Para empezar de cero, detén el servidor y elimina `instance/reparacampus.sqlite`.

La clave de sesión no está en el repositorio: se toma de la variable `REPARACAMPUS_SECRET_KEY` o se genera en `instance/secret_key`.

## Cuentas ficticias (seed)

| Usuario | Contraseña | Rol |
|---|---|---|
| `solicitante1` | `Repara-sol1` | Solicitante |
| `solicitante2` | `Repara-sol2` | Solicitante |
| `coordinador1` | `Repara-coo1` | Coordinador |
| `tecnico1` | `Repara-tec1` | Técnico |
| `tecnico2` | `Repara-tec2` | Técnico |

Las contraseñas se guardan con hash (`scrypt` de Werkzeug). No hay selector de rol: el rol pertenece a la cuenta.

## Recorrido de prueba manual

1. `solicitante1` registra una incidencia en **Nueva incidencia**.
2. `coordinador1` la abre desde **Incidencias** y le asigna un técnico.
3. `tecnico1` inicia la atención y registra la solución.
4. `solicitante1` la confirma o la rechaza con un motivo. Una incidencia cerrada puede reabrirse durante 48 horas.
5. `coordinador1` consulta el **Tablero**.

## Pruebas

```powershell
python -m pytest
```

Cada prueba crea su propio archivo SQLite temporal, independiente de la base de desarrollo, y usa un reloj controlado en lugar del reloj del sistema.

| Archivo | SPEC | Pruebas |
|---|---|---|
| `tests/test_auth.py` | Autenticación | 7 |
| `tests/test_s01_registro.py` | S01 | 20 |
| `tests/test_s02_prioridad_asignacion.py` | S02 | 18 |
| `tests/test_s03_atencion.py` | S03 | 17 |
| `tests/test_s04_validacion.py` | S04 | 37 |
| `tests/test_integracion.py` | S04 (integración: cierre, rechazo y reapertura) | 3 |
| `tests/test_s05_consulta_tablero.py` | S05 | 46 |
| **Total** | | **148** |

Solo las de integración: `python -m pytest -m integracion`. Detalle por prueba: `python -m pytest -v`.

Los casos parametrizados se cuentan por separado. Cada prueba indica en su comentario el identificador de prueba y los criterios de aceptación que cubre.

## Estructura

```
app/
  __init__.py     Fábrica de la aplicación
  auth.py         Inicio y cierre de sesión; decoradores de sesión y rol
  rutas.py        Entrada HTTP
  dominio.py      Reglas puras: validación, prioridad, transiciones, plazo, porcentaje
  servicios.py    Operaciones que cambian datos, cada una en una transacción
  consultas.py    Lecturas con la visibilidad por rol
  reloj.py        Hora del servidor en UTC
  db.py           Conexión, esquema y seed
  schema.sql      Tablas, restricciones y disparadores de inmutabilidad
  templates/      Plantillas Jinja
  static/         CSS y JavaScript
tests/            Pruebas con pytest y el cliente de pruebas de Flask
specs/            Especificaciones, planes y tareas
docs/             Diseño y revisiones
```

## Limitaciones conocidas

- Las tres preguntas al cliente (Q1 a Q3) no tienen respuesta; el prototipo aplica los supuestos de `specs/00-problema-y-alcance.md`.
- Los formularios no llevan token CSRF. La cookie de sesión usa `SameSite=Lax` y todas las operaciones que cambian datos exigen `POST`.
- El servidor de desarrollo de Flask no es apto para producción; el caso no pide hosting.
- No hay gestión de usuarios: las cuentas se crean solo con el seed.
- Sin paginación ni búsqueda por texto en el listado.
- Las fechas se muestran en UTC.

## Equipo

- Rafael Eduardo May Recuero
- Jean Marco Oyola De Martino
- José Leonardo Hernández Pedrosa
- Cristian David Diaz España
- Jorge Luis González Arroyo
- Luis Carlo Daza Ospino
