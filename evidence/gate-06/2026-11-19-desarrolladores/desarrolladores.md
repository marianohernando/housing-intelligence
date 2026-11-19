# Para desarrolladores: la API y el MCP (19 nov, D-249)

Rama `claude/f10-dev-docs`, desde `claude/sprint-1-public` en `396d8f6`. La página `/desarrolladores` documenta la API pública y el MCP, gratis para todos (decisión de Mariano del 19 nov), y el MCP suma dos herramientas de inversores, `ficha_inversor` y `viabilidad`. Decisión: D-249. Textos: `pitch/textos_web.md` §12.

## Los ejemplos, contra producción

Una petición por ejemplo contra `https://vidafacil-madrid.vercel.app` el 19 nov, entre las 10:53 y las 10:59: **17 peticiones**. Los 13 ejemplos de la página, la descripción OpenAPI, la salud, un 422 buscado y una primera versión del ejemplo de viabilidad. Todas dieron lo esperado; **nada roto**.

| Petición | HTTP | Tamaño | Tiempo | Lo que se comprobó |
|---|---|---|---|---|
| `GET /api/v1/openapi.json` | 200 | 79 KB | 0,45 s | 13 rutas de datos y 2 de salud, también las 3 de inversores |
| `GET /api/v1/health` | 200 | 225 B | 0,12 s | `status: ok` |
| `POST /api/v1/search` (ejemplo) | 200 | 140 KB | 2,32 s | `fit-0.9`, datos del 2026-11-19, 10 resultados (Puente de Vallecas, 97 %) |
| `POST /api/v1/search/barrios` (Ciudad Lineal) | 200 | 42 KB | 0,29 s | 9 barrios (Quintana primero) |
| `GET /api/v1/gaps/municipio/28106` (Parla) | 200 | 36 KB | 0,35 s | `gap-0.3`; farmacia y vivienda FALTA, el resto JUSTO |
| `GET /api/v1/gaps?level=municipio&row=farmacia` | 200 | 78 KB | 0,35 s | 179 zonas: 5 FALTA, 127 JUSTO, 47 CUBIERTO |
| `GET /api/v1/gaps/impact` | 200 | 24 KB | 0,40 s | `impact-0.1` |
| `GET /api/v1/datasets?cm_only=true` | 200 | 26 KB | 0,25 s | 39 conjuntos de la Comunidad de Madrid |
| `GET /api/v1/features?level=distrito` | 200 | 9 KB | 0,19 s | 8 indicadores de distrito |
| `GET /api/v1/features/suelo_publico_vivienda_m2/values?level=distrito` | 200 | 20 KB | 0,16 s | los 21 distritos |
| `GET /api/v1/geo/admin-units?level=distrito&parent=ES.28.MUN.28079` | 200 | 31 KB | 0,29 s | los 21 distritos, sin avisos |
| `GET /api/v1/places?category=pharmacy&admin_unit_id=ES.28.DIS.2807905` | 200 | 50 KB | 1,19 s | 114 farmacias de Chamartín, 1 página |
| `GET /api/v1/investors/zones` | 200 | 76 KB | 0,34 s | `viability-0.1`; 108 barrios del piloto |
| `GET /api/v1/investors/zones/ES.28.BAR.28079164` | 200 | 59 KB | 0,86 s | Pinar del Rey (Hortaleza), PEM 644 €/m², sin avisos |
| `POST /api/v1/investors/viability` (suelo a 2.200 €/m², primera versión) | 200 | 2 KB | 0,12 s | tres escenarios «Sale» |
| `POST /api/v1/investors/viability` (40 m²) | 422 | 153 B | 0,12 s | `buildable_m2`: «greater than or equal to 50» |
| `POST /api/v1/investors/viability` (ejemplo de la página, suelo a 3.200 €/m²) | 200 | 2 KB | 0,12 s | 15,1 % «Ajustar», 22,8 % «Sale», 5,6 % «No sale», como D-248 §10 |

## Las dos herramientas MCP, en la base local

Sobre `housing`, en transacción de solo lectura: `ficha_inversor` con «pinar del rey» da la misma ficha que la ruta (59 KB; 0,34 s, 1,3 s la primera vez), y `viabilidad` con el ejemplo de la página da 15,1 % «Ajustar», 22,8 % «Sale» y 5,6 % «No sale» (3 KB, 0,01 s).

## Invariante

`scripts/golden_search.py` sobre `housing`: **10 de 10**, con una salida idéntica a la de la base (`diff` vacío).
