# Entrega reproducible

## Repositorio y versión evaluada

| Dato | Valor |
|---|---|
| Repositorio | <{{REPO}}> |
| Acceso | Público |
| Tag | {{TAG}} |
| SHA exacto | {{SHA}} |
| Resultado de las pruebas sobre ese SHA | {{PRUEBAS}} |

## Instalación desde una copia limpia

En Windows (PowerShell):

```
git clone {{REPO}}.git
cd reparacampus
git checkout release-examen
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

En Linux o macOS la activación es `source .venv/bin/activate`.

## Arranque y seed

```
flask --app app run
```

Se abre en <http://127.0.0.1:5000>. En el primer arranque la aplicación crea `instance/reparacampus.sqlite` con el esquema y las cinco cuentas ficticias. Los datos permanecen al reiniciar. `flask --app app init-db` crea la base sin arrancar el servidor y no borra datos existentes.

## Cuentas ficticias

| Usuario | Contraseña | Rol |
|---|---|---|
| `solicitante1` | `Repara-sol1` | Solicitante |
| `solicitante2` | `Repara-sol2` | Solicitante |
| `coordinador1` | `Repara-coo1` | Coordinador |
| `tecnico1` | `Repara-tec1` | Técnico |
| `tecnico2` | `Repara-tec2` | Técnico |

## Comandos de pruebas

```
python -m pytest
python -m pytest -m integracion
python -m pytest -v
```

El primero ejecuta la batería completa; el segundo, solo las tres pruebas de integración; el tercero muestra el resultado prueba por prueba.

## Limitaciones conocidas

- Las tres preguntas al cliente (Q1 a Q3) no tienen respuesta; el prototipo aplica los supuestos declarados en la sección 3.
- Los formularios no llevan token CSRF. La cookie de sesión usa `SameSite=Lax` y las operaciones que cambian datos exigen `POST`.
- El servidor de desarrollo de Flask no es apto para producción; el caso no pide hosting.
- No hay gestión de usuarios: las cuentas se crean solo con el seed.
- Sin paginación ni búsqueda por texto en el listado.
- Las fechas se muestran en UTC.

El README del repositorio conserva el procedimiento completo.
