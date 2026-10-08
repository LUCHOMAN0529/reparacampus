# Ejecución final sobre el tag de entrega

Este registro se agregó a `main` después de crear el tag, porque un commit no puede contener su propio identificador. El commit etiquetado es el que se probó; los commits posteriores solo agregan este registro, la salida de pytest y el documento de entrega, sin tocar `app/` ni `tests/`.

## Versión probada

| Dato | Valor |
|---|---|
| Repositorio | <https://github.com/LUCHOMAN0529/reparacampus> |
| Tag | `release-examen` |
| SHA exacto | `b59faa1128708c5cc405d0b315c0226c610c5489` |
| Rama | `main`, sin cambios sin confirmar al ejecutar |
| Fecha y hora | 2026-10-08, de 02:57:23 a 02:58:06 (UTC−05:00) |
| Entorno | Microsoft Windows 11 Home Single Language 10.0.26300 · Python 3.14.3 · Flask 3.1.3 · Werkzeug 3.1.9 · Jinja2 3.1.6 · SQLite 3.50.4 · pytest 9.1.1 |
| Quién ejecutó | El asistente de IA (Claude Code), por instrucción del autor |

## Resultados

| N.º | Comando | Aprobadas | Fallidas | Salida completa |
|---|---|---|---|---|
| 1 | `python -m pytest` | 176 | 0 | [ejecucion/pytest.txt](ejecucion/pytest.txt) |
| 2 | `python -m pytest -m integracion -v` | 3 (173 no seleccionadas) | 0 | [ejecucion/pytest-integracion.txt](ejecucion/pytest-integracion.txt) |
| 3 | `python -m pytest -v` | 176 | 0 | [ejecucion/pytest-v.txt](ejecucion/pytest-v.txt) |

El comando 2 se ejecutó con `-v` para que la salida nombre las tres pruebas. A los tres comandos se les añadió `-p no:cacheprovider`, que solo evita crear la carpeta de caché de pytest.

## Pruebas de integración contra SQLite real

| Prueba | Recorrido | Resultado |
|---|---|---|
| `test_p_s04_01_flujo_de_cierre` | Registrar → asignar → iniciar → proponer → confirmar | Aprobada |
| `test_p_s04_02_rechazo_y_nueva_solucion` | … → proponer → rechazar → nueva solución → confirmar | Aprobada |
| `test_p_s04_03_reapertura_y_nuevo_cierre` | Cierre → reapertura a las 48 h exactas → nueva solución → nuevo cierre → reapertura rechazada a 48 h + 1 µs | Aprobada |

## Qué cubre esta ejecución

| Comprobación pedida | Pruebas que la cubren (todas aprobadas) |
|---|---|
| Límite exacto de 48 horas y caso fuera de plazo | `test_reabrir_exactamente_a_las_48_horas`, `test_reabrir_un_instante_despues_de_48_horas`, `test_p_s04_03_reapertura_y_nuevo_cierre` |
| Permisos por rol y pertenencia | `test_p_s01_04_otros_roles_no_registran`, `test_p_s02_04_otros_roles_no_asignan`, `test_p_s03_03_tecnico_no_asignado`, `test_p_s04_05_solo_el_duenio_valida`, `test_p_s05_01_detalle_segun_permisos` |
| Persistencia tras reinicio | `test_p_s05_05_los_datos_permanecen_al_reiniciar` |
| Efectos de operaciones rechazadas | `test_las_operaciones_rechazadas_no_dejan_rastro`, `test_un_fallo_al_guardar_el_evento_revierte_toda_la_operacion` |
| Métricas del tablero | `test_p_s05_03_tablero_vacio`, `test_p_s05_03_porcentaje_de_cierre_y_reapertura`, `test_tablero_cantidades_y_criticas`, `test_formato_y_redondeo_del_porcentaje` |
| Texto con HTML | `test_p_s01_05_el_texto_no_se_ejecuta_como_html`, `test_la_solucion_no_se_ejecuta_como_html`, `test_el_listado_no_ejecuta_html` |
| Contraseñas con hash y acceso con cuentas | `tests/test_auth.py` (7 pruebas) |

## Otras comprobaciones sobre la versión integrada

Hechas el mismo día sobre el commit `256605a`, anterior al tag. Entre ese commit y el tag solo cambian documentos; `app/` y `tests/` son idénticos.

| Comprobación | Resultado |
|---|---|
| Copia limpia (`git clone`, entorno virtual nuevo, `pip install -r requirements.txt`, `python -m pytest`) | 176 aprobadas, 0 fallidas |
| Recorrido de extremo a extremo por HTTP contra el servidor real, con [`recorrido_http.py`](recorrido_http.py) | 32 de 32 comprobaciones correctas |

## Lo que esta ejecución no demuestra

- No hay revisión de otro integrante ni recorrido en navegador hecho por una persona.
- La prueba de concurrencia usa ocho hilos en un mismo proceso contra SQLite; no es una prueba de carga.
- Se ejecutó en un solo equipo y sistema operativo.
