# Housing Intelligence

Plataforma de inteligencia residencial para la Comunidad de Madrid (PUBLIC · PRO · DATA/API/MCP), preparada para DATAMAD 2026.

> Idealista sabe qué vivienda hay. Nosotros queremos saber qué vivienda hace falta.

## Estado (2026-11-11)
Fase de competición: Sprint 1 (PUBLIC core) en curso según D-192. Gate 0, Gate 1 y Gate 2 PASS; Gate 3 iniciado.
- Geografía canónica: 179 municipios, 246 distritos censales, 131 barrios, 4.417 secciones, 86.361 celdas H3.
- 21 datasets del Portal de Datos Abiertos de la Comunidad de Madrid con Quality Gate: geografía, población, hogares, vivienda, renta, alquiler, nacimientos, equipamientos (educación, centros sanitarios, mayores, farmacias) y los 6 GTFS del CRTM (14.982 paradas y estaciones con frecuencias).
- 12 features municipales con lineage y confidence; mapa con coropletas y capas de equipamientos en `/map`.
- API de la lista de lo que falta por zona (`GET /api/v1/gaps/{level}/{code}`): FALTA / JUSTO / CUBIERTO frente a la referencia regional, con confidence, proxy declarado y datasets de origen. Hoy tiene las filas de colegio y centro de salud por municipio.
- Contratos PUBLIC del buscador y de la lista, con sus JSON Schema en `data/schemas/api/` y sus rutas en `docs/04_technical_architecture/31_public_api_routes.md`.
- Red peatonal de OpenStreetMap (57.659 km) para medir la distancia a pie a los equipamientos: en curso (CORE-005).
- Base de datos de la demo en Supabase con RLS en todas las tablas (D-197).
- Progreso fase a fase: `board/BOARD.md` («Registro de progreso»). Evidencias en `evidence/`.

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
Según §6 de las bases, este repositorio identifica el trabajo realizado antes del 7 de noviembre de 2026 mediante el tag `pre-datamad` (commit `cf39459`, 22 oct 2026: Sprints P0 y P1). Todo lo posterior a ese tag se ha desarrollado durante la competición.

El repositorio se publicó el 11 nov con el historial reescrito para quitar datos de contacto de unos fixtures (D-198); las fechas de los commits no cambian. El repositorio original, archivado y privado, conserva los commits, PR y ejecuciones de CI de octubre con sus SHAs originales como prueba de fechas (antes el tag apuntaba a `08cc526`). La correspondencia entre SHAs antiguos y nuevos está en `evidence/gate-00/2026-11-11/commit-map.txt`.

## Licencia
Código bajo [Apache License 2.0](LICENSE). Documentación y metadatos del catálogo bajo [CC BY 4.0](docs/LICENSE). Los datos de terceros conservan su licencia original, registrada en `data/catalog/sources/`.
