# Trello / Sprint Board Blueprint

## Lists

### 00 — INBOX
Ideas/no clasificadas.

### 01 — BACKLOG
Cards válidas pero sin sprint.

### 02 — READY THIS SPRINT
Definition of Ready completa.

### 03 — CLAUDE CODE
En implementación.

### 04 — REVIEW
Código/resultado preparado para revisar.

### 05 — TESTS / GATE
Implementado pero no terminado hasta pasar tests.

### 06 — BLOCKED
Con blocker explícito.

### 07 — DONE
Acceptance criteria + gate/evidence.

### 08 — CUT / LATER
Capabilities desactivadas por tiempo/riesgo.

## Labels
- DATA
- BACKEND
- FRONTEND
- MAP
- ML
- JEV
- RAG
- MCP
- PRO
- PUBLIC
- SECURITY
- QA
- DATAMAD
- TIER0
- TIER1
- TIER2
- BLOCKER

## Every card must include

### Outcome
Qué existe cuando se termina.

### Why
Qué capability/product/gate desbloquea.

### Source docs
Links/rutas exactas.

### Dependencies
Cards/contract/source.

### Acceptance criteria
Objetivos verificables.

### Tests
Nombres/comandos/casos.

### Quality Gate
G0–G13.

### Evidence
Ruta esperada bajo `evidence/`.

### Cut tier
Tier 0/1/2/3.

### Claude context
Files to read + no-go rules.

## Example

**Card:** DATA-014 — Ingest CRTM Metro/Bus GTFS

Outcome:
GTFS canonical tables + refreshable Bronze/Silver pipeline.

Acceptance:
- import succeeds;
- routes/stops/trips mapped;
- timezone correct;
- source/version metadata;
- sample routes validated.

Tests:
- schema;
- row count;
- stop coordinates Madrid bounds;
- referential integrity;
- golden route.

Gate:
G1/G2.

Evidence:
`evidence/gate-01/crtm-gtfs/`.
