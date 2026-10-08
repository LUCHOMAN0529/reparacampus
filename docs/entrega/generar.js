// Arma el documento de entrega (.docx) a partir de los Markdown del repositorio.
// Uso: node docs/entrega/generar.js <salida.docx>   (requiere el paquete npm "docx")
// Los datos que aún no existen se leen de docs/entrega/datos.json; si faltan, quedan marcados como PENDIENTE.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  HeadingLevel, AlignmentType, BorderStyle, PageBreak, LevelFormat, ExternalHyperlink, Footer,
  PageNumber, PageOrientation, TableOfContents, ImageRun, VerticalAlign,
} = require("docx");

const RAIZ = path.resolve(__dirname, "..", "..");
const datos = JSON.parse(fs.readFileSync(path.join(__dirname, "datos.json"), "utf8"));
const dato = (clave) => (datos[clave] && String(datos[clave]).trim()) || `[PENDIENTE: ${clave}]`;
const REPO = datos.REPO;

const A4 = { ancho: 11906, alto: 16838, margen: 1417 }; // márgenes de 2,5 cm
const ANCHO = { vertical: A4.ancho - 2 * A4.margen, horizontal: A4.alto - 2 * A4.margen };
const FUENTE = "Calibri";
const CUERPO = 22; // 11 pt
const TABLA = 18; // 9 pt
const INTERLINEADO = 276; // 1,15
const borde = { style: BorderStyle.SINGLE, size: 4, color: "9AA3AF" };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };

const FIGURAS = {
  componentes: "Componentes del sistema",
  datos: "Modelo de datos",
  estados: "Diagrama UML de estados de una incidencia",
  "secuencia-rechazo": "Diagrama UML de secuencia del rechazo de una solución",
};

let nTabla = 0;
let nFigura = 0;
let nLista = 0;
const contadores = [2, 0, 0]; // 1 = portada, 2 = índice
let ultimoTitulo = "";
const tablasPorTitulo = {};

// ---------- texto en línea ----------
function enlace(href, archivo) {
  if (/^https?:/.test(href)) return href;
  if (href.startsWith("#")) return null;
  const destino = path.posix.normalize(path.posix.join(path.posix.dirname(archivo), href));
  return `${REPO}/blob/main/${destino}`;
}

function enLinea(texto, archivo, base = {}) {
  const partes = texto.split(
    /(\[PENDIENTE:[^\]]*\]|\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|<https?:[^>]+>|\*[^*\s][^*]*\*)/
  );
  const salida = [];
  for (const parte of partes) {
    if (!parte) continue;
    let m;
    if (parte.startsWith("[PENDIENTE:")) {
      salida.push(new TextRun({ ...base, text: parte, bold: true, color: "B00020" }));
    } else if ((m = parte.match(/^\*\*([^*]+)\*\*$/))) {
      salida.push(...enLinea(m[1], archivo, { ...base, bold: true }));
    } else if ((m = parte.match(/^`([^`]+)`$/))) {
      salida.push(new TextRun({ ...base, text: m[1], font: "Consolas", size: (base.size || CUERPO) - 2 }));
    } else if ((m = parte.match(/^\[([^\]]+)\]\(([^)]+)\)$/))) {
      const url = enlace(m[2], archivo);
      const etiqueta = m[1].replace(/`/g, "");
      if (url) salida.push(new ExternalHyperlink({ link: url, children: [new TextRun({ ...base, text: etiqueta, style: "Hyperlink" })] }));
      else salida.push(new TextRun({ ...base, text: etiqueta }));
    } else if ((m = parte.match(/^<(https?:[^>]+)>$/))) {
      salida.push(new ExternalHyperlink({ link: m[1], children: [new TextRun({ ...base, text: m[1], style: "Hyperlink" })] }));
    } else if ((m = parte.match(/^\*([^*]+)\*$/))) {
      salida.push(new TextRun({ ...base, text: m[1], italics: true }));
    } else {
      salida.push(new TextRun({ ...base, text: parte }));
    }
  }
  return salida;
}

