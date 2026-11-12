# Parques de OpenStreetMap (DATA-018, D-222) · Gate 1

`uv run hi-ingest run osm_parques` (parser `osm-parks-1.1.0`): extracto de Geofabrik descargado el 12 nov (`https://download.geofabrik.de/europe/spain/madrid-latest.osm.pbf`, ODbL) y `data/catalog/corrections/parks.yaml`; versión `2026-11-12-199d4d500a72`. Calidad en verde: `osm_parques/quality_report.json`; recuentos: `osm_parques/row_counts.json`.

| | |
|---|---|
| Áreas `leisure=park` leídas | 6.367 |
| Cerradas al público (`access` no, private o customers) | 54 |
| Menores de 1 ha (umbral del indicador de la OMS) | 4.911 |
| Incluidos con fuente oficial (D-222 §5) | 2: Casa de Campo y Quinta de Torre Arias |
| **Parques publicados** | **1.404** (1.398 de OSM con 8.423 ha en 80 municipios, más los 2 incluidos; 1.400 dentro de una sección censal) |
| Sin nombre en OSM | 711 («Parque sin nombre») |
| Puntos de borde (cada 50 m) | 70.573 (1,5 MB de atributos) |
| En cuarentena | 0 |

Comprobación con parques conocidos de Madrid capital (superficie en OSM): Juan Carlos I 144 ha, El Retiro 118 ha, Parque del Oeste 76 ha, Madrid Río 69 ha, Cuña Verde de O'Donnell 60 ha, Dehesa de la Villa 58 ha, Enrique Tierno Galván 42 ha. **La Casa de Campo** está en OSM como `landuse=forest` (relación 1946885) y la **Quinta de Torre Arias** como `leisure=garden` (vía 22755919): entran por `parks.yaml` con la lista oficial del Ayuntamiento como fuente (D-222 §5).

`GET /api/v1/places?category=green&admin_unit_id=ES.28.MUN.28079` → 200, 507 parques en Madrid capital (TestClient sobre la base local).

## Comparación con la lista oficial del Ayuntamiento (D-222 §5)

Fuente: «Principales parques y jardines municipales» (datos.madrid.es, `200761-0-parques-jardines.csv`, consultado el 12 nov): 208 entradas, 203 con coordenadas. Para cada una, distancia al parque de OSM de 1 ha o más más cercano (envolvente de sus puntos de borde).

- 169 dentro o a menos de 150 m de un parque de OSM.
- 34 más lejos. Revisadas una a una contra las áreas de OSM con el mismo nombre que contienen su punto:
  - **Casa de Campo** (`landuse=forest`, 1.373 ha) y **Quinta de Torre Arias** (`leisure=garden`, 18 ha): incluidas con fuente oficial.
  - Quinta de los Molinos (21 ha) y Pan Bendito (6,7 ha) sí están en OSM como parque; la coordenada del Ayuntamiento cae a unos 300 m (su dirección postal).
  - El resto son jardines y plazas de menos de 1 ha en OSM (Jardín del Duque de Ahumada 0,5 ha, Parque Juan XXIII 0,9 ha, Parque San Juan Bautista 0,8 ha…) o no tienen área en OSM: fuera por el umbral de la OMS, no por un error.
- No se incluye el Monte de El Pardo (Patrimonio Nacional, acceso restringido): no está en la lista del Ayuntamiento.
