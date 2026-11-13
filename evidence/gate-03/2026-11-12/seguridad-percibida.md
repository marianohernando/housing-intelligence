# DATA-020 F2 · Seguridad percibida por los vecinos (D-226)

Base local, 12 nov. Panel recargado desde el mismo Bronze (`11a758e6249d`) con el parser `madrid_district_panel-1.2.1`, más `hi-features compute` de las dos features. Son datos de contexto: no tienen enlace `fit` ni `gap_row`, así que ni el buscador ni «Qué falta» los leen (`tests/data/test_catalog.py::test_safety_is_context_never_a_score`).

## Valores de 2025 (de 0 a 10)

| Zona | Código | De noche | De día | Confidence |
|---|---|---|---|---|
| Villaverde | 2807917 | 4.9 | 6.8 | 0.9 |
| Puente de Vallecas | 2807913 | 5.1 | 7.0 | 0.9 |
| Usera | 2807912 | 5.2 | 6.9 | 0.9 |
| Carabanchel | 2807911 | 5.8 | 7.3 | 0.9 |
| Tetuán | 2807906 | 6.1 | 7.5 | 0.9 |
| Villa de Vallecas | 2807918 | 6.1 | 7.5 | 0.9 |
| San Blas-Canillejas | 2807920 | 6.1 | 7.4 | 0.9 |
| Latina | 2807910 | 6.2 | 7.5 | 0.9 |
| Ciudad Lineal | 2807915 | 6.2 | 7.7 | 0.9 |
| Madrid | 28079 | 6.4 | 7.8 | 0.95 |
| Centro | 2807901 | 6.5 | 7.9 | 0.9 |
| Vicálvaro | 2807919 | 6.5 | 7.9 | 0.9 |
| Moratalaz | 2807914 | 6.8 | 8.1 | 0.9 |
| Arganzuela | 2807902 | 7.0 | 8.1 | 0.9 |
| Hortaleza | 2807916 | 7.0 | 8.3 | 0.9 |
| Fuencarral-El Pardo | 2807908 | 7.2 | 8.3 | 0.9 |
| Chamartín | 2807905 | 7.3 | 8.4 | 0.9 |
| Moncloa-Aravaca | 2807909 | 7.3 | 8.4 | 0.9 |
| Retiro | 2807903 | 7.4 | 8.4 | 0.9 |
| Salamanca | 2807904 | 7.5 | 8.4 | 0.9 |
| Chamberí | 2807907 | 7.7 | 8.5 | 0.9 |
| Barajas | 2807921 | 7.7 | 8.6 | 0.9 |

Resto de la región: 178 municipios sin dato (`SOURCE_MISSING`), nunca 0.

## La API ya lo sirve (ruta existente)

`GET /api/v1/features/seguridad_percibida_noche/values?level=distrito` → 200, 21 distritos, `methodology_version` seguridad_percibida_noche@metric_value, datasets ['ayto_panel_indicadores_distritos_barrios'].
