# Housing Intelligence

Plataforma de inteligencia residencial para la Comunidad de Madrid (PUBLIC · PRO · DATA/API/MCP), preparada para DATAMAD 2026.

> Idealista sabe qué vivienda hay. Nosotros queremos saber qué vivienda hace falta.

## Estado (2026-10-22)
Sprint P1 en curso. Gate 0 y Gate 1 PASS; Gate 3 iniciado.
- Geografía canónica: 179 municipios, 246 distritos censales, 131 barrios, 4.417 secciones, 86.361 celdas H3.
- 10 datasets de la Comunidad de Madrid en producción local: geografía, población, hogares, vivienda, renta, alquiler y equipamientos (educación, atención primaria, mayores).
- 12 features municipales con lineage y confidence; mapa con coropletas y capas de equipamientos en `/map`.
- Ver `board/BOARD.md`, `evidence/` y `data/catalog/reports/`.

## Quickstart
```bash
cp .env.example .env          # rellenar POSTGRES_PASSWORD
make dev                      # db + redis + migraciones + seed
make lint typecheck test      # Gate 0
make catalog-harvest          # catálogo de fuentes candidatas
make catalog-curate           # aplica data/catalog/curation/*.yaml
make ingest-all               # geografía + todos los pipelines declarados
uv run hi-features compute    # Feature Store
```

## Estructura
`apps/` entrypoints (api FastAPI, web Next.js) · `packages/` contratos, dominio, db · `services/` ingestion y futuros workers · `data/catalog` registro de fuentes, datasets y features · `infra/` Docker y migraciones · `docs/` documentación completa · `evidence/` evidencias de Quality Gates.

## Fuentes
Datos abiertos de la Comunidad de Madrid como fuente estructural, complementados con Ayuntamiento de Madrid, CRTM, Catastro (INSPIRE), INE y datos.gob.es. Cada fuente tiene licencia y atribución en `data/catalog/sources/`.

## Trabajo previo a DATAMAD
Según §6 de las bases, este repositorio identifica el trabajo realizado antes del 7 de noviembre de 2026 mediante el tag `pre-datamad`.
