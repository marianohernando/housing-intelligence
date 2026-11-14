# Minutos a pie hasta el ocio (D-236 §4) · Gate 3

`uv run hi-features compute --feature min_a_pie_bar --feature min_a_pie_restaurante --feature min_a_pie_gimnasio --feature min_a_pie_cultura` (14 nov, base local `housing_ocio`, ocio `2026-11-14-a3206c2d1d5f` con parser `osm-pois-1.1.0`, red peatonal de D-210): 4.974 filas por feature (4.417 secciones, 179 municipios, 246 distritos, 131 barrios de Madrid y la región), 4.950 con valor y 24 desconocidas explícitas (calles que no conectan con la red), ninguna a 0 sin datos. Mismo método, velocidad (4 km/h), calles de origen, reglas de nulos y niveles que `min_a_pie_parque` (test `test_leisure_features_walk_to_the_places_their_pipeline_publishes`).

| Feature | Grupo | Región (mediana) | Municipios ≤ 10 min | 10–30 min | > 30 min |
|---|---|---|---|---|---|
| `min_a_pie_bar` | Bares y cafeterías | 10,3 | 43 | 79 | 57 |
| `min_a_pie_restaurante` | Restaurantes | 8,4 | 66 | 69 | 44 |
| `min_a_pie_gimnasio` | Gimnasios y deporte | 11,8 | 28 | 94 | 57 |
| `min_a_pie_cultura` | Cultura (museos, bibliotecas, teatros, cines y centros culturales) | 18,9 | 12 | 83 | 84 |

`min_a_pie_cultura` sustituye a `min_a_pie_cine_teatro` (nunca publicada fuera de esta rama): la fila vieja se borró de `housing_ocio` antes de recalcular.

## Centro de Madrid frente a un pueblo pequeño

| Zona | Habitantes | Bares y cafeterías | Restaurantes | Gimnasios y deporte | Cultura |
|---|---|---|---|---|---|
| Centro (distrito) | — | 1.016 locales · 0,7 min | 1.498 · 0,6 min | 36 · 3,7 min | 133 · 2,3 min |
| Rascafría | 1.698 | 8 · 6,8 min | 18 · 5,1 min | 4 · 10,5 min | 3 · 9,3 min |
| Buitrago del Lozoya | 2.026 | 8 · 13,8 min | 10 · 9,9 min | 0 · 56,7 min | 2 · 13,1 min |
| Patones | 618 | 2 · 86,2 min | 14 · 68,6 min | 0 · 122,1 min | 1 · 81,2 min |
| La Hiruela | 88 | 1 · 16,1 min | 0 · 123,8 min | 0 · 136,2 min | 1 · 16,1 min |

Tiene sentido: en Centro hay un bar a menos de un minuto de la mitad de las calles; en Patones, con 14 restaurantes en OSM, la mitad de sus calles residenciales queda a más de una hora andando del más cercano (los minutos miden la distancia desde donde vive la gente, no cuántos locales hay). Las cifras de más de 30 minutos se leen como «no hay a un paseo» (la web muestra «a más de 60 min» por encima de una hora), no como una distancia útil; en los pueblos pequeños pueden ser locales que OSM no tiene (cobertura en `evidence/gate-01/2026-11-14/ocio.md`).

## Distritos de Madrid

| Distrito | Bares y cafeterías | Restaurantes | Gimnasios y deporte | Cultura | min bar | min rest. | min gim. | min cultura |
|---|---|---|---|---|---|---|---|---|
| Centro | 1016 | 1498 | 36 | 133 | 0,7 | 0,6 | 3,7 | 2,3 |
| Arganzuela | 188 | 235 | 39 | 33 | 2,1 | 1,9 | 5,1 | 6,6 |
| Retiro | 140 | 176 | 40 | 27 | 2,5 | 2,3 | 3,9 | 5,6 |
| Salamanca | 223 | 415 | 22 | 18 | 2,2 | 1,6 | 5,3 | 6,7 |
| Chamartín | 172 | 243 | 28 | 18 | 3,2 | 2,4 | 6,9 | 10,1 |
| Tetuán | 216 | 283 | 32 | 11 | 1,9 | 1,9 | 4,1 | 7,1 |
| Chamberí | 352 | 486 | 32 | 33 | 1,3 | 1,1 | 4,3 | 4,6 |
| Fuencarral-El Pardo | 214 | 265 | 63 | 22 | 5,9 | 5,0 | 9,0 | 21,5 |
| Moncloa-Aravaca | 153 | 221 | 54 | 49 | 7,9 | 7,1 | 9,4 | 18,9 |
| Latina | 246 | 132 | 42 | 18 | 3,0 | 4,0 | 7,6 | 10,5 |
| Carabanchel | 214 | 143 | 52 | 19 | 3,0 | 3,6 | 5,2 | 8,0 |
| Usera | 55 | 99 | 20 | 8 | 4,9 | 4,4 | 7,2 | 9,1 |
| Puente de Vallecas | 103 | 79 | 35 | 19 | 3,8 | 4,2 | 6,7 | 7,6 |
| Moratalaz | 72 | 35 | 11 | 4 | 3,8 | 5,1 | 6,9 | 12,5 |
| Ciudad Lineal | 170 | 130 | 36 | 8 | 3,1 | 3,4 | 5,6 | 10,2 |
| Hortaleza | 76 | 147 | 34 | 7 | 7,2 | 5,9 | 8,5 | 17,9 |
| Villaverde | 78 | 41 | 24 | 5 | 5,4 | 5,6 | 8,4 | 14,0 |
| Villa de Vallecas | 46 | 72 | 22 | 8 | 7,8 | 5,7 | 9,4 | 14,6 |
| Vicálvaro | 34 | 38 | 23 | 6 | 10,9 | 11,8 | 14,7 | 26,9 |
| San Blas-Canillejas | 63 | 115 | 28 | 11 | 5,5 | 5,1 | 9,1 | 11,4 |
| Barajas | 61 | 89 | 13 | 3 | 8,8 | 7,5 | 12,6 | 28,2 |

Locales dentro del polígono de cada distrito; minutos, mediana de las calles donde vive la gente. El centro histórico gana en todo; los distritos de la periferia con mucho suelo sin calles residenciales (Barajas, Vicálvaro, Fuencarral-El Pardo) tienen la cultura a más de 20 minutos.
