/**
 * Readable place names. `displayName` mirrors hi_domain.geo.names.display_name (same test cases),
 * because /api/v1/geo/admin-units still returns municipios in the official upper case.
 */

const LOWER_PARTICLES = new Set(["de", "del", "la", "las", "los", "el", "y", "e", "en"]);
const ARTICLES = new Set(["el", "la", "los", "las"]);

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

/** "ROZAS DE MADRID, LAS" -> "Las Rozas de Madrid". Accents missing in the source stay so. */
export function displayName(official: string): string {
  let name = official.trim().split(/\s+/).join(" ");
  if (!isUpper(name)) return name;
  const comma = name.lastIndexOf(", ");
  if (comma >= 0) {
    const article = name.slice(comma + 2);
    if (ARTICLES.has(article.toLowerCase())) name = `${article} ${name.slice(0, comma)}`;
  }
  return titleCase(name);
}
