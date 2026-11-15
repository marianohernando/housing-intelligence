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

/** D-230 as the web shows it: too small to compare, even with its neighbours (notComparable of lib/gaps.ts). */
export function notComparable(row) {
  return row.status !== "SIN_DATOS" && row.reliable === false && !((row.comparison_group?.names?.length ?? 0) >= 2);
}

/** Row names as the card writes them (ROW_NAME of lib/gaps.ts). */
export const ROW_NAME = {
  escuela_infantil: "Escuelas infantiles",
  colegio: "Colegios",
  centro_salud: "Centros de salud",
  mayores: "Centros de mayores",
  farmacia: "Farmacias",
  vivienda: "Vivienda para familias",
};

/**
 * zona.esencial.falta: the household's rows of a /gaps answer that are FALTA or JUSTO and can be
 * compared, as the card names them; with none, and some of its rows CUBIERTO (householdCovered),
 * the card says nothingMissing(many) (householdGaps of lib/essentials.ts).
 */
export function householdShortRows(rows, household) {
  const mine = householdRows(household);
  return rows.filter((r) => mine.includes(r.row) && (r.status === "FALTA" || r.status === "JUSTO") && !notComparable(r));
}

export function householdCovered(rows, household) {
  const mine = householdRows(household);
  return rows.some((r) => mine.includes(r.row) && r.status === "CUBIERTO" && !notComparable(r));
}

export const nothingMissing = (many) => `No le falta nada de lo que ${many ? "buscáis" : "buscas"}.`;

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
