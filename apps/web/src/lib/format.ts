/** Numbers the Spanish way (pitch/textos_web.md): 1.500 €, 0,47. es-ES skips the dot in 4-digit numbers by default. */
const EUROS = new Intl.NumberFormat("es-ES", { maximumFractionDigits: 0, useGrouping: "always" });

export function formatEuros(amount: number): string {
  return `${EUROS.format(amount)} €`;
}
