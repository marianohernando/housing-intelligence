# Dataset Contract

## Objetivo
Cada dataset es un asset versionado, no “un CSV que descargamos”.

## Identidad

```yaml
dataset_id: cm_health_facilities
source_id: comunidad_madrid
name: Centros sanitarios
domain: health
owner: Comunidad de Madrid
format: csv
geography: point
refresh_policy: daily
```

## Versionado

Cada ingestión produce:

```text
dataset_version
retrieved_at
source_modified_at
checksum
row_count
schema_hash
quality_status
```

## Estados
- `DISCOVERED`
- `REVIEWED`
- `INGESTING`
- `VALIDATED`
- `PRODUCTION`
- `DEGRADED`
- `RETIRED`

## Contrato mínimo
Un dataset en `PRODUCTION` debe tener:
- schema conocido;
- test de filas;
- clave o estrategia de deduplicación;
- política de nulos;
- geografía resuelta;
- licencia;
- lineage;
- alertas de cambio de esquema.

## Fallos
Un cambio de schema NO debe romper silenciosamente el feature store.
El pipeline debe:
1. detener asset afectado;
2. marcar `DEGRADED`;
3. conservar última versión válida;
4. generar alerta.
