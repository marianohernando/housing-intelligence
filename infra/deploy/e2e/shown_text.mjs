// What the web shows of the API's texts where it does not show them verbatim, for the plain Node
// checks (this e2e, apps/web/scripts/check-search.mjs and check-qa.mjs). Copied, not imported: they
// cannot load the web's TypeScript. Keep it in step with apps/web/src/lib/fit.ts (factText,
// PRICE_HINT, RENT_2024_NOTICE, RENT_LIST_NOTICE, passingText, speaksToMany), apps/web/src/lib/shortfall.ts
// (resultados.casi.*) and apps/web/src/lib/essentials.ts with lib/gaps.ts (householdGaps, householdRows).

/** zona.precio.orientativo: by the price of the card's essentials (second delivery of the UX mobile audit). */
export const PRICE_HINT = "Precio orientativo";

/** zona.precio.aviso_2024: renting, why the price is orientative, behind «Ver más» of the card; never buying (F5 of fit-0.9). */
export const RENT_2024_NOTICE = "Precio de contratos firmados en 2024; los anuncios de hoy suelen pedir más.";

/** resultados.aviso_2024: renting, once under the list; never buying. */
export const RENT_LIST_NOTICE = "Precios orientativos: hoy pueden ser algo más caros.";

/** resultados.aviso_compra: buying, once under the list (BUY_LIST_NOTICE of lib/fit.ts). */
export const BUY_LIST_NOTICE = "Precios orientativos: son una estimación del precio de compra.";

/** «para vosotros» for a household of more than one, «para ti» otherwise (the API's defaults: one adult). */
export function speaksToMany(household) {
  if (!household) return false;
  return (household.adults ?? 1) + (household.minors ?? 0) + (household.seniors_in_care ?? 0) > 1;
}

/** The rows of «Qué falta» that matter to a household (householdRows of lib/gaps.ts, highlight_rows of the API without housing). */
export function householdRows(household) {
  const minors = household?.minors ?? 0;
  const ages = household?.minor_ages ?? [];
  const rows = [];
  if (minors > 0 && (ages.length === 0 || Math.min(...ages) <= 2)) rows.push("escuela_infantil");
  if (minors > 0) rows.push("colegio");
  rows.push("centro_salud", "farmacia");
  if (household?.seniors === true || (household?.seniors_in_care ?? 0) > 0) rows.push("mayores");
  return rows;
}

const PRIORITY_ROW = { salud: "centro_salud", colegios: "colegio" };
const NEED_ROWS = ["escuela_infantil", "colegio", "centro_salud", "farmacia", "mayores"];

/** The household's rows and then what the person marks (pertinentRows of lib/essentials.ts, marked_rows of the API). */
export function pertinentRows(scenario) {
  const marked = [...(scenario.priorities ?? []).map((p) => PRIORITY_ROW[p]), ...(scenario.nearby ?? []).map((n) => n.need)];
  return [...new Set([...householdRows(scenario.household), ...marked.filter((row) => NEED_ROWS.includes(row))])];
}

/** D-230 as the web shows it: too small to compare, even with its neighbours (notComparable of lib/gaps.ts). */
export function notComparable(row) {
  return row.status !== "SIN_DATOS" && row.reliable === false && !((row.comparison_group?.names?.length ?? 0) >= 2);
}

/** Row names as the card writes them (ROW_NAME and ROW_IN_LIST of lib/gaps.ts). */
export const ROW_NAME = {
  escuela_infantil: "Escuelas infantiles",
  colegio: "Colegios",
  centro_salud: "Centros de salud",
  mayores: "Centros de mayores",
  farmacia: "Farmacias",
  vivienda: "Vivienda para familias",
};
const ROW_IN_LIST = {
  escuela_infantil: "escuelas infantiles",
  colegio: "colegios",
  centro_salud: "centros de salud",
  mayores: "centros de mayores",
  farmacia: "farmacias",
  vivienda: "viviendas grandes para familias",
};

const joinOr = (names) => (names.length <= 1 ? (names[0] ?? "") : `${names.slice(0, -1).join(", ")} o ${names.at(-1)}`);

/**
 * zona.esencial.falta, nada, comparable and no_sabemos (householdGaps of lib/essentials.ts and
 * HomeGaps of ZoneCard.tsx), from the /gaps answer the card asked for: what must be on the card,
 * and whether the green «No le falta nada…» may be. `place` is the district of a barrio's card.
 */
export function essentialGapLines(rows, scenario, many, place = null) {
  const own = pertinentRows(scenario).flatMap((key) => rows.filter((r) => r.row === key));
  const short = own.filter((r) => (r.status === "FALTA" || r.status === "JUSTO") && !notComparable(r));
  const unknown = own.filter((r) => r.status === "SIN_DATOS" || notComparable(r)).map((r) => r.row);
  const covered = own.some((r) => r.status === "CUBIERTO" && !notComparable(r));
  const where = place ? ` en ${place}` : "";
  const lines = short.map((r) => `${ROW_NAME[r.row]}${where}:`);
  const nothing = short.length === 0 && covered && unknown.length === 0;
  if (nothing) lines.push(nothingMissing(many, place));
  if (short.length === 0 && covered && unknown.length > 0) {
    lines.push(place ? `En ${place}, de lo que podemos comparar, no falta nada.` : "De lo que podemos comparar, no le falta nada.");
  }
  if (unknown.length) {
    const names = joinOr(unknown.map((r) => ROW_IN_LIST[r]));
    lines.push(place ? `No sabemos si en ${place} faltan ${names}.` : `No sabemos si le faltan ${names}.`);
  }
  return { lines, nothing };
}

/** zona.esencial.nada: «No le falta nada de lo que buscáis.», in a barrio «En Barajas no falta nada de lo que buscáis.» */
export function nothingMissing(many, place = null) {
  const buscas = many ? "buscáis" : "buscas";
  return place ? `En ${place} no falta nada de lo que ${buscas}.` : `No le falta nada de lo que ${buscas}.`;
}

/**
 * A fact as the card shows it: renting, the rent fact goes without its «; un anuncio de hoy puede
 * pedir más», which RENT_2024_NOTICE says by the price, and the cost fact says its figure in words
 * («unos 1.101 € al mes», not «≈ 1.101 €/mes»). Applied whatever the budget: a purchase fact has no
 * such warning, so it gets only the words, as in the web (factText of apps/web/src/lib/fit.ts).
 */
export function factAsShown(fact) {
  if (fact.topic !== "coste") return fact.text;
  return fact.text.replace(/;\s*un anuncio de hoy puede pedir más/, "").replace(/≈ /g, "unos ").replace(/€\/mes/g, "€ al mes");
}

/**
 * The line of a near miss in «Casi valen» (resultados.casi.*): what it lacks, by its figures (with
 * «unos», never «≈») or by its name, and «y otra condición» or «y {n} condiciones más» when it fails
 * more. Never a %.
 */
export const NEAR_MISS_LINE = new RegExp(
  "^(?:" +
    [
      "Se pasa unos [\\d.]+ €(?: al mes)? de tu presupuesto",
      "Tarda (?:unos \\d+ min|menos de 1 min) más de lo que pides(?: hasta .+)?",
      "Tarda más de 2 h(?: hasta .+)?; pides \\d+ min como mucho",
      ".+: (?:unos \\d+ min|menos de 1 min) más andando de lo que pides",
      ".+ a más de 1 h andando; pides \\d+ min como mucho",
      "No cumple: .+",
      "No cumple todo lo que pides\\.",
    ].join("|") +
    ")(?: y otra condición| y \\d+ condiciones más)?$",
);
