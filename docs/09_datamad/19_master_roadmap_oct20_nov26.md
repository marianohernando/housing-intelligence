# Master Roadmap — 20 octubre → 26 noviembre 2026

## Filosofía
- Final-product-first.
- Claude Code ejecuta tareas cerradas desde documentación.
- Cada sprint termina con review + Quality Gate.
- La segunda mitad de cada sprint no puede convertirse en acumulación de deuda.
- El último tramo es para estabilidad, evidencia y pitch; no para rescatar arquitectura.

# FASE PRE-DATAMAD / PREPARACIÓN

## Sprint P0 — 20–25 octubre
### Nombre
**Control Tower + Data Recon**

### Objetivo
Que Claude Code pueda recibir el repositorio y empezar sin preguntas estructurales.

### Prioridad
P0 absoluta.

### Entregables
- inscripción confirmada o card para completarla;
- consulta a organización sobre pretrabajo previo;
- repo definitivo;
- `CLAUDE.md` validado;
- estructura monorepo;
- Docker Compose;
- Postgres/PostGIS/pgvector + Redis;
- CI mínima;
- Trello/board operativo;
- catálogo inicial de 100–200 datasets candidatos;
- scorecard y shortlist P0/P1;
- seleccionar primeros 30–50 objetivos;
- definir golden Madrid fixtures;
- definir golden user profiles;
- contratos de source/dataset/feature;
- revisar acceso a Comunidad Madrid, Catastro, CRTM, Ayuntamiento;
- identificar fuentes con permiso/restricción.

### Si pre-código está autorizado
Añadir:
- scaffolding real frontend/backend;
- source registry;
- primer ingestion skeleton;
- mapa base.

### Quality Gates
- Gate 0 PASS.
- Source reviews de P0 iniciadas.

### Review
25 octubre:
- ¿Claude arranca repo con un comando?
- ¿CI está verde?
- ¿sabemos exactamente qué fuentes entran primero?
- ¿hay algún blocker legal/técnico?

---

## Sprint P1 — 26 octubre–1 noviembre
### Nombre
**Madrid Data Foundation**

### Objetivo
Construir/definir la columna vertebral de datos.

### Entregables objetivo
- Bronze/Silver/Gold funcionando o totalmente preparado para ejecución oficial;
- 10–15 fuentes P0 integradas/preparadas;
- Catastro pipeline;
- CRTM/GTFS pipeline;
- boundaries + H3;
- geocoding/address resolution;
- primeros servicios: educación/salud/comercio;
- feature dictionary real;
- primeros 75–125 features;
- data coverage prototype;
- lineage;
- PostGIS canonical entities;
- QA geoespacial;
- source snapshots/checksums;
- mapa 2D con capas base si está permitido programar.

### Quality Gates
- Gate 1.
- Gate 2.
- inicio Gate 3.

### Review
1 noviembre:
- 0 == unknown nunca mezclado;
- mapas/geometrías válidos;
- cada dato P0 tiene lineage;
- ninguna fuente crítica depende de scraping prohibido.

---

## Sprint P2 — 2–6 noviembre
### Nombre
**Launch Pack + Competition Readiness**

### Objetivo
Llegar al 7 de noviembre con todo listo para acelerar.

### Fechas oficiales
5 nov:
- inscripción cerrada;
- formación APIs/MCP/Data Spaces 09:30–13:30.

6 nov:
- formación IA aplicada a datos abiertos 09:30–13:30.

### Entregables
- asistir/revisar ambas sesiones;
- incorporar cualquier criterio/insight oficial;
- 30–50 datasets priorizados;
- 150–250 features definidas;
- baseline matemático de:
  - affordability;
  - constraints;
  - Residential Fit;
  - Total Housing Cost;
  - Housing Gap;
- ScenarioState contract;
- frontend map-first specification final;
- design tokens/layout;
- prompts/contracts JEV/RAG;
- backlog completo listo para Claude;
- clean launch branch/tag.

### Si el predesarrollo está autorizado
Objetivo extra:
- PUBLIC shell usable;
- map + filters;
- baseline scoring.

### Quality Gates
- Gate 3 listo o casi listo.
- Gate 4 preparado con golden cases.

### Review / Launch decision
6 noviembre 18:00:
- backlog reordenado según formación;
- confirmar capabilities activadas;
- cero decisiones arquitectónicas pendientes para arrancar.

# FASE OFICIAL DE DESARROLLO

## Sprint 1 — 7–12 noviembre
### Nombre
**PUBLIC End-to-End**

