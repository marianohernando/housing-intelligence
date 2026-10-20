# Ingestion Pipeline Specification

## Fases

```text
DISCOVER
→ FETCH
→ SNAPSHOT
→ SCHEMA CHECK
→ PARSE
→ NORMALIZE
→ GEO-RESOLVE
→ ENTITY RESOLUTION
→ QUALITY CHECK
→ PUBLISH SILVER
→ BUILD FEATURES
```

## Directorios sugeridos

```text
data/
  raw/
  bronze/
  silver/
  gold/
  quarantine/
```

En producción estos pueden ser buckets/objetos, no necesariamente filesystem.

## Idempotencia
La misma versión del dataset procesada dos veces debe producir el mismo resultado.

## Checkpoints
Guardar:
- checksum;
- parser version;
- row counts;
- schema hash;
- quality metrics.

## Quarantine
Las filas inválidas no se borran.
Se guardan con:
- razón;
- valor original;
- parser;
- source row reference.

## Incremental
Si una fuente soporta actualización incremental:
- usar `updated_since`;
- upsert por ID canónico;
- invalidar solo features dependientes.
