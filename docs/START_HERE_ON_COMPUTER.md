# START HERE — Primer arranque en el ordenador

## Objetivo
Pasar de documentación cerrada a ejecución sin volver a replantear el producto.

# 0. Antes de programar
Hay un único blocker externo:
`DATAMAD-PREWORK-01`.

La web pública sitúa el desarrollo entre el 7 y el 26 de noviembre.
Antes de implementar la solución específica antes del día 7, confirmar con la organización qué pretrabajo/código previo permiten.

Mientras tanto, toda la preparación técnica y de datos puede avanzar.

# 1. Copiar la documentación al ordenador

Descomprimir este repositorio documental dentro del workspace del proyecto.

Conservar:
- `CLAUDE.md`
- `START_HERE_ON_COMPUTER.md`
- `00_index/`
- `09_datamad/`
- `11_engineering/`
- resto de documentación.

No reducir la documentación a un único prompt gigante.

# 2. Crear el repositorio real

Target conceptual:

```text
housing-intelligence/
  CLAUDE.md
  README.md
  apps/
    web/
    api/
  packages/
    domain/
    contracts/
    map-config/
    ui/
  services/
    ingestion/
    features/
    ml/
    routing/
    mcp/
  data/
    catalog/
    schemas/
    fixtures/
  infra/
    docker/
    migrations/
  tests/
  evidence/
  docs/
```

Mover/copiar la documentación a `docs/` manteniendo rutas coherentes si se decide separar docs del root.

`CLAUDE.md` debe permanecer visible en el root.

# 3. Primera orden a Claude Code

NO:
> Construye la aplicación.

SÍ:
> Lee `CLAUDE.md`, `START_HERE_ON_COMPUTER.md`, `00_index/00_master_index.md`, `09_datamad/19_master_roadmap_oct20_nov26.md`, `11_engineering/11_phase_quality_gates.md` y `11_engineering/25_claude_code_execution_protocol.md`.  
> Inspecciona el repositorio actual y prepara únicamente Sprint P0 / Gate 0. No implementes features de producto todavía. Genera un plan de cards técnicas y detecta cualquier conflicto entre documentación y entorno local.

# 4. Qué hacemos primero de verdad

## Primera prioridad: CONTROL TOWER
Antes de datos o UI:

1. repo;
2. estructura;
3. Docker;
4. Python/Node versions;
5. Postgres/PostGIS/pgvector;
6. Redis;
7. CI;
8. lint/typecheck/tests;
9. env/secrets;
10. `make dev`, `make test`, `make lint`;
11. evidence folder;
12. Trello/board.

Resultado:
Claude puede ejecutar cards sin improvisar infraestructura.

Quality Gate:
**G0 PASS.**

# 5. Segunda prioridad: PREPARAR LA INFORMACIÓN

Sí: después de G0, el primer trabajo sustantivo es **DATA**.

No empezamos diseñando el dashboard bonito.

## Orden
### A. Dataset discovery
Construir catálogo real de 100–200 fuentes candidatas.

### B. Scorecard
Clasificarlas:
- P0;
- P1;
- P2;
- research only.

### C. Elegir primeras 30–50
Con foco:
- Comunidad de Madrid;
- Catastro;
- CRTM;
- Ayuntamiento;
- INE/ministerios cuando completen.

### D. Primeras fuentes a atacar
Orden recomendado:

1. límites administrativos / geografía base;
2. población/hogares/demografía CM;
3. vivienda/superficie/mercado CM;
4. renta/affordability;
5. educación;
6. salud;
7. social/accessibility;
8. CRTM/GTFS;
9. Catastro;
10. comercios/actividades;
11. ambiente;
12. urbanismo/parcelas.

# 6. No descargar “todo” sin sistema

Cada fuente entra mediante:

`DISCOVER → REVIEW → FETCH → BRONZE → SCHEMA → SILVER → GEO → QUALITY → FEATURE`

No vale tener una carpeta con 80 CSVs sin saber:
- licencia;
- fecha;
- geometría;
- qué feature alimentan;
- cómo refrescarlos.

# 7. Paralelización correcta

Cuando los primeros contratos estén cerrados:

## Workstream DATA
fuentes, Bronze/Silver, PostGIS, H3.

## BACKEND
contratos, services, API.

## FRONTEND/MAP
shell, MapLibre/deck.gl, ScenarioState.

## INTELLIGENCE
features, baseline math, golden profiles.

## TEST/QA
tests/gates desde el primer commit.

Frontend puede avanzar con fixtures tipados, pero nunca inventando el contrato de datos por su cuenta.

# 8. Primer resultado visible que buscamos

No es “landing bonita”.

Es:

> Madrid en mapa + datos reales + una microzona seleccionable + lineage visible.

Después:

> perfil simple → Residential Fit baseline → explicación.

Así cada capa visual ya se apoya en arquitectura real.

# 9. Primer orden de cards

1. `ENG-001` Bootstrap monorepo.
2. `ENG-002` Docker services.
3. `ENG-003` CI + static checks.
4. `ENG-004` DB migrations + PostGIS/pgvector.
5. `QA-001` Gate 0 test harness.
6. `DATA-001` Source Registry.
7. `DATA-002` Dataset Scorecard.
8. `DATA-003` Madrid boundary canonical geography.
9. `DATA-004` H3 mapping.
10. `DATA-005` First Comunidad de Madrid dataset ingestion.
11. `DATA-006` Geospatial QA.
12. `MAP-001` Map shell using canonical geography.
13. `CORE-001` ScenarioState contracts.
14. `CORE-002` Golden user profiles.
15. `CORE-003` Residential Fit baseline test harness.

No hacer 15 simultáneamente.
Ejecutar por dependencias y Gate.

# 10. Qué NO hacer al principio

- no diseñar 40 pantallas;
- no entrenar ML sin features fiables;
- no montar microservicios;
- no scrapear Idealista primero;
- no meter LLM para cálculos;
- no intentar realtime;
- no trabajar sin tests;
- no crear datos falsos salvo fixtures explícitas;
- no marcar una card DONE antes del Gate.

# 11. Rutina diaria

Al empezar:
- revisar `READY THIS SPRINT`;
- revisar blockers;
- seleccionar 1–3 cards compatibles.

Al terminar:
- run tests;
- mover a TESTS/GATE;
- guardar evidence;
- actualizar Done/Blocked/Next.

# 12. Cuándo empezamos la UI espectacular

En cuanto tengamos:
- geografía;
- H3;
- 2–4 fuentes útiles;
- contratos estables.

No esperamos a tener 50 datasets.

Así el mapa crece a la vez que los datos, pero nunca por delante de ellos.

# 13. Condición para decir “ya estamos construyendo”

Se cumplen tres cosas:
1. Gate 0 PASS.
2. Source Registry existe.
3. Primer dataset real llega de Bronze a Silver con tests.

Desde ese momento, el proyecto ya está en construcción real.
