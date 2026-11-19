/**
 * «Para desarrolladores» (D-249): the public API and the MCP, free for everyone. Copy from
 * pitch/textos_web.md, section 12 (desarrolladores.*). Every example was run once against
 * production on 19 Nov 2026 (evidence/gate-06/2026-11-19-desarrolladores/): change one and run it
 * again before publishing it.
 */

export const SITE_URL = "https://vidafacil-madrid.vercel.app";
export const API_BASE = `${SITE_URL}/api/v1`;
export const REPO_URL = "https://github.com/marianohernando/housing-intelligence";
/** The branch with the API and the MCP of production (the repo's default branch is older). */
export const REPO_BRANCH = "claude/sprint-1-public";
export const repoFile = (path: string) => `${REPO_URL}/blob/${REPO_BRANCH}/${path}`;
export const repoFolder = (path: string) => `${REPO_URL}/tree/${REPO_BRANCH}/${path}`;

export const DEV_TEXT = {
  tag: "Gratis · sin clave · solo lectura",
  title: "API y MCP para desarrolladores",
  intro:
    "Las mismas cifras que ves en Vida Fácil, para tu sistema o para tu agente de IA: qué falta en cada zona, qué zonas encajan con un hogar, el suelo público y si una promoción sale. Gratis para todos, también para empresas y ayuntamientos, igual que los datos.",
  tocLabel: "En esta página",
  verified: "Cada ejemplo se ha probado contra la API de producción el 19 de noviembre de 2026.",
  copy: "Copiar",
  copied: "Copiado",
  copyFailed: "No se ha podido copiar: selecciona el texto y cópialo.",
  works: "Funciona hoy",
  local: "Funciona en local",
  planned: "Aún no disponible",
  isNew: "Nueva",
} as const;

export interface Section {
  id: string;
  title: string;
}

export const SECTIONS: readonly Section[] = [
  { id: "que-es", title: "Qué es" },
  { id: "licencias", title: "Datos y licencias" },
  { id: "funciona-hoy", title: "Funciona hoy: la API" },
  { id: "mcp", title: "El MCP, para agentes de IA" },
  { id: "planteado", title: "Planteado" },
  { id: "uso-justo", title: "Uso justo" },
  { id: "mas", title: "Más información" },
];

export type Json = string | number | boolean | null | Json[] | { [key: string]: Json };

export interface ApiExample {
  id: string;
  title: string;
  method: "GET" | "POST";
  /** The route as documented, with its placeholders */
  path: string;
  description: string;
  /** What the example asks for: the path after /api/v1, with its query */
  request: string;
  body?: Json;
  returns: string;
}

export interface ApiGroup {
  id: string;
  title: string;
  examples: readonly ApiExample[];
}

/** The body with one top-level field per line, under the «{» of `  -d '{` (short lines on a phone). */
function bodyLines(body: Json): string {
  if (body === null || typeof body !== "object" || Array.isArray(body)) return JSON.stringify(body);
  const fields = Object.entries(body).map(([key, value]) => `${JSON.stringify(key)}:${JSON.stringify(value)}`);
  return `{${fields.join(",\n       ")}}`;
}

/** A copyable command: GET in quotes (the query has &), POST with its JSON body. */
export function curlOf(example: ApiExample): string {
  const url = `${API_BASE}${example.request}`;
  if (example.method === "GET") return `curl -s "${url}"`;
  return `curl -s -X POST ${url} \\\n  -H 'Content-Type: application/json' \\\n  -d '${bodyLines(example.body ?? {})}'`;
}