const plano = (t) => t.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/[`*]/g, "");

// ---------- bloques ----------
function parrafo(texto, archivo, opciones = {}) {
  return new Paragraph({
    spacing: { after: 120, line: INTERLINEADO },
    ...opciones.par,
    children: enLinea(texto, archivo, opciones.run),
  });
}

function titulo(texto, nivel) {
  let numero = "";
  if (nivel <= 3) {
    contadores[nivel - 1] += 1;
    for (let i = nivel; i < 3; i++) contadores[i] = 0;
    numero = contadores.slice(0, nivel).join(".") + (nivel === 1 ? ". " : " ");
  }
  ultimoTitulo = plano(texto).replace(/^\d+(\.\d+)*\.?\s+/, ""); // los Markdown ya traen su propio número
  const estilos = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4];
  return new Paragraph({
    heading: estilos[Math.min(nivel, 4) - 1],
    keepNext: true,
    spacing: { before: nivel === 1 ? 0 : 240, after: 120 },
    children: [new TextRun(numero + ultimoTitulo)],
  });
}

function anchosDeColumnas(filas, ancho) {
  const columnas = Math.max(...filas.map((f) => f.length));
  const pesos = [];
  for (let c = 0; c < columnas; c++) {
    const largo = Math.max(...filas.map((f) => plano(f[c] || "").length));
    pesos.push(Math.min(Math.max(largo, 10), 48));
  }
  const total = pesos.reduce((a, b) => a + b, 0);
  const anchos = pesos.map((p) => Math.floor((p / total) * ancho));
  anchos[anchos.length - 1] += ancho - anchos.reduce((a, b) => a + b, 0);
  return anchos;
}

function tabla(filas, archivo, ancho) {
  const anchos = anchosDeColumnas(filas, ancho);
  nTabla += 1;
  tablasPorTitulo[ultimoTitulo] = (tablasPorTitulo[ultimoTitulo] || 0) + 1;
  const sufijo = tablasPorTitulo[ultimoTitulo] > 1 ? ` (${tablasPorTitulo[ultimoTitulo]})` : "";
  const rotulo = new Paragraph({
    keepNext: true,
    spacing: { before: 120, after: 60 },
    children: [
      new TextRun({ text: `Tabla ${nTabla}. `, bold: true, size: 20 }),
      new TextRun({ text: ultimoTitulo + sufijo, italics: true, size: 20 }),
    ],
  });
  const cuerpo = new Table({
    width: { size: ancho, type: WidthType.DXA },
    columnWidths: anchos,
    rows: filas.map(
      (fila, i) =>
        new TableRow({
          tableHeader: i === 0,
          cantSplit: true,
          children: anchos.map(
            (w, c) =>
              new TableCell({
                width: { size: w, type: WidthType.DXA },
                borders: bordes,
                verticalAlign: VerticalAlign.TOP,
                shading: i === 0 ? { type: ShadingType.CLEAR, fill: "E7EBF0", color: "auto" } : undefined,
                margins: { top: 50, bottom: 50, left: 80, right: 80 },
                children: [new Paragraph({ children: enLinea(fila[c] || "", archivo, { size: TABLA, bold: i === 0 }) })],
              })
          ),
        })
    ),
  });
  return [rotulo, cuerpo, new Paragraph({ spacing: { after: 80 }, children: [] })];
}

function figura(nombre, vertical) {
  const ruta = path.join(RAIZ, "docs", "diseno", "img", `${nombre}.png`);
  const png = fs.readFileSync(ruta);
  const w = png.readUInt32BE(16);
  const h = png.readUInt32BE(20);
  const maxW = vertical ? 600 : 930;
  const maxH = vertical ? 800 : 480;
  const escala = Math.min(maxW / w, maxH / h);
  nFigura += 1;
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      keepNext: true,
      spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data: png, transformation: { width: Math.round(w * escala), height: Math.round(h * escala) } })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 160 },
      children: [
        new TextRun({ text: `Figura ${nFigura}. `, bold: true, size: 20 }),
        new TextRun({ text: FIGURAS[nombre] + ". Fuente: docs/diseno/" + nombre + ".puml", italics: true, size: 20 }),
      ],
    }),
  ];
}

// ---------- Markdown ----------
function convertir({ ruta, base, sinH1, imagenes }, vertical) {
  const ancho = vertical ? ANCHO.vertical : ANCHO.horizontal;
  let texto = fs.readFileSync(path.join(RAIZ, ruta), "utf8").replace(/\r\n/g, "\n");
  texto = texto.replace(/\{\{(\w+)\}\}/g, (_, clave) => dato(clave));
  const lineas = texto.split("\n");
  const bloques = [];
  let i = 0;
  while (i < lineas.length) {
    const linea = lineas[i];
    let m;
    if (!linea.trim() || /^---+$/.test(linea.trim())) { i++; continue; }
    if ((m = linea.match(/^(#{1,4})\s+(.*)$/))) {
      const n = m[1].length;
      if (!(sinH1 && n === 1)) bloques.push(titulo(m[2], base + n - 1));
      i++; continue;
    }
    if (linea.startsWith("```")) {
      i++;
      while (i < lineas.length && !lineas[i].startsWith("```")) {
        bloques.push(new Paragraph({
          shading: { type: ShadingType.CLEAR, fill: "F1F3F5", color: "auto" },
          spacing: { after: 0 },
          indent: { left: 200 },
          children: [new TextRun({ text: lineas[i] || " ", font: "Consolas", size: 18 })],
        }));
        i++;
      }
      i++;
      bloques.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      continue;
    }
    if (linea.startsWith("|")) {
      const filas = [];
      while (i < lineas.length && lineas[i].startsWith("|")) {
        const celdas = lineas[i].trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
        if (!celdas.every((c) => /^:?-+:?$/.test(c))) filas.push(celdas);
        i++;
      }
      bloques.push(...tabla(filas, ruta, ancho));
      continue;
    }
    if ((m = linea.match(/^(\s*)([-*]|\d+\.)\s+(.*)$/))) {
      nLista += 1;
      const ordenada = /\d/.test(m[2]);
      while (i < lineas.length && (m = lineas[i].match(/^(\s*)([-*]|\d+\.)\s+(.*)$/))) {
        let contenido = m[3];
        i++;
        while (i < lineas.length && /^\s{2,}\S/.test(lineas[i]) && !/^\s*([-*]|\d+\.)\s/.test(lineas[i])) contenido += " " + lineas[i++].trim();
        bloques.push(new Paragraph({
          numbering: { reference: ordenada ? "numeros" : "vinetas", level: 0, instance: nLista },
          spacing: { after: 60, line: INTERLINEADO },
          children: enLinea(contenido, ruta),
        }));
      }
      continue;
    }
    if (linea.startsWith(">")) {
      let cita = "";
      while (i < lineas.length && lineas[i].startsWith(">")) cita += " " + lineas[i++].replace(/^>\s?/, "");
      bloques.push(parrafo(cita.trim(), ruta, { par: { indent: { left: 400 }, border: { left: { style: BorderStyle.SINGLE, size: 12, color: "9AA3AF", space: 8 } } }, run: { italics: true } }));
      continue;
    }
    let par = linea;
    i++;
    while (i < lineas.length && lineas[i].trim() && !/^(#{1,4}\s|\||```|>|\s*([-*]|\d+\.)\s|---+$)/.test(lineas[i])) par += " " + lineas[i++].trim();
    bloques.push(parrafo(par, ruta));
    if (imagenes && (m = par.match(/\]\(([\w-]+)\.puml\)/)) && FIGURAS[m[1]]) bloques.push(...figura(m[1], vertical));
  }
  return bloques;
}

