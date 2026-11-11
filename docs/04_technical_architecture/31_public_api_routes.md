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
| `GapRowMap` en `GapRowMapResponse` | `hi_contracts/public/gaps.py`, `responses.py` | `data/schemas/api/gap_row_map_response.schema.json` |
| `DatasetList` en `DatasetListResponse` | `hi_contracts/public/common.py`, `responses.py` | `data/schemas/api/dataset_list_response.schema.json` |
| Error | `hi_contracts/api/envelope.py` | `data/schemas/api/error_response.schema.json` |

- Los schemas se regeneran con `make schemas`. CI falla si no están al día.
- Hay ejemplos con zonas e indicadores reales en `data/fixtures/contracts/` (son fixtures: solo para tests y desarrollo).
- Las filas de la lista salen del Feature Dictionary: cada feature declara su fila en `gap_row`, con su título, la unidad en palabras y el proxy. La API no tiene ningún id de feature escrito a mano.

## Rutas

| Método y ruta | Entrada | Salida | Estado |
|---|---|---|---|
| `GET /api/v1/gaps/{level}/{code}` | `level`: `municipio`, `distrito` (los 21 de Madrid capital, códigos 2807901–2807921) o `seccion_censal` · `code`: código INE | `ZoneGapListResponse` | **Funciona desde el 11 nov** (esqueleto andante): filas de colegio y centro de salud por municipio con datos reales, frente a la referencia regional del Feature Store. **Desde DATA-012 también por distrito de Madrid**: la población del distrito sale del padrón municipal (D-209) y cada fila cita también los datasets de la referencia regional. Las filas que aún no están calculadas a un nivel no aparecen (no son SIN DATOS) y la respuesta trae un aviso por cada una en `warnings` (ver «Lista de lo que falta»). **Desde GAP-001 F1** las filas traen en `extra_indicators` los minutos a pie hasta el más cercano (CORE-005). **Desde F3a** hay cinco filas por municipio y por distrito: escuela infantil, colegio, centro de salud, mayores y farmacia. Cada fila cuenta los mismos lugares que sus minutos a pie (F2: colegios con primaria, públicos o concertados). Farmacia añade la ratio oficial de la CM, solo por municipio, y mayores las plazas de residencia. **Desde F3b están las 6 filas.** Vivienda compara las viviendas de más de 90 m² con los hogares de 4 o más personas; por distrito sale `SIN_DATOS` (`SOURCE_MISSING`) porque la CM no publica esas tablas por distrito. Escuela infantil añade las aulas de infantil y los nacimientos (solo municipio) y vivienda el % en alquiler y el tamaño medio del hogar |
| `GET /api/v1/gaps?level=municipio&row=colegio` | `level`: `municipio`, `distrito` o `seccion_censal` (otro → 422 `OUT_OF_COVERAGE`) · `row`: una clave de `GapRowKey` (otra → 422) | `GapRowMapResponse`: la fila en todas las zonas del nivel, con `status`, `value`, `ratio_to_reference`, `confidence` y `null_reason` por zona, más `counts`, la referencia regional, los cortes (`method`) y los datasets | **Funciona desde GAP-001 F4.** Es el mapa de la lista: usa el mismo indicador, la misma referencia y los mismos cortes que `/gaps/{level}/{code}`, así que el color de cada zona coincide con su fila (lo comprueba un test). `zones[].admin_unit_id` es el `promoteId` de `/geo/admin-units`. Una fila que aún no está calculada a ese nivel devuelve `zones: []` y el aviso `INSUFFICIENT_DATA` de siempre (hoy, todas por sección censal). Vivienda por distrito sale con las 21 zonas en `SIN_DATOS`. Unos 179 municipios caben en unos 40 KB |
| `POST /api/v1/search` | `ScenarioState` en el cuerpo | `SearchResponse` | Prevista (CORE-003). CORS ya admite `POST`. Las zonas son municipios con Madrid capital por distritos (D-200) |
| `GET /api/v1/datasets?cm_only=true` | `cm_only` (opcional) | `DatasetListResponse`: `total`, `cm_open_data_count` y los `DatasetRef` con versión | **Funciona desde el 11 nov**. Lista los datasets con una versión válida (QA superado): hoy 22, de los que 21 son CM |
| `GET /api/v1/geo/admin-units?level=&parent=` | `level` · `parent` (opcional): `admin_unit_id` del padre directo (`?level=distrito&parent=ES.28.MUN.28079` → los 21 distritos de Madrid) · `simplify_m` | geometrías GeoJSON | Existe. **Desde el 11 nov,** `properties.name` viene legible («Las Rozas de Madrid»), como `ZoneRef.name`, y se puede filtrar por padre. El padre de una sección es su barrio o, si no tiene, su distrito. Un padre sin hijos devuelve una lista vacía con aviso en `warnings` |
| `GET /api/v1/features`, `GET /api/v1/features/{id}/values?level=` | — | catálogo y valores de features | Existe |
| `GET /api/v1/places?category=&admin_unit_id=&subcategory=` | `category` (obligatoria) · `admin_unit_id` (opcional): un municipio, distrito o sección (`ES.28.DIS.2807905`) · `subcategory` (opcional, repetible: `?subcategory=metro&subcategory=cercanias`; algunas subcategorías llevan comas, por eso no se separan por comas) | equipamientos como puntos GeoJSON | **Filtros desde el 11 nov.** Un lugar está en la zona en la que lo cuentan los features: su municipio, o el distrito o la sección de la sección censal en la que cae. Barrio u otro nivel → 422 `OUT_OF_COVERAGE`; unidad desconocida → 404. **Paginada:** 5.000 lugares por página (unos 1,4 MB; Vercel responde 4,5 MB como máximo), con `?page=` (desde 1) y `data.total`, `data.page` y `data.pages`. Si quedan páginas, `warnings` dice cómo pedir la siguiente o filtrar; una página fuera de rango → 422. Hoy solo transporte (14.982) pasa de una página; la web debería pedirlo siempre filtrado |

