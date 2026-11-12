# Minutos a pie hasta un parque (D-222 §6) · Gate 3

`uv run hi-features compute --feature min_a_pie_parque --feature pct_calle_parque_5min` (12 nov, base local, parques `2026-11-12-199d4d500a72`): 4.843 filas por feature (secciones, municipios, distritos y la región), 4.819 con valor y 24 desconocidas explícitas (calles que no conectan con la red), ninguna a 0 sin datos.

## Distritos de Madrid

| Distrito | Mediana de minutos | % de calle a 5 min | Confidence |
|---|---|---|---|
| Moratalaz | 1.8 | 87 | 0.99 |
| Carabanchel | 2.9 | 73 | 1.00 |
| Villa de Vallecas | 3.2 | 65 | 1.00 |
| Usera | 3.3 | 73 | 1.00 |
| Puente de Vallecas | 3.4 | 75 | 1.00 |
| Latina | 3.4 | 66 | 0.99 |
| Arganzuela | 3.4 | 69 | 1.00 |
| Hortaleza | 3.4 | 66 | 1.00 |
| Villaverde | 3.5 | 67 | 1.00 |
| Fuencarral-El Pardo | 3.8 | 60 | 1.00 |
| Retiro | 4.1 | 61 | 1.00 |
| Vicálvaro | 4.3 | 56 | 0.99 |
| Moncloa-Aravaca | 4.8 | 52 | 1.00 |
| San Blas-Canillejas | 4.8 | 51 | 1.00 |
| Barajas | 4.8 | 51 | 0.99 |
| Ciudad Lineal | 5.0 | 50 | 1.00 |
| Salamanca | 6.5 | 38 | 1.00 |
| Chamartín | 6.7 | 31 | 1.00 |
| Centro | 7.1 | 31 | 1.00 |
| Tetuán | 7.6 | 29 | 1.00 |
| Chamberí | 8.4 | 20 | 1.00 |

## Municipios

| Mediana de minutos | Municipios |
|---|---|
| ≤ 10 | 49 |
| 10–30 | 29 |
| > 30 (sin parque urbano a un paseo) | 101 |

Ejemplos: Móstoles y Madrid 4 min, Getafe 5, Alcalá de Henares y Collado Villalba 6, Aranjuez 7, Torrelodones 8; Cercedilla 62, Chinchón 192, Rascafría 343, Patones 363. Los de más de 30 minutos son, sobre todo, pueblos rodeados de campo: el indicador mide parques urbanos, no el verde (D-222 §6).