// ---------- estructura del documento ----------
const spec = (carpeta) => [
  { ruta: `specs/${carpeta}/spec.md`, base: 2 },
  { ruta: `specs/${carpeta}/plan.md`, base: 3 },
  { ruta: `specs/${carpeta}/tasks.md`, base: 3, horizontal: true },
];

const SECCIONES = [
  { titulo: "Problema y alcance", archivos: [{ ruta: "specs/00-problema-y-alcance.md", base: 1, sinH1: true }] },
  {
    titulo: "Cinco SPECS",
    intro: "Cada especificación incluye su historia, criterios de aceptación, plan de diseño, tareas, versión y registro de revisión. Los archivos fuente están en la carpeta specs/ del repositorio.",
    archivos: ["S01-registrar", "S02-priorizar-asignar", "S03-atender", "S04-validar", "S05-consultar-historizar"].flatMap(spec),
  },
  {
    titulo: "Diseño",
    archivos: [
      { ruta: "docs/diseno/arquitectura.md", base: 1, sinH1: true, imagenes: true },
      { ruta: "docs/diseno/adr-001-capa-de-dominio.md", base: 2 },
    ],
  },
  {
    titulo: "IA e implementación",
    archivos: [
      { ruta: "docs/entrega/06-ia-e-implementacion.md", base: 1, sinH1: true },
      { ruta: "docs/bitacora-ia.md", base: 2 },
      { ruta: "docs/revision/revision-asistida-ia-2026-10-08.md", base: 2 },
    ],
  },
  { titulo: "Validación", archivos: [{ ruta: "docs/validacion/validacion.md", base: 1, sinH1: true, horizontal: true }] },
  { titulo: "Riesgos", archivos: [{ ruta: "docs/riesgos.md", base: 1, sinH1: true }] },
  { titulo: "Entrega reproducible", archivos: [{ ruta: "docs/entrega/09-entrega-reproducible.md", base: 1, sinH1: true }] },
  { titulo: "Contribuciones y cierre", archivos: [{ ruta: "docs/entrega/10-contribuciones-y-cierre.md", base: 1, sinH1: true }] },
  { titulo: "Referencias", archivos: [{ ruta: "docs/referencias.md", base: 1, sinH1: true }] },
];

