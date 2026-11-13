/** Numbers the Spanish way (pitch/textos_web.md): 1.500 €, 0,47. es-ES skips the dot in 4-digit numbers by default. */
const EUROS = new Intl.NumberFormat("es-ES", { maximumFractionDigits: 0, useGrouping: "always" });

export function formatEuros(amount: number): string {
  return `${EUROS.format(amount)} €`;
}

const NUMBERS = new Map<number, Intl.NumberFormat>();

/** Fixed decimals the Spanish way, like hi_domain.gaps.es_number: 10.700,0 · 0,47. */
export function formatNumber(value: number, decimals: number): string {
  let format = NUMBERS.get(decimals);
  if (!format) {
    format = new Intl.NumberFormat("es-ES", { minimumFractionDigits: decimals, maximumFractionDigits: decimals, useGrouping: "always" });
    NUMBERS.set(decimals, format);
  }
  return format.format(value);
}
