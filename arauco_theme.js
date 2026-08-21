// arauco_theme.js
// Tema corporativo reutilizable (colores, fuentes, tamaños) para generar
// presentaciones .pptx con pptxgenjs, basado en KOM_Implementacion_Tercer_Filtro_LV.
//
// USO:
//   const pptxgen = require("pptxgenjs");
//   const { COLORS, FONT, SIZES, addTitle, addBody, addTableHeader } = require("./arauco_theme.js");
//   const pres = new pptxgen();
//   pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5 in
//   const slide = pres.addSlide();
//   addTitle(slide, "Título de la lámina");
//   ...
//   pres.writeFile({ fileName: "salida.pptx" });

const COLORS = {
  accent: "EF7D00",      // naranjo corporativo (acentos, destacados)
  textDark: "5F5A57",    // gris-café, texto principal
  textMedium: "6A6158",  // gris-café medio, texto secundario
  black: "000000",       // negro puro, texto/tablas
  beige: "D8CCA0",       // beige/dorado, headers de tabla o fondos de énfasis
  greyLight: "D0D0D0",   // gris claro, fondos secundarios
  greyLighter: "F2F2F2", // gris muy claro
  greyLightest: "EFEFEF",
  white: "FFFFFF",
};

const FONT = "Arial";

// Tamaños en puntos (pptxgenjs usa pt directamente en fontSize)
const SIZES = {
  titleMain: 24,     // título principal de slide
  titleSlide: 22,
  subtitle: 17,      // subtítulos / encabezados de sección
  body: 14,          // texto de tablas / cuerpo estándar
  bodySmall: 13,
  note: 10.5,        // texto secundario / notas
  footnote: 9,        // pies de página / referencias
  bigNumber: 34,      // cifras destacadas
};

function addTitle(slide, text, opts = {}) {
  slide.addText(text, {
    x: 0.5, y: 0.3, w: 12.3, h: 0.7,
    fontFace: FONT, fontSize: SIZES.titleMain, bold: true,
    color: COLORS.textDark,
    ...opts,
  });
}

function addSubtitle(slide, text, opts = {}) {
  slide.addText(text, {
    fontFace: FONT, fontSize: SIZES.subtitle, bold: true,
    color: COLORS.accent,
    ...opts,
  });
}

function addBody(slide, text, opts = {}) {
  slide.addText(text, {
    fontFace: FONT, fontSize: SIZES.body,
    color: COLORS.textDark,
    ...opts,
  });
}

// Genera opciones de tabla con header en beige y cuerpo en tonos corporativos
function tableStyle() {
  return {
    headerFill: COLORS.beige,
    headerColor: COLORS.textDark,
    bodyColor: COLORS.textDark,
    bodyFill: COLORS.white,
    altFill: COLORS.greyLighter,
    fontFace: FONT,
    headerFontSize: SIZES.body,
    bodyFontSize: SIZES.bodySmall,
  };
}

module.exports = { COLORS, FONT, SIZES, addTitle, addSubtitle, addBody, tableStyle };
