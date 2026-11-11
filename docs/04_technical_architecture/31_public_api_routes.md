# Rutas de la API PUBLIC para la demo DATAMAD

Contratos v2 del 11 nov 2026 (D-207, línea A), del producto «Vida Fácil». Los consume la web (línea B). La v1 (`7541527`) queda sustituida. Siguen las convenciones de `09_api_contract_conventions.md` y de `apps/api`:
- prefijo `/api/v1`;
- respuesta dentro del sobre `{data, meta, warnings}`;
- `meta.methodology_version` y `meta.data_version` informados;
- unidades explícitas.

## Contratos
| Contrato | Código | JSON Schema (para generar los tipos TypeScript) |
|---|---|---|
| `ScenarioState` v2 | `hi_contracts/public/scenario.py` | `data/schemas/api/scenario_state.schema.json` |
| `SearchResult` en `SearchResponse` | `hi_contracts/public/search.py`, `responses.py` | `data/schemas/api/search_response.schema.json` |
| `ZoneGapList` en `ZoneGapListResponse` | `hi_contracts/public/gaps.py`, `responses.py` | `data/schemas/api/zone_gap_list_response.schema.json` |
| `DatasetList` en `DatasetListResponse` | `hi_contracts/public/common.py`, `responses.py` | `data/schemas/api/dataset_list_response.schema.json` |
| Error | `hi_contracts/api/envelope.py` | `data/schemas/api/error_response.schema.json` |

- Los schemas se regeneran con `make schemas`. CI falla si no están al día.
- Hay ejemplos con zonas e indicadores reales en `data/fixtures/contracts/` (son fixtures: solo para tests y desarrollo).
- Las filas de la lista salen del Feature Dictionary: cada feature declara su fila en `gap_row`, con su título, la unidad en palabras y el proxy. La API no tiene ningún id de feature escrito a mano.

## Rutas

| Método y ruta | Entrada | Salida | Estado |
|---|---|---|---|
| `GET /api/v1/gaps/{level}/{code}` | `level`: `municipio`, `distrito` (los 21 de Madrid capital, códigos 2807901–2807921) o `seccion_censal` · `code`: código INE | `ZoneGapListResponse` | **Funciona desde el 11 nov** (esqueleto andante): filas de colegio y centro de salud por municipio con datos reales, frente a la referencia regional del Feature Store. Las filas que aún no están calculadas a un nivel no aparecen (no son SIN DATOS) y la respuesta lo avisa en `warnings`. GAP-001 añade escuela infantil, mayores, farmacia y vivienda, y CORE-005 la distancia a pie (`extra_indicators`) |
| `GET /api/v1/gaps?level=municipio&row=colegio` | nivel y fila | estado por zona para colorear el mapa | Prevista (GAP-001) |
| `POST /api/v1/search` | `ScenarioState` en el cuerpo | `SearchResponse` | Prevista (CORE-003). CORS ya admite `POST`. Las zonas son municipios con Madrid capital por distritos (D-200) |
| `GET /api/v1/datasets?cm_only=true` | `cm_only` (opcional) | `DatasetListResponse`: `total`, `cm_open_data_count` y los `DatasetRef` con versión | **Funciona desde el 11 nov**. Lista los datasets con una versión válida (QA superado): hoy 22, de los que 21 son CM |
| `GET /api/v1/geo/admin-units?level=` | — | geometrías GeoJSON | Existe |
| `GET /api/v1/features`, `GET /api/v1/features/{id}/values?level=` | — | catálogo y valores de features | Existe |
| `GET /api/v1/places?category=` | — | equipamientos como puntos | Existe |

## Reglas que la web puede dar por hechas
- **Zonas.** `ZoneRef.admin_unit_id` coincide con `promoteId` de las capas de `geo/admin-units`, y `name` ya viene legible («Las Rozas de Madrid», «Fuencarral-El Pardo»). Los distritos de Madrid traen `municipio_ine = 28079`.
- **Presupuesto (D-203).** `budget.kind` es `rent` (€/mes) o `buy` (€). La compra es orientativa; sin fuente fiable, su condición sale `UNKNOWN` con la explicación.
- **CORS.** Los orígenes se configuran con `CORS_ORIGINS` al arrancar la API (por ejemplo `CORS_ORIGINS='["http://localhost:3011"]'`). Se admiten `GET` y `POST`.
- **Lista de lo que falta.**
  - `SIN_DATOS` aparece si y solo si `indicator.value` es `null`, y entonces `indicator.null_reason` dice por qué. Un 0 es un dato real (ningún centro en un registro exhaustivo).
  - `ratio_to_reference` está orientado: por encima de 1 la zona está mejor que la región.
  - Los cortes van en `method` (`falta_below`, `cubierto_from`).
  - `proxy_note` declara lo que el indicador no mide (por ejemplo, centros no es lo mismo que plazas).
- **Buscador (D-202).**
  - `match_pct` es el % de encaje con la búsqueda: nunca se muestra como nota sobre 100 ni con barras.
  - `facts` trae 3–5 hechos tangibles, cada uno con su `confidence` y un `topic` para el icono.
  - `gap_highlights` trae 3 filas de «Qué falta aquí».
  - `all_zones` trae todas las zonas evaluadas para la coropleta; `match_pct: null` es desconocido, nunca 0.
  - Cada opción del Reality Check incluye `relaxed_scenario`: la web lo reenvía a `POST /search` al pulsarla.
  - `UNKNOWN` nunca cuenta como `PASS`. `results` solo trae zonas con todas las condiciones en `PASS`.
  - Las zonas que fallan una condición salen aparte, en `near_misses`, con `failed_constraints`.
  - En el Reality Check, `zones_if_relaxed = zones_passing + added_zones` para cada condición relajada, con las demás fijas.
- **Procedencia.** Todo resultado lleva `datasets` (`DatasetRef`) con el enlace al portal y `is_cm_open_data`. Este campo marca lo que cuenta como dataset de la Comunidad de Madrid (D-196).
- **Confidence** va de 0 a 1. En zonas pequeñas baja a 0,5 como máximo, y una confidence de 0 significa desconocido.
- **Errores.** Hoy la API los devuelve como `{"detail": {"code", "message"}}`, con los códigos de `ErrorCode`. `ErrorEnvelope` es el formato objetivo.
