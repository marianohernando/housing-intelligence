# Feature Dictionary — Machine-readable Contract

## Source of truth
`data/catalog/features/*.yaml`

## Ejemplo

```yaml
feature_id: pharmacy_access_walk_10m
version: 1
human_name: Farmacias accesibles andando en 10 min
domain: health
type: derived
unit: count
direction: higher_is_better
geo_level: h3
time_semantics: current
sources:
  - dataset_id: cm_pharmacies
    role: primary
formula:
  method: network_isochrone_count
null_policy:
  no_coverage: unknown
  confirmed_zero: 0
confidence:
  inputs:
    - source_freshness
    - routing_coverage
public_use: true
pro_use: true
models:
  - residential_fit
tests:
  - non_negative
  - routing_monotonicity
limitations:
  - Does not measure pharmacy capacity.
```

## Markdown
Generar documentación humana desde el catálogo o validar sincronización CI.

## Quality gate
CI debe fallar si una feature productiva no tiene campos requeridos.
