# Transport Ingestion Specification

## Fuente core
CRTM Open Data.

## Modos
- Metro;
- EMT;
- autobuses urbanos;
- interurbanos;
- Metro Ligero/Tranvía;
- Cercanías.

## Formatos
- GTFS;
- SHP/KML;
- CSV;
- GeoJSON/GeoServices/API según dataset.

## Pipeline
### Static
- stops;
- routes;
- trips;
- stop_times;
- calendars;
- transfers.

### Realtime / incidents
Añadir donde exista fuente reusable:
- delays;
- service alerts;
- disruptions.

## Features
- nearest_stop_time;
- service_frequency;
- direct_destination_count;
- transfer_count;
- first/last service;
- multimodal_access;
- accessible_station attributes when available.

## Regla
No scrapear horarios si existe GTFS oficial.

## Estado DATAMAD (D-196, nivel A)
- Implementado: los 6 GTFS estáticos del CRTM, publicados también en el Portal de Datos Abiertos de la CM, se cargan con el pipeline declarativo `gtfs_feed` (`data/catalog/pipelines/crtm_gtfs_*.yaml`).
- Salida: una fila por parada o estación en `place_master` (`category=transport`, `subcategory` = modo), con `departures_day`, `departures_peak_per_hour`, `headway_peak_min` + `headway_basis`, `first_departure`/`last_departure`, `routes`/`n_routes`, `gtfs_wheelchair_boarding` (el código tal cual: el CRTM no usa el sentido del estándar, D-223), `service_date` y `feed_end_date`. Metro, Metro Ligero y Cercanías añaden `step_free`, `topology_station_ids` y `step_free_source` desde la topología del CRTM (D-223).
- Día de referencia: el martes mediano dentro de la vigencia del feed. Punta: 07:00–09:00.
- Calidad: cuarentena fuera de la región, servicio en punta plausible (≤1.200 salidas/h; headway ≥0,5 min), `stop_times` legibles y aviso si el feed está vencido. Casos golden en `data/fixtures/golden/transport_golden.yaml`.
- Pendiente: nivel B (tiempo a polos de empleo, CORE-009), transbordos y número de destinos directos, y tiempo real.