export const API_GROUPS: readonly ApiGroup[] = [
  {
    id: "buscar",
    title: "Buscar zonas para un hogar",
    examples: [
      {
        id: "search",
        title: "Las zonas que encajan con un hogar",
        method: "POST",
        path: "/api/v1/search",
        description:
          "Ordena los municipios de la Comunidad de Madrid (Madrid capital, por sus 21 distritos) para un hogar: cuánto puede pagar, quién vive, dónde trabaja y qué le importa. Es el buscador de la web. El cuerpo es un ScenarioState.",
        request: "/search",
        body: {
          budget: { kind: "rent", amount_eur: 1500 },
          household: { adults: 2, minors: 1, minor_ages: [4] },
          priorities: ["colegios", "transporte"],
        },
        returns:
          "Las 10 zonas que mejor encajan (results), con su % de encaje y sus hechos; las que fallan por poco (near_misses); qué pasa si cambias una condición (reality_check), y todas las zonas para pintar un mapa (all_zones).",
      },
      {
        id: "search-barrios",
        title: "Las mismas, por barrios de un distrito de Madrid",
        method: "POST",
        path: "/api/v1/search/barrios",
        description:
          "El mismo buscador dentro de un distrito de Madrid capital, barrio a barrio. distrito es su código INE: aquí, Ciudad Lineal.",
        request: "/search/barrios",
        body: { scenario: { budget: { kind: "rent", amount_eur: 1500 }, household: { adults: 2 } }, distrito: "2807915" },
        returns: "Los barrios del distrito, con el mismo contrato que /search y el distrito en distrito.",
      },
    ],
  },
  {
    id: "que-falta",
    title: "Qué falta en cada zona",
    examples: [
      {
        id: "gaps-zone",
        title: "Qué falta en una zona",
        method: "GET",
        path: "/api/v1/gaps/{level}/{code}",
        description:
          "Lo que falta en una zona frente a los municipios de su tipo (urbanos o rurales): escuela infantil, colegio, centro de salud, mayores, farmacia y vivienda. level es municipio, distrito (los 21 de Madrid) o seccion_censal, y code, su código INE: aquí, Parla.",
        request: "/gaps/municipio/28106",
        returns:
          "Una fila por servicio con su estado (FALTA, JUSTO, CUBIERTO o SIN_DATOS), su cifra, la referencia con la que se compara, una explicación en palabras y sus fuentes.",
      },
      {
        id: "gaps-map",
        title: "Una fila en todas las zonas",
        method: "GET",
        path: "/api/v1/gaps?level=&row=",
        description:
          "El mapa de lo que falta: una fila en todas las zonas de un nivel. row es escuela_infantil, colegio, centro_salud, mayores, farmacia o vivienda.",
        request: "/gaps?level=municipio&row=farmacia",
        returns: "Cada zona con su estado, su cifra y su confianza, el recuento por estado, la referencia y los cortes.",
      },
      {
        id: "gaps-impact",
        title: "A cuánta gente afecta y dónde invertir primero",
        method: "GET",
        path: "/api/v1/gaps/impact",
        description: "Por cada fila, cuánta gente vive donde falta y la lista de zonas de más a menos gente afectada.",
        request: "/gaps/impact",
        returns: "people_in_falta, people_total y share_in_falta por fila, y el ranking con una explicación de cada zona.",
      },
    ],
  },
  {
    id: "fuentes",
    title: "Fuentes e indicadores",
    examples: [
      {
        id: "datasets",
        title: "Los conjuntos de datos",
        method: "GET",
        path: "/api/v1/datasets",
        description:
          "Los conjuntos de datos que usamos, con su versión, su licencia, su enlace y el texto con el que hay que citarlos. cm_only=true deja solo los del portal de la Comunidad de Madrid.",
        request: "/datasets?cm_only=true",
        returns: "total, cm_open_data_count y la lista de datasets, cada uno con license, url y attribution_text.",
      },
      {
        id: "features",
        title: "El catálogo de indicadores",
        method: "GET",
        path: "/api/v1/features?level=",
        description:
          "Los indicadores de un nivel (municipio, distrito, barrio…), con su unidad, sus límites y sus fuentes. Aquí, los de distrito.",
        request: "/features?level=distrito",
        returns: "Cada indicador con su feature_id, su nombre, su unidad, lo que no mide (limitations) y sus fuentes.",
      },
      {
        id: "feature-values",
        title: "Los valores de un indicador",
        method: "GET",
        path: "/api/v1/features/{feature_id}/values?level=",
        description: "Un indicador en todas las zonas de un nivel. Aquí, el suelo público para vivienda por distrito.",
        request: "/features/suelo_publico_vivienda_m2/values?level=distrito",
        returns: "El valor de cada zona con su null_reason y su confianza, y los datasets y versiones de los que sale.",
      },
    ],
  },
  {
    id: "mapa",
    title: "Zonas y lugares en el mapa",
    examples: [
      {
        id: "admin-units",
        title: "Las geometrías de las zonas",
        method: "GET",
        path: "/api/v1/geo/admin-units?level=&parent=",
        description:
          "Las zonas en GeoJSON: municipios, distritos, barrios o secciones censales. parent deja solo las de una zona madre: aquí, los 21 distritos de Madrid.",
        request: "/geo/admin-units?level=distrito&parent=ES.28.MUN.28079",
        returns: "Una FeatureCollection; cada zona con su admin_unit_id, su código, su nombre y su superficie.",
      },
      {
        id: "places",
        title: "Los equipamientos de una zona",
        method: "GET",
        path: "/api/v1/places?category=&admin_unit_id=",
        description:
          "Colegios, centros de salud, farmacias, transporte… como puntos GeoJSON. category admite varias, separadas por comas (education, health, pharmacy, transport…). Aquí, las farmacias de Chamartín.",
        request: "/places?category=pharmacy&admin_unit_id=ES.28.DIS.2807905",
        returns: "Los lugares con su nombre, su categoría, su capacidad si la fuente la publica y su confianza, de 5.000 en 5.000 (page).",
      },
    ],
  },
  {
    id: "inversores",
    title: "Para inversores y promotores (piloto: Madrid capital dentro de la M-40)",
    examples: [
      {
        id: "investor-zones",
        title: "Los barrios del piloto",
        method: "GET",
        path: "/api/v1/investors/zones",
        description: "Los barrios del piloto con lo que falta en su distrito, su suelo público, la edificabilidad que queda y sus precios.",
        request: "/investors/zones",
        returns: "Cada barrio con su distrito, las filas de «Qué falta» de su distrito, sus parcelas y sus m², y su precio y alquiler estimados.",
      },
      {
        id: "investor-zone",
        title: "La ficha de un barrio",
        method: "GET",
        path: "/api/v1/investors/zones/{admin_unit_id}",
        description:
          "Quién vive, precios, qué falta, suelo y los valores de partida de la viabilidad. Cada cifra trae su fuente y si es un dato o un supuesto. Aquí, Pinar del Rey.",
        request: "/investors/zones/ES.28.BAR.28079164",
        returns: "Bloques demand, prices, gaps, land y defaults; cada cifra con value, unit, mark (dato o supuesto) y source.",
      },
      {
        id: "viability",
        title: "¿Sale una promoción?",
        method: "POST",
        path: "/api/v1/investors/viability",
        description:
          "La viabilidad por el método residual (v0): m² construidos (50 como mínimo), precio de venta, PEM y, si quieres, alquiler y precio del suelo, en total o por m² edificable. Sin precio del suelo te dice lo máximo que se puede pagar por él. No es una tasación.",
        request: "/investors/viability",
        body: {
          buildable_m2: 1000,
          sale_price_m2: 4847,
          new_build_premium_pct: 9.3,
          rent_m2_month: 16,
          pem_m2: 644,
          land_eur_m2: 3200,
        },
        returns:
          "Tres escenarios. Con este ejemplo, un margen sobre ventas del 15,1 % en el base («Ajustar»), del 22,8 % en el optimista («Sale») y del 5,6 % en el pesimista («No sale»), con sus avisos.",
      },
    ],
  },
];