### Objetivo
Un ciudadano puede usar el producto de principio a fin.

### Entregables
- mapa 3D/base visual SimCity estable;
- chat + chips + filtros;
- ScenarioState;
- Residential Fit baseline;
- affordability;
- anchors;
- routing/mobility;
- 15-minute living;
- accessibility core;
- explanations;
- confidence;
- Reality Check;
- saved scenario básico;
- source/provenance panel.

### Stretch
- HomeFit manual/address;
- PLUS entitlements skeleton.

### Gates
- Gate 4 PASS.
- Gate 5 PASS.
- Gate 6 PASS mínimo.
- Gate 7 PASS mínimo.

### Definition of sprint success
Hay una demo PUBLIC real sin mocks críticos.

### Review
12 noviembre noche.
Cortar features inestables antes de añadir nuevas.

---

## Sprint 2 — 13–18 noviembre
### Nombre
**Intelligence + PRO + MCP**

### Objetivo
Demostrar que el sistema no es solo un buscador ciudadano.

### Entregables
- Place Model / embeddings;
- similarity search;
- Housing Gap real;
- Demand/Supply Explorer;
- PRO workspace;
- parcel/project analysis;
- Product Recommender;
- price sensitivity baseline;
- JEV workflows reales;
- RAG de metodología/ayudas/docs;
- API;
- OpenAPI;
- >=10 MCP tools útiles;
- dynamic analysis layer si estable;
- source/evidence bundle.

### Gates
- Gate 8.
- Gate 9.
- Gate 10.
- Gate 11.

### Review
18 noviembre:
- ML debe superar baseline o queda desactivado;
- MCP debe aportar valor real, no postureo;
- PRO debe poder contar una historia comercial clara.

---

## Sprint 3 — 19–22 noviembre
### Nombre
**Wow Layer + Product Completion**

### Objetivo
Convertir un producto bueno en una demo difícil de olvidar.

### Entregables priorizados
- 3D polish;
- H3 extrusions;
- timeline histórico;
- Emerging Opportunity;
- scenario engine reducido;
- car dependency;
- accessibility visual modes;
- HomeFit URL/address si legal/estable;
- reports/export;
- alerts/feed skeleton;
- responsive/mobile;
- app WCAG;
- performance optimization;
- offline snapshot.

### Cut review
22 noviembre:
clasificar cada capability:
- GREEN: demo/release.
- YELLOW: mantener fuera de demo o detrás de flag.
- RED: desactivar.

### Gate
- Gate 12 debe estar muy cerca de PASS.

---

## Sprint 4 — 23–25 noviembre
### Nombre
**Freeze, Evidence, Pitch**

### Regla
No iniciar features grandes nuevas.

### 23 noviembre
- code feature freeze por la noche;
- fixes permitidos;
- cerrar Gate 12;
- datos/modelos freeze candidate;
- generar final source manifest.

### 24 noviembre
- demo rehearsal;
- 10-run smoke empieza;
- offline mode;
- security;
- backup/restore;
- open-source pack;
- README;
- screenshots;
- evidence matrix;
- pitch draft.

### 25 noviembre
- release candidate final;
- Gate 13;
- mínimo 10 demos consecutivas;
- pitch rehearsal;
- deck final;
- repo final;
- snapshot final;
- backup local;
- backup cloud si procede;
- NO risky migrations;
- NO nuevos modelos.

## 26 noviembre — FINAL
### Morning
Solo:
- smoke test;
- credenciales;
- portátil/cargador;
- offline pack;
- final demo reset.

### Presentation
Narrativa:
problema → persona → mapa → inteligencia → PRO → data/open-source → impacto.

# Ritmo interno por sprint

## Daily
Al final del día:
- Done
- Blocked
- Next
- Tests broken
- Gate status

## Mid-sprint review
No esperar al final para descubrir integración rota.

## Sprint review
- demo de lo construido;
- Quality Gate;
- bug triage;
- capability cut;
- siguiente sprint.

# Regla Claude Code
Claude no recibe “haz Sprint 2”.
Recibe cards pequeñas con:
- contexto;
- docs;
- archivos;
- acceptance criteria;
- tests;
- dependencies;
- gate;
- evidence.

# Regla de paralelización
Aunque el usuario sea una persona, Claude puede abrir workstreams separados:
1. DATA
2. BACKEND
3. FRONTEND/MAP
4. INTELLIGENCE
5. TEST/QA

Pero solo integrar cuando contracts estén cerrados.
