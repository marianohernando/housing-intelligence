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