export interface McpTool {
  name: string;
  text: string;
  isNew?: boolean;
}

export const MCP_TOOLS: readonly McpTool[] = [
  { name: "buscar_zonas", text: "ordena las zonas para un hogar, como POST /search." },
  { name: "que_falta", text: "lo que falta en una zona, como GET /gaps/{level}/{code}." },
  { name: "explicar_zona", text: "una zona explicada, con todos sus indicadores y sus fuentes." },
  { name: "encontrar_zona", text: "el código de un municipio o de un distrito de Madrid a partir de su nombre." },
  { name: "fuentes_de_datos", text: "los conjuntos de datos, como GET /datasets." },
  {
    name: "ficha_inversor",
    text: "la ficha de un barrio del piloto, por su nombre o su código, como GET /investors/zones/{admin_unit_id}.",
    isNew: true,
  },
  { name: "viabilidad", text: "la viabilidad de una promoción, con el mismo cuerpo que POST /investors/viability.", isNew: true },
];

const LOCAL_DATABASE_URL = "postgresql+psycopg://housing:housing@localhost:5440/housing";
const CLONE_PATH = "/ruta/a/housing-intelligence";

export const MCP_SETUP = `git clone --branch ${REPO_BRANCH} ${REPO_URL}.git
cd housing-intelligence
cp .env.example .env
make dev
make ingest-all`;

export const MCP_CLAUDE_CODE = `claude mcp add vida-facil \\
  -e DATABASE_URL=${LOCAL_DATABASE_URL} \\
  -- uv run --quiet --directory ${CLONE_PATH} hi-mcp`;

export const MCP_CLAUDE_DESKTOP = JSON.stringify(
  {
    mcpServers: {
      "vida-facil": {
        command: "uv",
        args: ["run", "--quiet", "--directory", CLONE_PATH, "hi-mcp"],
        env: { DATABASE_URL: LOCAL_DATABASE_URL },
      },
    },
  },
  null,
  2,
);

export const ENVELOPE_EXAMPLE = `{
  "data": { … },
  "meta": {
    "request_id": "…",
    "generated_at": "2026-11-19T09:54:01Z",
    "api_version": "v1",
    "methodology_version": "gap-0.3",
    "data_version": "2026-11-19"
  },
  "warnings": []
}`;

export interface PlannedItem {
  title: string;
  text: string;
}

export const PLANNED: readonly PlannedItem[] = [
  {
    title: "El MCP en remoto (HTTP), en este mismo dominio",
    text: "Para conectar tu asistente sin instalar nada ni cargar una base de datos.",
  },
  {
    title: "Avisos de suelo público nuevo",
    text: "Un aviso cuando aparezca una parcela para vivienda nueva en el Portal del Suelo de la Comunidad de Madrid.",
  },
  {
    title: "Claves opcionales para integraciones con mucho tráfico",
    text: "Con una cuota de uso justo. La API seguirá funcionando sin clave.",
  },
  {
    title: "Descargas en CSV y GeoJSON",
    text: "Las tablas y los mapas de una vez, para abrirlos en una hoja de cálculo o en un SIG.",
  },
];
