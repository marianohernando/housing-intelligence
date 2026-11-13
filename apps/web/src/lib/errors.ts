/** Plain-language message for a failed API call (pitch/textos_web.md, error.*). */
import type { ApiError } from "@/lib/api";

const BY_CODE: Record<string, string> = {
  NETWORK: "No hemos podido conectar. Comprueba tu conexión a internet e inténtalo otra vez.",
  VALIDATION: "Hay algo en tu búsqueda que no podemos usar. Revisa los datos marcados.",
  NOT_FOUND: "No encontramos esa zona. Elige otra en el mapa.",
  OUT_OF_COVERAGE: "Ese lugar está fuera de la Comunidad de Madrid. Vida Fácil solo cubre la Comunidad de Madrid.",
  INSUFFICIENT_DATA: "No hay datos suficientes para responder con seguridad en esta zona.",
  SOURCE_DEGRADED: "Uno de los datos oficiales no está disponible ahora. Te enseñamos lo que tenemos y marcamos lo que falta.",
  RATE_LIMITED: "Hay mucha gente usando Vida Fácil ahora mismo. Espera unos segundos y vuelve a intentarlo.",
};
const SERVER = "Algo ha fallado por nuestra parte. Inténtalo de nuevo en unos minutos.";

export function errorMessage(error: Pick<ApiError, "code">): string {
  return BY_CODE[error.code] ?? SERVER;
}
