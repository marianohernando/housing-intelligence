# Ocio de OpenStreetMap (D-236) · Gate 1

`uv run hi-ingest run osm_ocio --local data/bronze/datasets/osm_red_peatonal/e6fa128706ac/madrid-latest.osm.pbf` (parser `osm-pois-1.1.0`, base local `housing_ocio`): el mismo extracto de Geofabrik que la red peatonal (descargado el 11 nov, ODbL); versión `2026-11-14-a3206c2d1d5f`. Calidad en verde: `osm_ocio/quality_report.json`; recuentos: `osm_ocio/row_counts.json`.

| Grupo de «Ocio» | Etiqueta de OSM | Locales | Sin nombre en OSM |
|---|---|---|---|
| Bares y cafeterías | `amenity=bar` | 2.343 | 144 |
| | `amenity=pub` | 1.632 | 62 |
| | `amenity=cafe` | 2.226 | 144 |
| Restaurantes | `amenity=restaurant` (la comida rápida, `fast_food`, no cuenta) | 7.678 | 190 |
| Gimnasios y deporte | `leisure=fitness_centre` | 556 | 43 |
| | `leisure=sports_centre` (polideportivos municipales incluidos) | 1.182 | 333 |
| Cultura | `tourism=museum` | 196 | 5 |
| | `amenity=library` | 260 | 16 |
| | `amenity=theatre` | 259 | 29 |
| | `amenity=cinema` | 77 | 1 |
| | `amenity=arts_centre` | 98 | 4 |
| **Total publicado** | | **16.507** | 971 |

- Nodos y áreas (vías cerradas y multipolígonos, con un punto dentro del área). Un local con dos etiquetas declaradas toma la primera de `data/catalog/pipelines/osm_ocio.yaml`: un museo con cafetería es museo (2 centros culturales pasaron a museo al añadir `tourism=museum`).
- Cerrados al público (`access` = `no` o `private`): 28, fuera. En cuarentena: 0. Dentro de una sección censal: 16.490 (17 caen fuera de todas, en el borde de la región).
- De cada local solo se guarda su nombre, su punto y su etiqueta (`attributes.osm_tag`); nunca dirección, teléfono ni horario.
- Antes de la ampliación (parser `osm-pois-1.0.0`, mismo extracto) había 16.053 locales y el grupo se llamaba «Cines y teatros» (cines, teatros y centros culturales). La ampliación a «Cultura» viene del feedback de usuarios de prueba (D-236).

## Cobertura de OSM por tamaño de municipio

Municipios con al menos un local de cada grupo y mediana municipal de minutos a pie (`min_a_pie_*`, D-236 §4). Población: `poblacion_total` (padrón, Feature Store).

| Población | Municipios | Bares | Restaurantes | Gimnasios | Cultura | Mediana min bar | Mediana min cultura |
|---|---|---|---|---|---|---|---|
| < 1.000 | 42 | 21 (50 %) | 28 (67 %) | 17 (40 %) | 10 (24 %) | 44,9 | 88,6 |
| 1.000–5.000 | 53 | 34 (64 %) | 38 (72 %) | 35 (66 %) | 23 (43 %) | 24,4 | 73,1 |
| 5.000–20.000 | 47 | 39 (83 %) | 47 (100 %) | 46 (98 %) | 43 (91 %) | 14,0 | 18,1 |
| 20.000–100.000 | 26 | 26 (100 %) | 26 (100 %) | 26 (100 %) | 23 (88 %) | 12,5 | 21,1 |
| ≥ 100.000 (Madrid incluido) | 11 | 11 (100 %) | 11 (100 %) | 11 (100 %) | 11 (100 %) | 6,6 | 15,6 |

Municipios sin ningún local en OSM: bares 48, restaurantes 29, gimnasios 44, cultura 69. Casi todos son pueblos de menos de 5.000 habitantes (Madarcos, Robregordo, Somosierra, La Hiruela…), pero no solo: Brunete (11.261 hab.) no tiene ningún bar en OSM, y algunas ciudades tienen muy pocos para su tamaño (Parla, 138.012 hab.: 13 bares y cafeterías; Valdemoro, 86.078: 5). **En OSM un pueblo sin bar casi siempre es un bar sin mapear, no un pueblo sin bar.**

## Cultura frente a dos datasets abiertos de la Comunidad de Madrid

El portal no publica un censo con coordenadas de bares, restaurantes, gimnasios ni cines. Para cultura publica dos datasets que sirven para validar (no para geolocalizar):

**Bibliotecas** — «Relación de Bibliotecas. Directorio de Bibliotecas de la Comunidad de Madrid» (`spacm_listado_bibliotecas_servicios_lectura`, CC BY, consultado el 14 nov). Tiene dirección y localidad pero no coordenadas: ponerlas en el mapa exigiría geocodificar 809 direcciones, fuera de este alcance. Comparación por municipio de las 211 bibliotecas públicas de punto fijo (207 casan con 97 municipios por el nombre de la localidad; 4 no casan por erratas de la fuente) con las bibliotecas de OSM:

| Población | Municipios con biblioteca pública (CM) | De ellos, con biblioteca en OSM | Bibliotecas CM | Bibliotecas OSM |
|---|---|---|---|---|
| 1.000–5.000 | 17 | 6 (35 %) | 17 | 6 |
| 5.000–20.000 | 43 | 37 (86 %) | 44 | 40 |
| 20.000–100.000 | 26 | 23 (88 %) | 42 | 45 |
| ≥ 100.000 | 11 | 11 (100 %) | 104 | 158 |

En total 77 de 97 municipios (79 %). En las ciudades OSM tiene más bibliotecas que el directorio de públicas porque también cuenta las universitarias, las especializadas y las de otras instituciones; en los pueblos de menos de 5.000 habitantes OSM no tiene dos de cada tres bibliotecas públicas.

**Museos** — «Museos por municipios. Municipios» (tabla 1923960 del Instituto de Estadística, CC BY, año 2025): 199 museos en 54 municipios. OSM tiene 196 museos (195 dentro de un municipio) en 53 municipios; Madrid, 109 según la CM y 99 en OSM. 32 de los 54 municipios con museo según la CM tienen alguno en OSM (59 %); 22 no, casi todos con un solo museo (Chinchón, Manzanares el Real, Navalcarnero, Tres Cantos, Valdemoro…).

Conclusión: en las ciudades y municipios de más de 5.000 habitantes OSM es una buena aproximación (86–100 % de los municipios con biblioteca pública la tienen en OSM); en los pueblos pequeños faltan locales. Por eso el ocio solo puntúa si la persona lo marca, «Imprescindible» empieza sin marcar, un local a más de un paseo puntúa 0 con confianza ≤ 0,5 y la web lo dice («en los pueblos pequeños puede faltar algún local»). Ver D-236.

## Límites de esta evidencia

- Las comparaciones con los datasets de la CM y la tabla de cobertura se hicieron con un script de exploración, no versionado (como la comparación de parques de D-222): casa la localidad del directorio con el nombre oficial del municipio sin tildes y con el artículo delante («Acebeda (La)» → «la acebeda»), y el código de la tabla de museos con el código INE. Los datasets de la CM se leyeron, no se cargan en la base.
- Un local dibujado a la vez como nodo y como área, o dos veces con el mismo nombre, cuenta dos veces: hay 91 parejas con el mismo nombre y tipo a menos de 50 m (el Ateneo de Madrid sale dos veces en la lista de Centro). No cambia ningún minuto a pie.
- OSM puede tener locales que ya cerraron y no distingue bibliotecas públicas de privadas con acceso abierto.
