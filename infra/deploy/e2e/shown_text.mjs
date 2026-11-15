// What the web shows of the API's texts where it does not show them verbatim, for the plain Node
// checks (this e2e, apps/web/scripts/check-search.mjs and check-qa.mjs). Copied, not imported: they
// cannot load the web's TypeScript. Keep it in step with apps/web/src/lib/fit.ts (factText,
// RENT_2024_NOTICE) and apps/web/src/lib/shortfall.ts (resultados.casi.*).

/** resultados.aviso_2024 and zona.precio.aviso_2024: renting, never buying (F5 of fit-0.9; plain words since the UX audit). */
export const RENT_2024_NOTICE = "Precio orientativo: hoy puede ser algo más caro.";

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
