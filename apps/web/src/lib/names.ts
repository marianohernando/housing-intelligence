/**
 * Readable place names. Zone names come readable from the API (display_name, since 12c834a);
 * /api/v1/places keeps the upper case of some sources (metro stations, schools).
 */

const LOWER_PARTICLES = new Set(["de", "del", "la", "las", "los", "el", "y", "e", "en"]);

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
    .map((word, i) => (i > 0 && LOWER_PARTICLES.has(word) ? word : word.split("-").map(capitalize).join("-")))
    .join(" ");
}
