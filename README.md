# Housing Intelligence

Plataforma de inteligencia residencial para la Comunidad de Madrid (PUBLIC · PRO · DATA/API/MCP), preparada para DATAMAD 2026.

> Idealista sabe qué vivienda hay. Nosotros queremos saber qué vivienda hace falta.

## Estado
Sprint P0 — Control Tower + Data Recon. Ver `board/BOARD.md` y `evidence/`.

## Quickstart
```bash
cp .env.example .env          # rellenar POSTGRES_PASSWORD
make dev                      # db + redis + migraciones + seed
make lint typecheck test      # Gate 0
make catalog-harvest          # catálogo de fuentes candidatas
make ingest DATASET=cm_secciones_censales
```

## Estructura
`apps/` entrypoints (api FastAPI, web Next.js) · `packages/` contratos, dominio, db · `services/` ingestion y futuros workers · `data/catalog` registro de fuentes, datasets y features · `infra/` Docker y migraciones · `docs/` documentación completa · `evidence/` evidencias de Quality Gates.

## Fuentes
Datos abiertos de la Comunidad de Madrid como fuente estructural, complementados con Ayuntamiento de Madrid, CRTM, Catastro (INSPIRE), INE y datos.gob.es. Cada fuente tiene licencia y atribución en `data/catalog/sources/`.

## Trabajo previo a DATAMAD
Según §6 de las bases, este repositorio identifica el trabajo realizado antes del 7 de noviembre de 2026 mediante el tag `pre-datamad`.
