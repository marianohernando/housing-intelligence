# Parques de OpenStreetMap (DATA-018, D-222) · Gate 1

`uv run hi-ingest run osm_parques` (parser `osm-parks-1.0.0`): extracto de Geofabrik descargado el 12 nov (`https://download.geofabrik.de/europe/spain/madrid-latest.osm.pbf`, ODbL), versión `2026-11-12-b8d92f0485d9`. Calidad en verde: `osm_parques/quality_report.json`; recuentos: `osm_parques/row_counts.json`.

| | |
|---|---|
| Áreas `leisure=park` leídas | 6.367 |
| Cerradas al público (`access` no, private o customers) | 54 |
| Menores de 1 ha (umbral del indicador de la OMS) | 4.911 |
| **Parques publicados** | **1.402** (8.423 ha, 80 municipios; 1.398 dentro de una sección censal) |
| Sin nombre en OSM | 711 («Parque sin nombre») |
| Puntos de borde (cada 50 m) | 70.573 (1,5 MB de atributos) |
| En cuarentena | 0 |

Comprobación con parques conocidos de Madrid capital (superficie en OSM): Juan Carlos I 144 ha, El Retiro 118 ha, Parque del Oeste 76 ha, Madrid Río 69 ha, Cuña Verde de O'Donnell 60 ha, Dehesa de la Villa 58 ha, Enrique Tierno Galván 42 ha. **La Casa de Campo no está:** OSM la etiqueta `landuse=forest` (relación 1946885), no `leisure=park` (D-222 §4).

`GET /api/v1/places?category=green&admin_unit_id=ES.28.MUN.28079` → 200, 507 parques en Madrid capital (TestClient sobre la base local).
