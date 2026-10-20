# Source review — Google Maps vía Gosom (google-maps-scraper)

- **source_id:** `google_maps_scraped`
- **Owner:** Google LLC
- **Herramienta:** `gosom/google-maps-scraper` (imagen Docker disponible en la máquina local)
- **Fecha de revisión:** 2026-10-20
- **Estado:** `REJECTED` para el proyecto DATAMAD. Como máximo `RESEARCH_ONLY` privado, fuera del repositorio, si Mariano lo decide.

## Qué haría
Extraer fichas de negocios (nombre, categoría, dirección, valoración, horarios) navegando la web pública de Google Maps de forma automatizada.

## Términos y licencia
- Los Términos de Servicio de Google Maps/Google Maps Platform prohíben el acceso automatizado y la extracción o almacenamiento masivo de contenido fuera de las APIs oficiales.
- No hay licencia de reutilización. El contenido no es dato abierto.

## Conflicto con las bases DATAMAD 2026
- §6.3: respetar licencias y condiciones de uso de datos y APIs.
- §6.7: no incorporar datos obtenidos ilícitamente.
- §16: exclusión por utilización ilícita de datos.
- §10: 10 puntos por tecnologías abiertas y reproducibilidad. Un dataset scrapeado de Google no es reproducible ni redistribuible.

## Conflicto con la documentación del proyecto
- `CLAUDE.md` §15 y `docs/02_data/10_external_enrichment_strategy.md` §5 y §7: "no depender de scraping de Google Maps".
- `docs/11_engineering/09_data_acquisition_rules.md`: scraping solo tras source review y si los términos lo permiten.

## Justificación posible
No hay forma de justificar ante el jurado datos scrapeados de Google Maps sin contradecir las bases. Usarlos en el producto o en el repo pone en riesgo la candidatura entera.

## Alternativas abiertas para POIs
| Necesidad | Fuente | Licencia |
|---|---|---|
| Comercio y actividades, Madrid capital | Censo de locales, actividades y terrazas (datos.madrid.es) | Open data Ayto. Madrid |
| Sanidad | Centros y servicios sanitarios (datos.comunidad.madrid) | CC-BY |
| Educación | Centros educativos (datos.comunidad.madrid) | CC-BY |
| Farmacias | Oficinas de farmacia (datos.comunidad.madrid) | CC-BY |
| Servicios sociales | Registro de centros de atención social (datos.comunidad.madrid) | CC-BY |
| POIs generales, resto de municipios | OpenStreetMap (extracto Geofabrik) | ODbL, con atribución |
| Validación puntual | Google Places API oficial, si se justifica coste | Términos de la API; sin almacenamiento persistente |

## Decisión pendiente de Mariano
Confirmar `REJECTED` o permitir un benchmark privado de cobertura (POIs oficiales+OSM frente a Google) que nunca entre al producto, al repo ni a la presentación.