const centrado = (texto, opciones = {}, despues = 120) =>
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: despues, line: INTERLINEADO }, children: enLinea(texto, "", opciones) });

const portada = [
  new Paragraph({ spacing: { before: 1400 }, children: [] }),
  centrado("Universidad Simón Bolívar", { bold: true, size: 36 }),
  centrado("Programa de Ingeniería de Sistemas", { size: 28 }),
  centrado("Ingeniería de Software I", { size: 28 }, 900),
  centrado("Segundo examen práctico: Spec-Driven Development con IA", { bold: true, size: 32 }),
  centrado("Caso ReparaCampus", { bold: true, size: 32 }, 900),
  centrado(`Equipo: ${dato("EQUIPO")}`, { size: 26 }, 240),
  centrado("Integrantes", { bold: true, size: 24 }),
  ...datos.INTEGRANTES.map((nombre) => centrado(nombre, { size: 24 }, 40)),
  new Paragraph({ spacing: { before: 700 }, children: [] }),
  centrado(`Grupo: ${dato("GRUPO")}`, { size: 24 }, 60),
  centrado(`Docente: ${dato("DOCENTE")}`, { size: 24 }, 60),
  centrado(`Fecha: ${dato("FECHA")}`, { size: 24 }, 60),
  centrado(`Repositorio: <${REPO}>`, { size: 22 }, 60),
];

const indice = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Índice")] }),
  new TableOfContents("Índice", { hyperlink: true, headingStyleRange: "1-2" }),
];

// Agrupa los bloques en secciones de Word según la orientación de la página.
const grupos = [{ vertical: true, hijos: portada }, { vertical: true, hijos: indice }];
for (const seccion of SECCIONES) {
  let primero = true;
  for (const archivo of seccion.archivos) {
    const vertical = !archivo.horizontal;
    let grupo = grupos[grupos.length - 1];
    if (primero || grupo.vertical !== vertical) {
      grupo = { vertical, hijos: [] };
      grupos.push(grupo);
    }
    if (primero) {
      grupo.hijos.push(titulo(seccion.titulo, 1));
      if (seccion.intro) grupo.hijos.push(parrafo(seccion.intro, ""));
      primero = false;
    }
    grupo.hijos.push(...convertir(archivo, vertical));
  }
}

const pie = () =>
  new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: "ReparaCampus · Examen SDD + IA · Página ", size: 18, color: "666666" }),
        new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "666666" }),
      ],
    })],
  });

const estiloTitulo = (id, nombre, size, nivel) => ({
  id, name: nombre, basedOn: "Normal", next: "Normal", quickFormat: true,
  run: { size, bold: true, color: "1F3A5F", font: FUENTE },
  paragraph: { outlineLevel: nivel },
});

const documento = new Document({
  creator: "Equipo ReparaCampus",
  title: "Examen SDD + IA · ReparaCampus",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FUENTE, size: CUERPO } } },
    paragraphStyles: [
      estiloTitulo("Heading1", "Heading 1", 32, 0),
      estiloTitulo("Heading2", "Heading 2", 26, 1),
      estiloTitulo("Heading3", "Heading 3", 23, 2),
      estiloTitulo("Heading4", "Heading 4", 22, 3),
    ],
  },
  numbering: {
    config: [
      { reference: "vinetas", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 250 } } } }] },
      { reference: "numeros", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] },
    ],
  },
  sections: grupos.map((grupo, i) => ({
    properties: {
      page: {
        size: { width: A4.ancho, height: A4.alto, orientation: grupo.vertical ? PageOrientation.PORTRAIT : PageOrientation.LANDSCAPE },
        margin: { top: A4.margen, bottom: A4.margen, left: A4.margen, right: A4.margen },
      },
      titlePage: i === 0,
    },
    footers: { default: pie(), first: new Footer({ children: [new Paragraph("")] }) },
    children: grupo.hijos,
  })),
});

Packer.toBuffer(documento).then((buffer) => {
  fs.writeFileSync(process.argv[2], buffer);
  console.log(`ok · ${grupos.length} secciones de página · ${nTabla} tablas · ${nFigura} figuras`);
});
