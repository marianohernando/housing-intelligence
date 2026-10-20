# Entity Resolution Specification

## Problema
Una misma entidad puede aparecer en:
- Comunidad de Madrid;
- Ayuntamiento;
- OSM;
- Catastro;
- API comercial;
- web oficial.

## Entidades iniciales
- `place_master`
- `building_master`
- `parcel_master`
- `school_master`
- `health_facility_master`
- `social_facility_master`
- `transport_stop_master`

## Ejemplo `place_master`

```sql
canonical_place_id uuid primary key
canonical_name text
category_id text
geom geometry(Point, 4326)
address_normalized text
official_source_id text
official_entity_id text
confidence numeric
status text
created_at timestamptz
updated_at timestamptz
```

## Tabla de aliases

```sql
place_source_alias
- canonical_place_id
- source_id
- external_id
- source_name
- source_address
- source_geom
- match_method
- match_score
```

## Matching pipeline
1. exact external ID si existe;
2. identificador oficial;
3. address normalization;
4. geospatial radius;
5. normalized name;
6. category compatibility;
7. fuzzy score;
8. JEV/LLM solo en casos ambiguos.

## Umbrales iniciales
- >0.95: auto-merge.
- 0.80–0.95: merge con reglas adicionales.
- <0.80: mantener separado o revisión.

## Regla
Nunca fusionar dos entidades solo por nombre.