## Reglas que la web puede dar por hechas
- **Zonas.** `ZoneRef.admin_unit_id` coincide con `promoteId` de las capas de `geo/admin-units`, y `name` ya viene legible («Las Rozas de Madrid», «Fuencarral-El Pardo»). Los distritos de Madrid traen `municipio_ine = 28079`.
- **Presupuesto (D-203).** `budget.kind` es `rent` (€/mes) o `buy` (€). La compra es orientativa; sin fuente fiable, su condición sale `UNKNOWN` con la explicación.
- **CORS.** Los orígenes se configuran con `CORS_ORIGINS` al arrancar la API (por ejemplo `CORS_ORIGINS='["http://localhost:3011"]'`). Se admiten `GET` y `POST`.
- **Lista de lo que falta.**
  - `SIN_DATOS` aparece si y solo si `indicator.value` es `null`, y entonces `indicator.null_reason` dice por qué. Un 0 es un dato real (ningún centro en un registro exhaustivo).
  - `ratio_to_reference` está orientado: por encima de 1 la zona está mejor que la región.
  - Los cortes van en `method` (`falta_below`, `cubierto_from`, `confidence_level`). **Desde GAP-001 F5 (`gap-0.2`, D-213):**
    - `reference` es la tasa de los municipios del mismo tipo (rural o urbano, Ley 45/2007) y `reference_label` lo dice («Municipios urbanos de la Comunidad de Madrid»). La región entera va en `regional_reference` y en la explicación.
    - FALTA exige ratio < 0,8 y que la falta sea significativa (Poisson exacto al 95 %); CUBIERTO es ratio ≥ 1; el resto es JUSTO.
    - `reliable: false` marca una zona demasiado pequeña para esa fila (menos de 3,7 casos esperados): nunca sale FALTA y la web debería mostrarla como «poco fiable», con su valor. En `/gaps?level=&row=`, cada zona trae su `reference`, `reference_label` y `reliable`.
    - Ratios muy altos (La Acebeda, vivienda: 10.700 por 100 hogares, un solo hogar grande) son reales; se leen mejor como «más de 10 veces la referencia».
  - `proxy_note` declara lo que el indicador no mide (por ejemplo, centros no es lo mismo que plazas).
  - `extra_indicators` acompaña al indicador principal sin cambiar el estado de la fila. Hoy son los minutos a pie hasta el servicio más cercano: la mediana de las calles de la zona a 4 km/h (D-210, D-211). No tienen estado ni referencia propios. `value: null` con su `null_reason` es desconocido, nunca 0. Un extra que aún no está calculado a ese nivel no aparece. Sus datasets, como la red peatonal de OSM (no CM), se suman a los `datasets` de la fila. Los minutos muy altos (hasta unos 380 en pueblos sin colegio) se leen mejor como «más de 60 min».
  - Una fila puede estar en `SIN_DATOS` aunque la zona exista: la vivienda por distrito, o un municipio sin niños de 0 a 4 años (`NOT_APPLICABLE`). La fila aparece con su `null_reason`; no es lo mismo que una fila que falta.
  - Las 6 filas esperadas son las de `GapRowKey`. Por cada una que aún no esté calculada a ese nivel, `warnings` trae `INSUFFICIENT_DATA: row <fila> not computed at <nivel> level yet` (por ejemplo, `row farmacia … distrito`). La web puede leer la clave de la fila de ese texto o compararlas con `rows`.
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
