# Local Development

## Objetivo
Un comando debe levantar la plataforma local.

## Docker Compose
Servicios previstos:
- postgres/postgis/pgvector;
- redis;
- api;
- web;
- worker;
- routing;
- optional object storage.

## Comandos objetivo

```bash
make dev
make test
make lint
make seed
make ingest SAMPLE_DATASET
make eval
```

## Seed
Debe existir un dataset pequeño de ejemplo para:
- 3–5 zonas;
- POIs;
- población;
- alquiler;
- perfiles.

Permite desarrollar sin descargar Madrid completo.

## Entornos
- local;
- test;
- staging;
- production.
