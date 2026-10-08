"""Recorrido de extremo a extremo por HTTP contra el servidor real de Flask (no el cliente de pruebas).

Uso: python recorrido_http.py <carpeta del repositorio> <python del entorno> <puerto>
Arranca el servidor, recorre el flujo con los cinco usuarios, lo detiene, lo vuelve a arrancar
y comprueba que los datos siguen ahí.
"""
import http.cookiejar
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO, PY, PUERTO = sys.argv[1], sys.argv[2], sys.argv[3]
BASE = f"http://127.0.0.1:{PUERTO}"
CLAVES = {"solicitante1": "Repara-sol1", "solicitante2": "Repara-sol2", "coordinador1": "Repara-coo1", "tecnico1": "Repara-tec1", "tecnico2": "Repara-tec2"}
resultados = []


def arrancar():
    proceso = subprocess.Popen([PY, "-m", "flask", "--app", "app", "run", "--port", PUERTO], cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen(BASE + "/login", timeout=1)
            return proceso
        except Exception:
            time.sleep(0.25)
    proceso.kill()
    raise SystemExit("el servidor no arrancó")


class Sesion:
    def __init__(self, usuario):
        self.abridor = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        estado, _, _ = self.post("/login", usuario=usuario, clave=CLAVES[usuario])
        assert estado == 200, f"no inició sesión {usuario}"

    def _ir(self, peticion):
        try:
            with self.abridor.open(peticion, timeout=10) as r:
                return r.status, r.geturl(), r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return e.code, e.geturl(), e.read().decode("utf-8")

    def get(self, ruta):
        return self._ir(BASE + ruta)

    def post(self, ruta, **datos):
        return self._ir(urllib.request.Request(BASE + ruta, data=urllib.parse.urlencode(datos).encode("utf-8"), method="POST"))


def comprobar(nombre, condicion, detalle=""):
    resultados.append(bool(condicion))
    print(f"{'OK   ' if condicion else 'FALLA'} {len(resultados):02d}. {nombre}{(' — ' + detalle) if detalle else ''}")


def estado_de(pagina):
    return re.search(r'class="etiqueta estado">(\w+)<', pagina).group(1)


def porcentaje(pagina):
    return re.search(r'id="porcentaje-cierre">([^<]+)<', pagina).group(1)


servidor = arrancar()
try:
    sol1, sol2, coo, tec1, tec2 = (Sesion(u) for u in CLAVES)
    comprobar("Los cinco usuarios inician sesión", True)
    try:
        urllib.request.urlopen(urllib.request.Request(BASE + "/login", data=b"usuario=solicitante1&clave=mala", method="POST"), timeout=10)
        e = 200
    except urllib.error.HTTPError as error:
        e = error.code
    comprobar("Credenciales incorrectas no dan acceso", e == 401, f"respuesta {e}")

    e, url, p = sol1.post("/incidencias/nueva", ubicacion="LAB-01", categoria="ELECTRICIDAD", descripcion="Chispas en el tomacorriente del puesto 4", impacto="ALTO", riesgo_personas="true")
    comprobar("S01 solicitante1 registra; código generado", url.endswith("/incidencias/INC-000001") and estado_de(p) == "REGISTRADA", url.rsplit("/", 1)[-1])
    comprobar("S02 riesgo para personas da prioridad CRITICA", "prioridad-CRITICA" in p)
    e, url, p = sol1.post("/incidencias/nueva", ubicacion="BIB-01", categoria="MOBILIARIO", descripcion="La silla de la mesa 3 tiene una pata rota", impacto="BAJO", riesgo_personas="false")
    comprobar("S02 sin riesgo e impacto BAJO da NORMAL", url.endswith("INC-000002") and "prioridad-NORMAL" in p)
    e, _, _ = sol1.post("/incidencias/nueva", ubicacion="LAB-01", categoria="TIC", descripcion="corta", impacto="BAJO", riesgo_personas="false")
    comprobar("S01 descripción corta se rechaza", e == 400, f"respuesta {e}")
    e, _, _ = coo.post("/incidencias/nueva", ubicacion="LAB-01", categoria="TIC", descripcion="El coordinador intenta registrar un reporte", impacto="BAJO", riesgo_personas="false")
    comprobar("S01 el coordinador no registra", e == 403, f"respuesta {e}")

    e, _, _ = sol2.get("/incidencias/INC-000001")
    comprobar("S05 otro solicitante no ve el reporte ajeno", e == 404, f"respuesta {e}")
    e, _, p = coo.get("/tablero")
    comprobar("S05 tablero con dos abiertas: 0,0 %", e == 200 and porcentaje(p) == "0,0 %", porcentaje(p))
    e, _, _ = sol1.get("/tablero")
    comprobar("S05 el solicitante no ve el tablero", e == 403, f"respuesta {e}")

    _, _, p = coo.get("/incidencias/INC-000001")
    tecnico1_id = re.search(r'<option value="(\d+)">Técnico Uno</option>', p).group(1)
    e, _, _ = sol1.post("/incidencias/INC-000001/asignar", tecnico_id=tecnico1_id)
    comprobar("S02 el solicitante no asigna", e == 403, f"respuesta {e}")
    e, _, p = coo.post("/incidencias/INC-000001/asignar", tecnico_id=tecnico1_id)
    comprobar("S02 el coordinador asigna a Técnico Uno", estado_de(p) == "ASIGNADA" and "Técnico Uno" in p)
    e, _, _ = coo.post("/incidencias/INC-000001/asignar", tecnico_id=tecnico1_id)
    comprobar("S02 no hay reasignación", e == 409, f"respuesta {e}")

    e, _, _ = tec2.get("/incidencias/INC-000001")
    comprobar("S03 el técnico no asignado no la ve", e == 404, f"respuesta {e}")
    e, _, _ = tec1.post("/incidencias/INC-000001/solucion", solucion="Se intenta registrar la solución sin iniciar")
    comprobar("S03 solución antes de iniciar se rechaza", e == 409, f"respuesta {e}")
    e, _, p = tec1.post("/incidencias/INC-000001/iniciar")
    comprobar("S03 el técnico asignado inicia la atención", estado_de(p) == "EN_ATENCION")
    e, _, p = tec1.post("/incidencias/INC-000001/solucion", solucion="Se reemplazó el tomacorriente y se probó con carga")
    comprobar("S03 registra la solución", estado_de(p) == "PENDIENTE_VALIDACION")

    e, _, _ = coo.post("/incidencias/INC-000001/confirmar")
    comprobar("S04 el coordinador no confirma", e == 403, f"respuesta {e}")
    e, _, _ = tec1.post("/incidencias/INC-000001/confirmar")
    comprobar("S04 el técnico no cierra", e == 403, f"respuesta {e}")
    e, _, p = sol1.post("/incidencias/INC-000001/rechazar", motivo="El daño sigue presente")
    comprobar("S04 el dueño rechaza; vuelve a EN_ATENCION con el mismo técnico", estado_de(p) == "EN_ATENCION" and "Técnico Uno" in p and "El daño sigue presente" in p)
    e, _, p = tec1.post("/incidencias/INC-000001/solucion", solucion="Se cambió el cableado del circuito y se midió el voltaje")
    e, _, p = sol1.post("/incidencias/INC-000001/confirmar")
    comprobar("S04 nueva solución y confirmación: CERRADA", estado_de(p) == "CERRADA")
    comprobar("S04 se conservan las dos soluciones", "Se reemplazó el tomacorriente" in p and "Se cambió el cableado" in p)

    _, _, p = coo.get("/tablero")
    comprobar("S05 una cerrada de dos: 50,0 %", porcentaje(p) == "50,0 %", porcentaje(p))
    _, _, p = coo.get("/incidencias/?estado=CERRADA")
    comprobar("S05 filtro por estado", re.findall(r">(INC-\d{6})</a>", p) == ["INC-000001"])
    _, _, p = coo.get("/incidencias/?prioridad=NORMAL")
    comprobar("S05 filtro por prioridad", re.findall(r">(INC-\d{6})</a>", p) == ["INC-000002"])
    e, _, _ = coo.get("/incidencias/?estado=ABIERTA")
    comprobar("S05 filtro inválido se rechaza", e == 400, f"respuesta {e}")

    e, _, p = sol1.post("/incidencias/INC-000001/reabrir", motivo="La falla volvió a aparecer")
    comprobar("S04 el dueño reabre dentro del plazo", estado_de(p) == "EN_ATENCION" and "Técnico Uno" in p)
    comprobar("S05 historial con ocho eventos", p.count("<li>") == 8, f"{p.count('<li>')} eventos")
    _, _, p = coo.get("/tablero")
    comprobar("S05 al reabrir el porcentaje baja a 0,0 %", porcentaje(p) == "0,0 %", porcentaje(p))

    sol2.post("/incidencias/nueva", ubicacion="AULA-201", categoria="TIC", descripcion="<script>alert(1)</script> el proyector no enciende", impacto="BAJO", riesgo_personas="false")
    _, _, p = sol2.get("/incidencias/INC-000003")
    comprobar("El texto con HTML se muestra escapado", "&lt;script&gt;alert(1)&lt;/script&gt;" in p and "<script>alert(1)</script>" not in p)
    _, _, p = sol2.get("/incidencias/")
    comprobar("S05 solicitante2 solo lista las suyas", re.findall(r">(INC-\d{6})</a>", p) == ["INC-000003"])
finally:
    servidor.terminate()
    servidor.wait(timeout=10)

servidor = arrancar()
try:
    _, _, p = Sesion("solicitante1").get("/incidencias/INC-000001")
    comprobar("Tras reiniciar el servidor los datos permanecen", estado_de(p) == "EN_ATENCION" and p.count("<li>") == 8)
finally:
    servidor.terminate()
    servidor.wait(timeout=10)

print(f"\nRESULTADO: {sum(resultados)} de {len(resultados)} comprobaciones correctas")
sys.exit(0 if all(resultados) else 1)
