/**
 * Confidence in words (pitch/textos_web.md, section 6, cut-offs confirmed by line A on 11 nov).
 * The API gives 0 to 1; 0,5 is the cap for small zones (D-189) and counts as approximate.
 */
export interface ConfidenceText {
  label: string;
  help: string;
}

const HIGH: ConfidenceText = { label: "Dato fiable", help: "Sale de un registro oficial completo." };
const MEDIUM: ConfidenceText = {
  label: "Dato aproximado",
  help: "Es una aproximación: la zona tiene poca población, la fuente no está completa o el dato es una estimación. Tómalo como orientativo.",
};
const LOW: ConfidenceText = { label: "Dato poco seguro", help: "Faltan bastantes datos en la fuente. Úsalo con cuidado." };
const NONE: ConfidenceText = { label: "Sin datos", help: "No tenemos este dato." };

export function confidenceText(confidence: number): ConfidenceText {
  if (confidence >= 0.8) return HIGH;
  if (confidence >= 0.5) return MEDIUM;
  if (confidence > 0) return LOW;
  return NONE;
}
