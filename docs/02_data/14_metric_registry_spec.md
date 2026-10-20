# Metric Registry Specification

## Objetivo
Que cada métrica sea una entidad del sistema con significado estable.

## Tabla conceptual

```sql
metric_id text primary key
human_name text
description text
domain text
unit text
direction text
aggregation_method text
geo_resolution_min text
temporal_resolution text
source_policy jsonb
null_policy text
normalization_method text
public_visible boolean
pro_visible boolean
sensitive boolean
methodology_version text
created_at timestamptz
updated_at timestamptz
```

## Ejemplo

```yaml
metric_id: pharmacy_access_10m_walk
human_name: Acceso a farmacias en 10 minutos andando
unit: count
direction: higher_is_better
aggregation_method: routing_count
geo_resolution_min: h3_r9
temporal_resolution: current
source_policy:
  preferred: official_pharmacies
  fallback: osm
null_policy: do_not_impute_if_no_coverage
public_visible: true
pro_visible: true
```

## Reglas
- No mezclar “dato observado” con “score derivado”.
- Los scores tienen documentación propia.
- No renombrar una métrica existente si cambia su significado: crear nueva versión.
