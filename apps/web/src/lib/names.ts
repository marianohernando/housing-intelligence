/**
 * Readable place names. Zone names come readable from the API (display_name, since 12c834a);
 * /api/v1/places keeps the upper case of some sources (metro stations, schools).
 */

const LOWER_PARTICLES = new Set(["de", "del", "la", "las", "los", "el", "y", "e", "en"]);
/** «Juan Pablo II», «Carlos III»: a whole word of Roman numerals (not the particle «y» or «e»). */
const ROMAN = /^(?=[ivxl]+$)(x{0,3})(ix|iv|v?i{0,3})$/;

function isUpper(text: string): boolean {
  return text === text.toUpperCase() && text !== text.toLowerCase();
}

function capitalize(word: string): string {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

/** "CONCHA ESPINA" -> "Concha Espina"; mixed-case names are already readable. */
export function titleCase(text: string): string {
  const name = text.trim().split(/\s+/).join(" ");
  if (!isUpper(name)) return name;
  return name
    .toLowerCase()
    .split(" ")
    .map((word, i) => {
      if (i > 0 && LOWER_PARTICLES.has(word)) return word;
      if (i > 0 && ROMAN.test(word)) return word.toUpperCase();
      return word.split("-").map(capitalize).join("-");
    })
    .join(" ");
}
